from typing import Iterator, List, Dict, Union
from requests.exceptions import ConnectionError

import lxml.etree as etree
import folium
import geojson

from perdido.utils.disambiguation import clustering_disambiguation
from perdido.utils.webservices import WebService
from perdido.perdido import Perdido, PerdidoCollection

from pandas.core.series import Series


class Geoparser:


    def __init__(self, api_key: str = "libPython", lang: str = 'fr', version: str = 'Standard', sources: Union[List[str], None] = None, 
                max_rows: Union[int, None] = None, alt_names: Union[bool, None] = None, bbox: Union[List[float], None] = None, country_code: Union[str, None] = None, disambiguation: Union[str, None] = None) -> None:

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

        self.disambiguation = disambiguation


    def __call__(self, content: Union[str, List[str], Series]) -> Union[Perdido, PerdidoCollection, None]:
        return self.parse(content)


    def parse(self, content: Union[str, List[str], Series], geom = None) -> Union[Perdido, PerdidoCollection, None]:
        
        if type(content) == str:
            return self.call_perdido_ws(content, geom)
        elif type(content) == list or type(content) == Series:
            collection = PerdidoCollection()
            for c in content:
                collection.append(self.call_perdido_ws(c, geom))
            return collection
        else:
            return None

        
    def call_perdido_ws(self, content: str, geom = None) -> Perdido:
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
            res.geometry_layer = geom

            success, val = ws.get_result('xml-tei', 'xml')
            if success:
                res.tei = val

                success, val =  ws.get_result('geojson')
                if success:
                    res.geojson = val
            else:
                print(val)

            if self.disambiguation == 'cluster':
                res.geojson, res.geojson_ambiguous, res.best_cluster = clustering_disambiguation(res)

            res.parse_tei()

            return res
        except ConnectionError as e:
            print(e)
            return None


