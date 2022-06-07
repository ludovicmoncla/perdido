from typing import Iterator, List, Dict, Union

import lxml.etree as etree
import folium
import geojson

from perdido.utils.webservices import WebService
from perdido.perdido import Perdido

class Geoparser:


    def __init__(self, api_key: str = "libPython", lang: str = 'fr', version: str = 'Standard', sources: Union[List[str], None] = None, 
                max_rows: Union[int, None] = None, alt_names: Union[bool, None] = None, bbox: Union[List[float], None] = None, country_code: Union[str, None] = None) -> None:

        self.url_api = 'http://choucas.univ-pau.fr/PERDIDO/api/'
        self.serviceGeoparsing = 'geoparsing'

        self.lang = lang
        self.api_key = api_key
        self.version = version

        if sources is not None:
            self.sources = sources
        else:
            self.sources = ['nominatim']
            
        self.max_rows = max_rows
        self.alt_names = alt_names

        self.country_code = country_code

        if bbox is not None and len(bbox) == 4:
            self.bbox = bbox
        else:
            self.bbox = None


    def __call__(self, content: str) -> Perdido: 
        return self.parse(content)


    def parse(self, content: str) -> Perdido:

        ws = WebService()

        parameters = {'api_key': self.api_key, 
                'content': content, 
                'lang': self.lang, 
                'version': self.version, 
                'max_rows': self.max_rows, 
                'alt_names': self.alt_names,
                'sources': self.sources}
        
        if self.bbox is not None:
            parameters['bbox'] = self.bbox
   
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

