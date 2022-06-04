import lxml.etree as etree
import folium
import geojson
from perdido.utils.webservices import WebService
from perdido.utils.xml import *
from perdido.utils.map import *


class Geoparser:
    """
    Geoparser Class -- Provides geotagging and geocoding methods.

    """

    def __init__(self, apiKey = "libPython", language='French', version='Standard', sources = None):
        """
        Instanciate a geoparser
        TODO: Add the description...
        :param version: Standard (default) or Encyclopedie
        """
        self._urlAPI = 'http://choucas.univ-pau.fr/PERDIDO/api/'
        self._serviceGeoparsing = 'geoparsing'

        self._language = language
        self._apiKey = apiKey
        self._version = version
        if sources is not None:
            self._sources = {'ign' : False, 'osm' : True, 'geonames' : False, 'google' : False, 'wikiG' : False}


    def __call__(self, content):
        return self.parse(content)


    def parse(self, content):

        ws = WebService()

        #TODO il manque les parametres optionnels: sources, bbox...
        parameters = {'api_key': self._apiKey, 'content': content, 'version': self._version}
        ws.post(self._serviceGeoparsing, params=parameters)

        res = Perdido()
        res.text = content

        res.tei = ws.getResult('xml-tei', 'xml')
        res.geojson = ws.getResult('geojson')

        #TODO ajouter l'appel à la méthode de Perdido qui va remplir les attributs 
        res.parseTEI()

        return res




class Perdido:

    def __init__(self):

        self.text = None
        self.tei = None  # type etree xml, string or both?
        self.geojson = None
        
        self.ne = []
        self.nne = [] # nested named entities
        self.tokens = []

        self.toponyms = []


    def __iter__(self):
        for t in self.tokens:
            yield t


    def __len__(self):
        return len(self.tokens)


    def parseTEI(self):
        root = etree.fromstring(self.tei)
        
        self.tokens = get_tokens(root)
        self.ne = get_entities(root)
        self.toponyms = get_toponyms(root)
        self.nne = get_nested_entities(root)
        

    def get_folium_map(self, properties=None, gpx=None):
        m = folium.Map()
        if gpx is not None:
            overlayGPX(m, gpx)

        coords = list(geojson.utils.coords(self.geojson))
        if len(coords) > 0:
            #print(str(len(coords))+" records found in gazetteer:")

            m.fit_bounds(get_bounding_box(coords))
            #folium.GeoJson(json_data, name='Toponyms', tooltip=folium.features.GeoJsonTooltip(fields=['id', 'name', 'source'], localize=True)).add_to(m)
            if properties is not None:
                folium.GeoJson(self.geojson, name='Toponyms', tooltip=folium.features.GeoJsonTooltip(fields=properties, localize=True)).add_to(m)
            else:
                folium.GeoJson(self.geojson, name='Toponyms').add_to(m)
            return m
        else:
            #print("Sorry, no records found in gazetteer for geocoding!")
            return None

    #TODO ajouter les méthodes de display
