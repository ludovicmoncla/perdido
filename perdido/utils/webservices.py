from typing import Any
import json
from lxml import etree
from io import StringIO
import requests


class WebService():

    def __init__(self, url_api: str = 'http://choucas.univ-pau.fr/PERDIDO/api/') -> None:
        self._url_api = url_api
        self._parameters = None
        self.result = None


    def post(self, service: str, params: dict[str, Any]) -> None:
        self._parameters = params
        self.result = requests.post(self._url_api + service, params=self._parameters)


    def get_result(self, field: str = 'result', output_format: str = 'json') -> str | None:
        if json.loads(self.result.text)['status'] == "success":
            if output_format == 'xml':
                parser = etree.XMLParser(ns_clean=True, remove_blank_text=True)
                return etree.tostring(etree.parse(StringIO(json.loads(self.result.text)[field]), parser), pretty_print=True, method="html").decode('utf-8')
                #return ast.literal_eval(json.dumps())
            #elif outputFormat == 'xml':
            #    return  etree.tostring(etree.XML(json.loads(jsonStr.text)[field]), pretty_print=True)
            else:
                return json.loads(json.loads(self.result.text)[field])
        else:
            return None

