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


class Entity:
    def __init__(self, text, tokens, tag, parent=None, child=None, level=0):

        self.text = text
        self.tokens = tokens
        self.tag = tag
    
        self.parent = parent
        self.child = child

        self.level = level # find a better name?
        #...


class Toponym: 
    def __init__(self, name, ):

        self.name = name
        


class Token:
    def __init__(self, text, lemma=None, pos=None):

        self.text = text
        self.lemma = lemma
        self.pos = pos
        



#TODO deplacer cette classe dans un nouveau fichier perdido.py
class Perdido:

    def __init__(self):

        self.text = None
        self.tei = None  # type etree xml, string or both?
        self.geojson = None
        
        self.ne = []
        self.ene = []
        self.tokens = []

        self.toponyms = []

        # TODO ajouter le parsing xml pour récupérer les différents éléments :


    def parseTEI(self):
        root = etree.fromstring(self.tei)
        for w in root.findall('.//w'):
            lemma = w.get('lemma') if 'lemma' in w.attrib else  ""
            pos = w.get('type') if 'type' in w.attrib else  ""
            self.tokens.append(Token(w.text, lemma, pos))

        
        for rs in root.findall('.//name'):

            #self.ne.append(Token(rs.text, lemma, pos))
            pass        

    #TODO ajouter une méthode qui retourne le contenu txt d'une balise tei (boucle sur les balises w)
    
    #TODO ajouter les méthodes de display


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
        res.txt = content
        res.tei = getResult(r, 'xml-tei', 'xml')
        res.geojson = getResult(r, 'geojson')

        #TODO ajouter l'appel à la méthode de Perdido qui va remplir les attributs 
        res.parseTEI()

        return res


 #TODO deplacer cette classe dans un nouveau fichier geocoder.py
class Geocoder:
    def __init__(self):
        pass

