import json
import lxml.etree as etree
from io import StringIO
import requests

class WebService():

    def __init__(self, urlAPI = 'http://choucas.univ-pau.fr/PERDIDO/api/'):
        self._urlAPI = urlAPI
        self._parameters = None
        self.result = None


    def post(self, service, params):
        self._parameters = params
        self.result = requests.post(self._urlAPI + service, params=self._parameters)


    def getResult(self, field='result', outputFormat='json'):
        if json.loads(self.result.text)['status'] == "success":
            if outputFormat == 'xml':
                parser = etree.XMLParser(ns_clean=True, remove_blank_text=True)
                return etree.tostring(etree.parse(StringIO(json.loads(self.result.text)[field]), parser), pretty_print=True, method="html").decode('utf-8')
                #return ast.literal_eval(json.dumps())
            #elif outputFormat == 'xml':
            #    return  etree.tostring(etree.XML(json.loads(jsonStr.text)[field]), pretty_print=True)
            else:
                return json.loads(json.loads(self.result.text)[field])
        else:
            return None

