from typing import Iterator, List, Union

import lxml.etree as etree
import folium
import geojson

from perdido.utils.xml import Token
from perdido.utils.xml import get_tokens_from_tei, get_entities_from_tei, get_toponyms_from_tei, get_nested_entities_from_tei, get_toponyms_from_geojson, parent_exists
from perdido.utils.map import overlay_gpx, get_bounding_box

from spacy.tokens import Span
from spacy.tokens import Doc
from spacy.vocab import Vocab


class Perdido:


    def __init__(self) -> None:

        self.text = None
        self.tei = None
        self.geojson = None  # geojson.FeatureCollection?
        
        self.ne = []
        self.nne = [] # nested named entities or extended named entities? 
        self.tokens = []

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
            self.ne = get_entities_from_tei(root)
            self.toponyms = get_toponyms_from_tei(root) 
            self.nne = get_nested_entities_from_tei(root)


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


    def to_displacy(self) -> Doc:
        vocab = Vocab()
        
        words = [t.text for t in self.tokens]
        spaces = [True] * len(words)
        
        doc = Doc(vocab, words = words, spaces = spaces)
        ents = [] 

        for e in self.ne:
            if e.start is not None and e.end is not None:
                print(e.text, e.tag, e.start, e.end)
                ents.append(Span(doc, int(e.start), int(e.end), label=e.tag))

        doc.ents = ents
        return doc 



