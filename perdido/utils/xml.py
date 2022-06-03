
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


def get_toponyms(elt):
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


def get_entities(elt):
    entities = []
    for elt in elt.findall('.//name'):
        text, tokens, tag, parent = get_entity(elt)
        toponyms = get_toponyms(elt)
        entities.append(Entity(text, tokens, tag, parent, toponyms=toponyms))
    return entities


def get_nested_entities(elt):
    nestedEntities = []
    for elt in elt.findall(".//rs[@type='ene']/rs[@subtype='ene']"):
        text, tokens, tag, parent = get_entity(elt)
        child = elt.xpath(".//*[self::rs or self::name]")[0]
        ne = get_entities(elt)
        #TODO get the nesting level
        toponyms = get_toponyms(elt)
        nestedEntities.append(Entity(text, tokens, tag, parent, child, ne, 1, toponyms=toponyms))
    return nestedEntities




class Entity:
    def __init__(self, text, tokens, tag, parent=None, child=None, ne=None, level=0, toponyms=None):

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


    def __str__(self): 
        res = self.text + " " + self.tag + "\n"
        if self.tag == 'place':
            for toponym in self.toponyms:
                res += " toponym candidate > "+ str(toponym) + "\n"
        return res


class Toponym: 
    def __init__(self, name, lat, lng, source, sourceName, type):

        self.name = name
        self.lat = lat
        self.lng = lng
        self.source = source
        self.sourceName = sourceName
        self.type = type
    
    def __str__(self): 
        return self.name + " " + self.lat + " " + self.lng + " " + self.source + " " + self.sourceName


class Token:
    def __init__(self, text, lemma=None, pos=None):

        self.text = text
        self.lemma = lemma
        self.pos = pos

        # position, start, end ?
        
    def __str__(self): 
        return self.text + " " + self.lemma + " " + self.pos
