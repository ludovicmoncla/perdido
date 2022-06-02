import requests
import json
import ast
import lxml.etree as etree


#TODO deplacer cette fonction dans utils/xx.py
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


#TODO deplacer cette fonction dans utils/xx.py 
def get_w_content(element):
    content = ""
    for w in element.findall('.//w'):
        content += w.text + " "
    return content.strip()



def parent_exists(elt, parent_name):
    try:
        parent_node = next(elt.iterancestors())
        if parent_name is not None:
            if parent_node.tag == parent_name:
                if 'start' in parent_node.attrib:
                    return True
        return parent_exists(parent_node, parent_name)
    except StopIteration:
        return False



#TODO deplacer cette fonction dans utils/xx.py 
def get_tokens(elt):
    tokens = []
    for elt in elt.findall('.//w'):
        lemma = elt.get('lemma') if 'lemma' in elt.attrib else  ""
        pos = elt.get('type') if 'type' in elt.attrib else  ""
        tokens.append(Token(elt.text, lemma, pos))
    return tokens


def get_entity(elt):
    text = get_w_content(elt)
    tag = elt.get('type') if 'type' in elt.attrib else  ""
    tokens = get_tokens(elt)
    parent = elt.getparent()
    #TODO get and return lat/lng if it is a place
    return text, tokens, tag, parent


def get_entities(elt):
    entities = []
    for elt in elt.findall('.//name'):
        text, tokens, tag, parent = get_entity(elt)
        entities.append(Entity(text, tokens, tag, parent))
    return entities


def get_nested_entities(elt):
    nestedEntities = []
    for elt in elt.findall(".//rs[@type='ene']/rs[@subtype='ene']"):
        text, tokens, tag, parent = get_entity(elt)
        child = elt.xpath(".//*[self::rs or self::name]")[0]
        ne = get_entities(elt)
        #TODO get the nesting level
        nestedEntities.append(Entity(text, tokens, tag, parent, child, ne, 1))
    return nestedEntities


class Entity:
    def __init__(self, text, tokens, tag, parent=None, child=None, ne=None, level=0, lat=None, lng=None):

        self.text = text
        self.tokens = tokens
        self.tag = tag

        self.lat = lat
        self.lng = lng

        self.parent = parent
        self.child = child

        self.level = level # find a better name?
        self.ne = ne
        #self.sent = sent # sentence in which the entity occurs, useful?
        #...


# TODO
class Toponym: 
    def __init__(self, name):

        self.name = name


class Token:
    def __init__(self, text, lemma=None, pos=None):

        self.text = text
        self.lemma = lemma
        self.pos = pos

        # position, start, end ?
        

#TODO deplacer cette classe dans un nouveau fichier perdido.py
class Perdido:

    def __init__(self):

        self.text = None
        self.tei = None  # type etree xml, string or both?
        self.geojson = None
        
        self.ne = []
        self.nne = [] # nested named entities
        self.tokens = []

        self.toponyms = []

    

    def parseTEI(self):
        root = etree.fromstring(self.tei)
        
        self.tokens = get_tokens(root)
        self.ne = get_entities(root)
        
        for elt in root.findall(".//rs[@type='ene']/rs[@subtype='ene']"):
            text = get_w_content(elt)
            tag = elt.get('type') if 'type' in elt.attrib else  ""
            tokens = get_tokens(elt)
            parent = elt.getparent()
            child = elt.xpath(".//*[self::rs or self::name]")[0]
            ne = get_entities(elt)
            #TODO get the nesting level
            self.nne.append(Entity(text, tokens, tag, parent, child, ne, 1))

        

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
        res.text = content
        res.tei = getResult(r, 'xml-tei', 'xml')
        res.geojson = getResult(r, 'geojson')

        #TODO ajouter l'appel à la méthode de Perdido qui va remplir les attributs 
        res.parseTEI()

        return res


 #TODO deplacer cette classe dans un nouveau fichier geocoder.py
class Geocoder:
    def __init__(self):
        pass

