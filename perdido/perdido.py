from cgitb import text
from typing import Iterator, List, Union

import lxml.etree as etree
import folium
import geojson

from perdido.utils.xml import Token, Entity
from perdido.utils.xml import get_tokens_from_tei, get_entities_from_tei, get_toponyms_from_tei, get_nested_entities_from_tei, get_toponyms_from_geojson, parent_exists
from perdido.utils.map import overlay_gpx, get_bounding_box

from spacy.tokens import Span
from spacy.tokens import Doc
from spacy.vocab import Vocab
import spacy

import pandas as pd


class Perdido:


    def __init__(self) -> None:

        self.text = None
        self.tei = None
        self.geojson = None 
        
        self.tokens = []

        self.entities = [] # TODO
        
        self.named_entities = []
        self.nested_named_entities = [] 
        self.nominal_entities = []
        
        self.toponyms = []


    def __iter__(self) -> Iterator[Token]:
        for t in self.tokens:
            yield t


    def __len__(self) -> int:
        return len(self.tokens)


    def parse_tei(self) -> None:
        if self.tei is not None:
            root = etree.fromstring(self.tei)
            
            self.tokens = get_tokens_from_tei(root)
            self.named_entities = get_entities_from_tei(root)
            self.toponyms = get_toponyms_from_tei(root) 
            self.nested_named_entities = get_nested_entities_from_tei(root)


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
            
            if len(e.toponyms) > 0:
                lat = e.toponyms[0].lat
                lng = e.toponyms[0].lng 
                toponym_candidates = [t.to_dict() for t in e.toponyms]
            else:
                lat = None
                lng = None
                toponym_candidates = None

            data.append([name, tag, lat, lng, toponym_candidates])

        return pd.DataFrame(data, columns=['name', 'tag', 'lat', 'lng', 'toponym_candidates'])

