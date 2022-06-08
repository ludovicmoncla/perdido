from typing import Iterator, List, Union

import lxml.etree as etree
import folium
import geojson

from perdido.utils.xml import Token
from perdido.utils.xml import get_tokens_from_tei, get_entities_from_tei, get_toponyms_from_tei, get_nested_entities_from_tei, get_toponyms_from_geojson
from perdido.utils.map import overlay_gpx, get_bounding_box


class Perdido:


    def __init__(self) -> None:

        self.text = None
        self.tei = None
        self.geojson = None  # geojson.FeatureCollection?
        
        self.ne = []
        self.nne = [] # nested named entities
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
           

    def get_folium_map(self, properties: Union[List[str], None] = None, gpx: Union[str , None] = None) -> Union[folium.Map,None]:
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



