
from typing import Any, List, Tuple, Union
from lxml.etree import Element


class Toponym: 
    def __init__(self, name: str, lat: float, lng: float, source: str, source_name: str, type: str) -> None:

        self.name = name
        self.lat = lat
        self.lng = lng
        self.source = source
        self.source_name = source_name
        self.type = type
    
    def __str__(self) -> str: 
        return self.name + " " + str(self.lat) + " " + str(self.lng) + " " + self.source + " " + self.source_name


class Token:
    def __init__(self, text: str, lemma: Union[str, None] = None, pos: Union[str, None] = None) -> None:

        self.text = text
        self.lemma = lemma
        self.pos = pos

        # tag BIO NE and NNE ?

        # position, start, end ?
        
    def __str__(self) -> str: 
        return self.text + " " + self.lemma + " " + self.pos



class Entity:
    def __init__(self, text: str, tokens: List[Token], tag: str, parent: Any = None, child: Any = None, ne: Any = None, level: int = 0, toponyms: List[Toponym] = []) -> None:

        self.text = text
        self.tokens = tokens
        self.tag = tag

        self.parent = parent
        self.child = child

        self.level = level # find a better name?
        self.ne = ne

        self.toponyms = toponyms

        #self.sent = sent # sentence in which the entity occurs, useful?
        #...


    def __str__(self) -> str: 
        res = self.text + " " + self.tag + "\n"
        if self.tag == 'place':
            for toponym in self.toponyms:
                res += " toponym candidate > "+ str(toponym) + "\n"
        return res


def get_w_content(element: Element) -> str:
    content = ""
    for w in element.findall('.//w'):
        content += w.text + " "
    return content.strip()


def parent_exists(elt: Element, parent_name: Element) -> bool:
    try: 
        parent_node = next(elt.iterancestors())
        if parent_name is not None:
            if parent_node.tag == parent_name:
                if 'start' in parent_node.attrib:
                    return True
        return parent_exists(parent_node, parent_name)
    except StopIteration:
        return False


def get_tokens_from_tei(elt: Element) -> List[Token]:
    tokens = []
    for elt in elt.findall('.//w'):
        lemma = elt.get('lemma') if 'lemma' in elt.attrib else  ""
        pos = elt.get('type') if 'type' in elt.attrib else  ""
        tokens.append(Token(elt.text, lemma, pos))
    return tokens


def get_entity(elt: Element) -> Tuple[str, List[Token], str, Element]:
    text = get_w_content(elt)
    tag = elt.get('type') if 'type' in elt.attrib else  ""
    tokens = get_tokens_from_tei(elt)
    parent = elt.getparent()
    #TODO get and return lat/lng if it is a place
    return text, tokens, tag, parent


def get_toponyms_from_tei(elt: Element) -> List[Toponym]:
    toponyms = []
    for elt in elt.findall('.//location/geo'):
        parent = elt.getparent()
        text = get_w_content(parent)
        coords = elt.text.split()
        source = elt.get('source') if 'source' in elt.attrib else  ""
        rend = elt.get('rend') if 'rend' in elt.attrib else  ""
        type = 'ne' if parent.tag == 'name' else  'nne'
        toponyms.append(Toponym(text, coords[0], coords[1], source, rend, type))
    return toponyms


def get_toponyms_from_geojson(json_content: Any) -> List[Toponym]:
    toponyms = []

    for feature in json_content['features']:

        lat = feature['geometry']['coordinates'][0]
        lng = feature['geometry']['coordinates'][1]
        name = feature['properties']['name']
        source_name = feature['properties']['sourceName']
        source = feature['properties']['source']
        name = feature['properties']['name']
        type = 'ne'

        toponyms.append(Toponym(name, lat, lng, source, source_name, type))
    return toponyms


def get_entities_from_tei(elt: Element) -> List[Entity]:
    entities = []
    for elt in elt.findall('.//name'):
        text, tokens, tag, parent = get_entity(elt)
        toponyms = get_toponyms_from_tei(elt)
        entities.append(Entity(text, tokens, tag, parent, toponyms=toponyms))
    return entities


def get_nested_entities_from_tei(elt: Element) -> List[Entity]:
    nestedEntities = []
    for elt in elt.findall(".//rs[@type='ene']/rs[@subtype='ene']"):
        text, tokens, tag, parent = get_entity(elt)
        child = elt.xpath(".//*[self::rs or self::name]")[0]
        ne = get_entities_from_tei(elt)
        #TODO get the nesting level
        toponyms = get_toponyms_from_tei(elt)
        nestedEntities.append(Entity(text, tokens, tag, parent, child, ne, 1, toponyms=toponyms))
    return nestedEntities

