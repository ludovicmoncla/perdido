from typing import Iterator, List, Dict, Union
from requests.exceptions import ConnectionError

import lxml.etree as etree
import folium
import geojson

from perdido.utils.webservices import WebService
from perdido.perdido import Perdido

from pandas.core.series import Series


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


    def __call__(self, content: Union[str, List[str], Series]) -> Union[Perdido, List[Perdido], Series, None]:
        return self.parse(content)


    def parse(self, content: Union[str, List[str], Series]) -> Union[Perdido, List[Perdido], Series, None]:
        
        if type(content) == str:
            return self.call_perdido_ws(content)
        elif type(content) == list or type(content) == Series:
            l = []
            for c in content:
                l.append(self.call_perdido_ws(c))
            if type(content) == Series:
                return Series(l)
            else:
                return l
        else:
            return None

        
    def call_perdido_ws(self, content: str) -> Perdido:
        try:
            ws = WebService()

            parameters = {'api_key': self.api_key, 
                    #'content': content, 
                    'lang': self.lang, 
                    'version': self.version, 
                    'max_rows': self.max_rows, 
                    'alt_names': self.alt_names,
                    'sources': self.sources}
            
            if self.bbox is not None:
                parameters['bbox'] = self.bbox
    
            if self.country_code is not None:
                parameters['country_code'] = self.country_code

            data = {'content': content}

            ws.post(self.serviceGeoparsing, params=parameters, data=data)

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
        except ConnectionError as e:
            print(e)
            return None