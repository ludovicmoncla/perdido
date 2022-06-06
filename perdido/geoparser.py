from typing import Iterator, List, Dict

import lxml.etree as etree
import folium
import geojson

from perdido.utils.webservices import WebService
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
        

    def get_folium_map(self, properties: list[str] | None = None, gpx: str | None = None) -> folium.Map | None:
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


class Geoparser:


    def __init__(self, api_key: str = "libPython", lang: str = 'fr', version: str = 'Standard', sources: Dict[str, bool] | None = None, 
                max_rows: int | None = None, alt_names: bool | None = None, bbox: List[float] | None = None, country_code: str | None = None) -> None:

        self.url_api = 'http://choucas.univ-pau.fr/PERDIDO/api/'
        self.serviceGeoparsing = 'geoparsing'

        self.lang = lang
        self.api_key = api_key
        self.version = version

        if sources is not None:
            self.sources = sources
        else:
            self.sources = {'nominatim' : True}
            
        self.max_rows = max_rows
        self.alt_names = alt_names

        self.country_code = country_code

        if bbox is not None and len(bbox) == 4:
            self.bbox = {'west' : bbox[0], 'south' : bbox[1], 'east' : bbox[2], 'north' : bbox[3]}
        else:
            self.bbox = None


    def __call__(self, content: str) -> Perdido: 
        return self.parse(content)


    def parse(self, content: str) -> Perdido:

        ws = WebService()

        parameters = {'api_key': self.api_key, 'content': content, 'lang': self.lang, 'version': self.version, 'max_rows': self.max_rows, 'alt_names': self.alt_names}
        parameters.update(self.sources)
        if self.bbox is not None:
            parameters.update(self.bbox)
        print(self.country_code)

        if self.country_code is not None:
            parameters['country_code'] = self.country_code

        ws.post(self.serviceGeoparsing, params=parameters)

        res = Perdido()
        res.text = content

        success, val = ws.get_result('xml-tei', 'xml')
        if success:
            res.tei = val

            success, val =  ws.get_result('geojson')
            if success:
                res.geojson = val
        else:
            print(val)
            

        res.parse_tei()

        return res

