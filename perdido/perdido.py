from typing import Iterator, List, Union

import lxml.etree as etree
import folium
import geojson

from perdido.utils.xml import Token
from perdido.utils.xml import get_tokens, get_entities, get_toponyms, get_nested_entities
from perdido.utils.map import overlay_gpx, get_bounding_box


class Perdido:


    def __init__(self) -> None:

        self.text = None
        self.tei = None
        self.geojson = None
        
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
            
            self.tokens = get_tokens(root)
            self.ne = get_entities(root)
            self.toponyms = get_toponyms(root)
            self.nne = get_nested_entities(root)
        

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



