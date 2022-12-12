from __future__ import annotations
from cgitb import text
from typing import Iterator, List, Union, Dict

import lxml.etree as etree
import folium
import geojson

from perdido.utils.utils import Token, Entity
from perdido.utils.utils import get_tokens_from_tei, get_entities_from_tei, get_toponyms_from_tei, get_nested_entities_from_tei, get_toponyms_from_geojson, parent_exists
from perdido.utils.map import overlay_gpx, get_bounding_box
from perdido.utils.disambiguation import clustering_disambiguation

from spacy.tokens import Span
from spacy.tokens import Doc
from spacy.vocab import Vocab
import json
import pickle

import pandas as pd
import geopandas as gpd


class Perdido:


    def __init__(self) -> None:

        self.text = None
        self.tei = None

        self.geojson = None 
        self.geojson_ambiguous = None 
        self.best_cluster = None

        self.geometry_layer = None # GPX track
        
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
        #tree = etree.ElementTree(etree.fromstring(self.tei))
        #tree.write(path)
        with open(path, 'w') as f:
            f.write(self.tei)


    def to_geojson(self, path: str) -> None:
        with open(path, 'w') as f:
            geojson.dump(self.geojson, f)


    def to_csv(self, path: str, sep: str = ',') -> None:
        df = self.to_dataframe()
        df.to_csv(path, sep=sep)


    def to_iob(self, path: str, sep: str = '\t') -> None:
        content = ''
        for token in self:
            if sep == '\t':
                content += token.tsv_format() + '\n'
            elif sep == ' ':
                content += token.iob_format() + '\n'

        with open(path, 'w') as f:
            f.write(content)


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
           

    # ajouter un param pour tenir compte du best cluster
    def get_folium_map(self, properties: Union[List[str], None] = ['name', 'source'], gpx: Union[str , None] = None) -> Union[folium.Map,None]:
        m = folium.Map()
        if gpx is not None:
            overlay_gpx(m, gpx)

        if self.geometry_layer is not None:
            folium.GeoJson(data=gpd.GeoSeries(self.geometry_layer).to_json()).add_to(m)


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
            
            if len(e.toponym_candidates) > 0:
                lat = e.toponym_candidates[0].lat
                lng = e.toponym_candidates[0].lng 
                toponym_candidates = [t.to_dict() for t in e.toponym_candidates]
            else:
                lat = None
                lng = None
                toponym_candidates = None

            data.append([name, tag, lat, lng, toponym_candidates])

        return pd.DataFrame(data, columns=['name', 'tag', 'lat', 'lng', 'toponym_candidates'])


    def to_geodataframe(self) -> None:
        return gpd.GeoDataFrame.from_features(self.geojson['features'])


    def cluster_disambiguation(self, e: float = 0.1) -> None:
        self.geojson, self.geojson_ambiguous, self.best_cluster = clustering_disambiguation(self, e)



class PerdidoCollection:

    def __init__(self, data: List[Perdido] = [], metadata: List[Dict] = []) -> None:
        self.data = data
        self.metadata = metadata


    def __len__(self) -> int:
        return len(self.data)


    def __getitem__(self, index: int) -> Perdido:
        return self.data[index]
    

    def __iter__(self) -> Iterator[Perdido]:
        for d in self.data:
            yield d


    def append(self, item: Perdido) -> None:
        if type(item) == Perdido:
            self.data.append(item)


    def extend(self, collection: PerdidoCollection) -> None:
        self.data.extend(collection.data)
        self.metadata.extend(collection.metadata)


    def to_dataframe(self) -> pd.DataFrame :

        #TODO add some columns such as number of entity of each type.
        df = pd.DataFrame(self.metadata)
        df['text'] = [doc.text for doc in self.data]
        df['#_places'] = [len(doc.ne_place) for doc in self.data]
        df['#_person'] = [len(doc.ne_person) for doc in self.data]
        df['#_event'] = [len(doc.ne_event) for doc in self.data]
        df['#_date'] = [len(doc.ne_date) for doc in self.data]
        df['#_misc'] = [len(doc.ne_misc) for doc in self.data]
        df['#_locations'] = [len(doc.toponyms) for doc in self.data]
        return df


    def to_geojson(self):
        pass


    #TODO find a better name?
    def within_area(self, bbox:List[float]) -> PerdidoCollection:
        #get the documents with places located within a bounding box
        pass


    # filter on metadata
    def keyword_search(self, keyword: str) -> PerdidoCollection:   
        data = [doc for doc in self.data if keyword in doc.text]
        metadata = [self.metadata[key]  for key, doc in enumerate(self.data) if keyword in doc.text]
        return PerdidoCollection(data, metadata)


    # filter on metadata
    def filter_equal(self, column: str, value: str) -> PerdidoCollection:
        data = [self[k] for k, d in enumerate(self.metadata) if d[column] == value]
        metadata = [d for d in self.metadata if d[column] == value]
        return PerdidoCollection(data, metadata)


    # filter on metadata
    # TODO: catch KeyError exception
    def filter_gt(self, column: str, value: int) -> PerdidoCollection:
        if column in ['#_locations', '#_places', '#_person', '#_date', '#_event', '#_misc']:
            if column == '#_locations':
                data = [d for d in self.data if len(d.toponyms) > value]
                metadata = [self.metadata[k] for k, d in enumerate(self.data) if len(d.toponyms) > value]
            if column == '#_places':
                data = [d for d in self.data if len(d.ne_place) > value]
                metadata = [self.metadata[k] for k, d in enumerate(self.data) if len(d.ne_place) > value]
            if column == '#_person':
                data = [d for d in self.data if len(d.ne_person) > value]
                metadata = [self.metadata[k] for k, d in enumerate(self.data) if len(d.ne_person) > value]
            if column == '#_event':
                data = [d for d in self.data if len(d.ne_event) > value]
                metadata = [self.metadata[k] for k, d in enumerate(self.data) if len(d.ne_event) > value]
            if column == '#_date':
                data = [d for d in self.data if len(d.ne_date) > value]
                metadata = [self.metadata[k] for k, d in enumerate(self.data) if len(d.ne_date) > value]
            if column == '#_misc':
                data = [d for d in self.data if len(d.ne_misc) > value]
                metadata = [self.metadata[k] for k, d in enumerate(self.data) if len(d.ne_misc) > value]
        else:
            data = [self[k] for k, d in enumerate(self.metadata) if d[column] > value]
            metadata = [d for d in self.metadata if d[column] > value]
        return PerdidoCollection(data, metadata)


    # filter on metadata
    def filter_lt(self, column: str, value: int) -> PerdidoCollection:
        if column in ['#_locations', '#_places', '#_person', '#_date', '#_event', '#_misc']:
            if column == '#_locations':
                data = [d for d in self.data if len(d.toponyms) > value]
                metadata = [self.metadata[k] for k, d in enumerate(self.data) if len(d.toponyms) < value]
            if column == '#_places':
                data = [d for d in self.data if len(d.ne_place) < value]
                metadata = [self.metadata[k] for k, d in enumerate(self.data) if len(d.ne_place) < value]
            if column == '#_person':
                data = [d for d in self.data if len(d.ne_person) < value]
                metadata = [self.metadata[k] for k, d in enumerate(self.data) if len(d.ne_person) < value]
            if column == '#_event':
                data = [d for d in self.data if len(d.ne_event) < value]
                metadata = [self.metadata[k] for k, d in enumerate(self.data) if len(d.ne_event) < value]
            if column == '#_date':
                data = [d for d in self.data if len(d.ne_date) < value]
                metadata = [self.metadata[k] for k, d in enumerate(self.data) if len(d.ne_date) < value]
            if column == '#_misc':
                data = [d for d in self.data if len(d.ne_misc) < value]
                metadata = [self.metadata[k] for k, d in enumerate(self.data) if len(d.ne_misc) < value]
        else:
            data = [self[k] for k, d in enumerate(self.metadata) if d[column] < value]
            metadata = [d for d in self.metadata if d[column] < value]
        return PerdidoCollection(data, metadata)
    
    
    # filter on metadata
    def filter_in(self, column: str, values: List[str]) -> PerdidoCollection:
        data = [self[k] for k, d in enumerate(self.metadata) if d[column] in values]
        metadata = [d for d in self.metadata if d[column] in values]
        return PerdidoCollection(data, metadata)


    def get_folium_map(self, properties: Union[List[str], None] = ['name', 'source'], gpx: Union[str , None] = None) -> Union[folium.Map,str]:
        m = folium.Map()
        if gpx is not None:
            overlay_gpx(m, gpx)
        res = False
        for doc in self.data:
            if doc.geojson is not None:
                if type(doc.geojson) == str:
                    doc.geojson = json.loads(doc.geojson)
                if len(doc.geojson["features"]) > 0:
                    coords = list(geojson.utils.coords(doc.geojson))
                    if len(coords) > 0:
                        m.fit_bounds(get_bounding_box(coords))
                        if properties is not None:
                            folium.GeoJson(doc.geojson, name='Toponyms', tooltip=folium.features.GeoJsonTooltip(fields=properties, localize=True)).add_to(m)
                        else:
                            folium.GeoJson(doc.geojson, name='Toponyms').add_to(m)
                        res = True
        if res:                
            return m
        return 'No location found!'


    def dump(self, filepath: str) -> None:
        # .pickle
        dump = open(filepath, "wb")
        pickle.dump(self, dump)
        dump.close()


    def load(self, filepath: str) -> None:
        # .pickle
        dump = open(filepath, "rb")
        collection = pickle.load(dump)
        self.data = collection.data
        self.metadata = collection.metadata
        dump.close()