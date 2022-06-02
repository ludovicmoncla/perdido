import requests
import json
import ast
import lxml.etree as etree


#TODO deplacer cette fonction dans utils/xx.py
#TODO retourner le tei et le geojson avec le service geoparsing
def getResult(jsonStr, field='result', outputFormat='json'):
    if json.loads(jsonStr.text)['status'] == "success":
        if outputFormat == 'html':
            return ast.literal_eval(json.dumps(json.loads(jsonStr.text)[field]))
        elif outputFormat == 'xml':
            return  etree.tostring(etree.XML(json.loads(jsonStr.text)[field]), pretty_print=True)
        else:
            return json.dumps(json.loads(jsonStr.text)[field])
    else:
        return None

#TODO faire une fonction qui génére le geojson à partir de la TEI


#TODO deplacer cette classe dans un nouveau fichier perdido.py
class Perdido:

    def __init__(self):

        self._txt = None
        self._tei = None  # type etree xml, string or both?
        self._geojson = None
        
        self._ne = []
        self._ene = []
        self._tokens = []

        # TODO ajouter le parsing xml pour récupérer les différents éléments :


class Geoparser:
    """
    Geoparser Class -- Provides geotagging and geocoding methods.

    """

    def __init__(self, language='French', version='Standard'):
        """
        Instanciate a geoparser
        TODO: Add the description...
        :param version: Standard (default) or Encyclopedie
        """
        self._urlAPI = 'http://choucas.univ-pau.fr/PERDIDO/api/'
        self._serviceGeoparsing = 'geoparsing'

        self._language = language
        self._apiKey = "libPython"
        self._version = version
        self._sources = {'ign' : False, 'osm' : True, 'geonames' : False, 'google' : False, 'wikiG' : False}


    def parse(self, content, sources = None):

        if sources is not None:
            self._sources = sources

        #TODO il manque les parametres optionnels
        parameters = {'api_key': self._apiKey, 'content': content}
        r = requests.post(self._urlAPI + self._serviceGeoparsing, params=parameters)
        
        res = Perdido()
        res._txt = content
        res._tei = getResult(r, 'xml-tei')
        res._geojson = getResult(r, 'geojson')

        #TODO ajouter l'appel à la méthode de Perdido qui va remplir les attributs 

        return res


 #TODO deplacer cette classe dans un nouveau fichier geocoder.py
class Geocoder:
    def __init__(self):
        pass

