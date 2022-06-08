from typing import Iterator, List, Dict, Union
from perdido.utils.webservices import WebService
from perdido.perdido import Perdido


class Geocoder:
    
    def __init__(self, api_key: str = "libPython", sources: Union[List[str], None] = None, max_rows: Union[int, None] = None, 
                alt_names: Union[bool, None] = None, bbox: Union[List[float], None] = None, country_code: Union[str, None] = None) -> None:
        
        self.url_api = 'http://choucas.univ-pau.fr/PERDIDO/api/'
        self.serviceGeocoding = 'geocoding'

        self.api_key = api_key

        if sources is not None:
            self.sources = sources
        else:
            self.sources = {'nominatim' : True}
            
        self.max_rows = max_rows
        self.alt_names = alt_names

        self.country_code = country_code

        if bbox is not None and len(bbox) == 4:
            self.bbox = bbox
        else:
            self.bbox = None


    def __call__(self, toponyms: Union[str, List[str]]) -> Perdido: 
        return self.geocode(toponyms)

    
    def geocode(self, toponyms: Union[str, List[str]]) -> Perdido:

        if type(toponyms) == str:
            toponyms = [toponyms]
       
        ws = WebService()

        parameters = {'api_key': self.api_key, 
                'toponyms': toponyms, 
                'max_rows': self.max_rows, 
                'alt_names': self.alt_names,
                'sources': self.sources}

        if self.bbox is not None:
            parameters['bbox'] = self.bbox
   
        if self.country_code is not None:
            parameters['country_code'] = self.country_code

        ws.post(self.serviceGeocoding, params=parameters)

        res = Perdido()
        res.text = ', '.join(toponyms)

        success, val = ws.get_result('geojson')
        if success:
            res.geojson = val
        else:
            print(val)

        # TODO:    res.toponyms
        res.parse_geojson()

        return res
