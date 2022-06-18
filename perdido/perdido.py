from cgitb import text
from typing import Iterator, List, Union, Dict
from __future__ import annotations

import lxml.etree as etree
import folium
import geojson

from perdido.utils.utils import Token, Entity
from perdido.utils.utils import get_tokens_from_tei, get_entities_from_tei, get_toponyms_from_tei, get_nested_entities_from_tei, get_toponyms_from_geojson, parent_exists
from perdido.utils.map import overlay_gpx, get_bounding_box

from spacy.tokens import Span
from spacy.tokens import Doc
from spacy.vocab import Vocab
import spacy
import pickle

import pandas as pd


class Perdido:


    def __init__(self) -> None:

        self.text = None
        self.tei = None
        self.geojson = None 
        
        self.tokens = []

        self.entities = [] # TODO

        self.named_entities = []
        self.ne_place = []
        self.ne_person = []
        self.ne_date = []
        self.ne_event = []
        self.ne_misc = []

        self.nested_named_entities = [] 
        self.nominal_entities = []
        
        self.toponyms = []


    def __iter__(self) -> Iterator[Token]:
        for t in self.tokens:
            yield t


    def __len__(self) -> int:
        return len(self.tokens)


    def to_xml(self, path: str) -> None:
        tree = etree.ElementTree(etree.fromstring(self.tei))
        tree.write(path)


    def to_geojson(self, path: str) -> None:
        with open(path, 'w') as f:
            geojson.dump(self.geojson, f)


    def to_csv(self, path: str, sep: str = ',') -> None:
        df = self.to_dataframe()
        df.to_csv(path, sep=sep)


    def parse_tei(self) -> None:
        if self.tei is not None:
            root = etree.fromstring(self.tei)
            
            self.tokens = get_tokens_from_tei(root)
            self.named_entities = get_entities_from_tei(root)
            self.toponyms = get_toponyms_from_tei(root) 
            self.nested_named_entities = get_nested_entities_from_tei(root)

            self.ne_place = get_entities_from_tei(root, 'place')
            self.ne_person = get_entities_from_tei(root, 'person')
            self.ne_date = get_entities_from_tei(root, 'date')
            self.ne_event = get_entities_from_tei(root, 'event')
            self.ne_misc = get_entities_from_tei(root, 'other')

            #self.nominal_entities = []
            #self.entities = []

    def parse_geojson(self) -> None:
        if self.geojson is not None:
           
            self.toponyms = get_toponyms_from_geojson(self.geojson)  
           

    def get_folium_map(self, properties: Union[List[str], None] = ['name', 'source'], gpx: Union[str , None] = None) -> Union[folium.Map,None]:
        m = folium.Map()
        if gpx is not None:
            overlay_gpx(m, gpx)

        if self.geojson is not None:
            coords = list(geojson.utils.coords(self.geojson))
            if len(coords) > 0:
                m.fit_bounds(get_bounding_box(coords))
                if properties is not None:
                    folium.GeoJson(self.geojson, name='Toponyms', tooltip=folium.features.GeoJsonTooltip(fields=properties, localize=True)).add_to(m)
                else:
                    folium.GeoJson(self.geojson, name='Toponyms').add_to(m)
                return m    
        return None



    def to_spacy_spans(self, entities: List[Entity], doc: Doc) -> List[Span]:
        spans = []
        for e in entities:
            if e.start is not None and e.end is not None:
                #print(e.text, e.tag, e.start, e.end)
                if e.tag == 'place':
                    tag = 'LOC'
                elif e.tag == 'person':
                    tag = 'PERSON'
                #elif e.tag == 'person':
                #    tag = 'NORP'
                elif e.tag == 'date':
                    tag = 'DATE'
                elif e.tag == 'event':
                    tag = 'EVENT'
                else:
                    tag = 'MISC'

                spans.append(Span(doc, int(e.start), int(e.end), tag))
        return spans


    def to_spacy_doc(self) -> Doc:
        
        vocab = Vocab()
        words = [t.text for t in self.tokens]
        spaces = [True] * len(words)
        doc = Doc(vocab, words = words, spaces = spaces)

        #spacy_parser = spacy.blank("fr")
        #doc = spacy_parser(self.text)
  
        doc.ents = self.to_spacy_spans(self.named_entities, doc)
        doc.spans["sc"] = self.to_spacy_spans(self.nested_named_entities + self.named_entities, doc)

        return doc


    def to_dataframe(self) -> pd.DataFrame:

        data = []
        for e in self.named_entities:

            name = e.text
            tag = e.tag
            
            if len(e.toponyms_candidate) > 0:
                lat = e.toponyms_candidate[0].lat
                lng = e.toponyms_candidate[0].lng 
                toponym_candidates = [t.to_dict() for t in e.toponyms_candidate]
            else:
                lat = None
                lng = None
                toponym_candidates = None

            data.append([name, tag, lat, lng, toponym_candidates])

        return pd.DataFrame(data, columns=['name', 'tag', 'lat', 'lng', 'toponym_candidates'])


class PerdidoCollection:

    def __init__(self, data: List[Perdido] = [], metadata: List[Dict] = []) -> None:
        self.data = data
        self.metadata = metadata


    def __len__(self) -> int:
        return len(self.data)


    def __getitem__(self, index: int) -> Perdido:
        return self.data[index]


    def __iter__(self) -> Iterator[Token]:
        for t in self.tokens:
            yield t


    def __iter__(self):
        self.index = 0
        return self
 

    def __next__(self) -> Perdido:
        if self.index < len(self.data):
            d = self.data[self.index]
            self.index += 1
            return d
        raise StopIteration


    def append(self, item: Perdido) -> None:
        if type(item) == Perdido:
            self.data.append(item)


    def extend(self, items: List[Perdido]) -> None:
        self.data.extend(items)


    #TODO find a better name?
    def contains(self, tags: Union[str, List[str]]) -> PerdidoCollection:
        collection = PerdidoCollection()

        for doc in self.data:
            
            if type(tags) == str:
                if tags == 'place':
                    collection.extend(doc.ne_place)
                elif tags == 'person':
                    collection.extend(doc.ne_person)
                elif tags == 'event':
                    collection.extend(doc.ne_event)
                elif tags == 'misc' or tags == 'other':
                    collection.extend(doc.ne_misc)
                else:
                    pass
            elif type(tags) == list:
                pass

        return collection


    #TODO find a better name?
    def within_area(self, bbox:List[float]) -> PerdidoCollection:
        #get the documents with places located within a bounding box
        pass


    # filter on metadata
    def filter(self) -> PerdidoCollection:
        pass


    def dump(self, filepath: str) -> None:
        # .pickle
        dump = open(filepath, "wb")
        pickle.dump(self, dump)
        dump.close()


    def load(self, filepath: str) -> None:
        # .pickle
        dump = open(filepath, "wb")
        collection = pickle.load(self, dump)
        self.data = collection.data
        self.metadata = collection.metadata
        dump.close()