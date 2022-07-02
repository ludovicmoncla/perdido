from typing import Any, Dict, Tuple, Union
import json
from lxml import etree
from io import StringIO
import requests


class WebService():

    def __init__(self, url_api: str = 'http://choucas.univ-pau.fr/PERDIDO/api/') -> None:
        self._url_api = url_api
        self._parameters = None
        self._data = None
        self.result = None


    def post(self, service: str, params: Dict[str, Any], data : Union[Dict[str, Any], None] = None) -> None:
        self._parameters = params
        if data is not None:
            self._data = data
            self.result = requests.post(self._url_api + service, params=self._parameters, json=self._data)
        else:
            self.result = requests.post(self._url_api + service, params=self._parameters)


    def get_result(self, field: str = 'result', output_format: str = 'json') -> Union[Tuple[bool, str], None]:
        
        try :
            if json.loads(self.result.text)['status'] == "success":
                if output_format == 'xml':
                    parser = etree.XMLParser(ns_clean=True, remove_blank_text=True)
                    #return True, etree.tostring(etree.parse(StringIO(json.loads(self.result.text)[field]), parser), pretty_print=True, method="html").decode('utf-8')
                    return True, etree.tostring(etree.parse(StringIO(json.loads(self.result.text)[field]), parser), encoding='unicode')
                    #return ast.literal_eval(json.dumps())
                #elif outputFormat == 'xml':
                #    return  etree.tostring(etree.XML(json.loads(jsonStr.text)[field]), pretty_print=True)
                else:
                    return True, json.loads(json.loads(self.result.text)[field])
            elif json.loads(self.result.text)['status'] == "failure":
                return False, json.loads(self.result.text)['message']
            else:
                return False, 'Oops! An error occured.'
        except json.decoder.JSONDecodeError:
            return False, 'Oops! An error occured: '+ self.result.text
