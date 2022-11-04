from typing import Any, List, Dict, Union
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


    def to_dict(self) -> Dict:
        return {
            'name': self.name, 
            'lat': self.lat, 
            'lng': self.lng,
            'source': self.source,
            'source_name': self.source_name,
            'type': self.type
        }


class Token:
    def __init__(self, id: str, text: str, idx: int, lemma: Union[str, None] = None, pos: Union[str, None] = None, tags: List[str] = []) -> None:
        self.id = id
        self.text = text
        self.lemma = lemma
        self.pos = pos
        self.tags = tags

        self.idx = idx # The character offset of the token within the parent document.

        # tag CONLL-U / BIO NE and NNE ?

          
    def __str__(self) -> str: 
        return self.tsv_format()


    def tsv_format(self) -> str:
        if len(self.tags) > 0:
            tags = '\t'.join(self.tags)
            return f'{self.id}\t{self.text}\t{self.lemma}\t{self.pos}\t{tags}'
        else:
            return f'{self.id}\t{self.text}\t{self.lemma}\t{self.pos}'


    def iob_format(self) -> str:
        if len(self.tags) > 0:
            tags = ' '.join(self.tags)
            return f'{self.text} {self.lemma} {self.pos} {tags}'
        else:
            return f'{self.text} {self.lemma} {self.pos}'


    def n_tagged_format(self) -> str:
        if len(self.tags) > 0:
            return '__{' + self.text + '}__[' + self.tags[0] + ']'
        else:
            return self.text


class Entity:
    def __init__(self, text: str, tokens: List[Token], tag: str, start: str, end: str, id: str=None, parent: Any = None, child: Any = None, named_entities: Any = None, level: int = 0, toponym_candidates: List[Toponym] = []) -> None:
        self.text = text
        self.tokens = tokens
        self.tag = tag

        self.id = id # tei xml id
        self.start = start # attritbut startT des elements <rs>
        self.end = end

        self.parent = parent # seulement le parent, ou la liste des parents ?
        self.child = child

        self.level = level # find a better name?
        self.named_entities = named_entities

        self.lat = toponym_candidates[0].lat if len(toponym_candidates) > 0 else None
        self.lng = toponym_candidates[0].lng if len(toponym_candidates) > 0 else None
        self.toponym_candidates = toponym_candidates

        # position, start, end ?
        if len(tokens) > 0:
            self.start_offset = tokens[0].id
            self.end_offset = tokens[-1].id
        else:
            self.start_offset = None
            self.end_offset = None
        #self.sent = sent # sentence in which the entity occurs, useful?
        #...


    def __str__(self) -> str: 
        res = self.text + " " + self.tag + "\n"
        if self.tag == 'place':
            for toponym in self.toponym_candidates:
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


def get_tokens_from_webanno() -> List[Token]:
    pass


def get_tokens_from_tei(elt: Element) -> List[Token]:
    tokens = []
    for elt in elt.findall('.//w'):
        lemma = elt.get('lemma') if 'lemma' in elt.attrib else ""
        pos = elt.get('pos') if 'pos' in elt.attrib else ""

        id = int(elt.get('id')[1:]) if 'id' in elt.attrib else None
        idx = int(elt.get('idx')) if 'idx' in elt.attrib else None

        tags = []
    
        try: 
            p = elt
            while True:
             
                p = next(p.iterancestors())
                
                if p.tag in ['rs']: # term | phr?
                    
                    # si l'id de w est le meme que startT alors B- sinon I- 
                   
                    startT = int(p.get('startT')) if 'startT' in p.attrib else None
                    if startT is not None and id is not None:
                    
                        if startT == id:
                            tag = 'B-'
                        else:
                            tag = 'I-'

                        
                        type = p.get('type') if 'type' in p.attrib else  None
                        if type is not None:
                            if type == 'place':
                                tag += 'LOC'
                            elif type == 'person':
                                tag += 'PER'
                            elif type == 'date':
                                tag += 'DATE'
                            else:
                                tag += 'OTHER'
                        
                        # recuperer le niveau dimbrication
                        # subtype="no" | subtype="ene"
                        subtype = p.get('subtype') if 'subtype' in p.attrib else  None
                        if subtype is not None:
                            #if subtype == 'no':
                            #    tag += ''
                            if subtype == 'ene':
                                tag += '-NNE'

                        tags.append(tag)
        except StopIteration:
            pass

        if len(tags) == 0:
            tags.append('O')

        tags.reverse()

        tokens.append(Token(id+1, elt.text, idx, lemma, pos, tags))
    return tokens


def get_entity(elt: Element, att_tag:str = 'type') -> Entity:
    text = get_w_content(elt)
    tag = elt.get(att_tag) if att_tag in elt.attrib else  ""
    tokens = get_tokens_from_tei(elt)
    #TODO fix this, issue with pickle etree element
    parent = ''#elt.getparent() 
    start = None
    end = None
    id = elt.get('id') if 'id' in elt.attrib else  ""
    if elt.tag == 'name':
        start = elt.get('startT') if 'startT' in elt.attrib else  None
        end = elt.get('endT') if 'endT' in elt.attrib else  None
    elif elt.tag == 'rs':
        subtype = elt.get('subtype') if 'subtype' in elt.attrib else  None
        if subtype == 'ene' or subtype == 'latlong':
            start = elt.get('startT') if 'startT' in elt.attrib else  None
            end = elt.get('endT') if 'endT' in elt.attrib else  None
        
    #TODO get and return lat/lng if it is a place
    return Entity(text = text, id = id, tokens = tokens, start = start, end = end, tag = tag, parent = parent)


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


def get_entities_from_tei(elt: Element, tag:str = 'all') -> List[Entity]:
    entities = []
    
    if tag == 'all':
        xpath = './/name'
    elif tag in ['place', 'person', 'date', 'event', 'other']:
        xpath = ".//name[@type='" + tag + "']"

    for e in elt.findall(xpath):
        entity = get_entity(e)
        if entity.tag == 'place':
            entity.toponym_candidates = get_toponyms_from_tei(e)
        entities.append(entity)

    for e in elt.findall(".//rs[@subtype='latlong']"):
        entities.append(get_entity(e, 'subtype'))

    return entities


def get_nested_entities_from_tei(elt: Element) -> List[Entity]:
    nestedEntities = []
    for e in elt.findall(".//rs[@type='ene']/rs[@subtype='ene']"):
        entity = get_entity(e)
        entity.toponym_candidates = get_toponyms_from_tei(e)
        #TODO fix this, issue with pickle etree element
        entity.child = '' # e.xpath(".//*[self::rs or self::name]")[0]
        entity.named_entities = get_entities_from_tei(e)
        #TODO get the nesting level
        entity.level = 1
        
        nestedEntities.append(entity)
    return nestedEntities

