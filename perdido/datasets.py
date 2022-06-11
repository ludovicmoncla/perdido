from typing import Any, List, Tuple, Union
from lxml import etree


def load_edda_artfl():
    pass


def load_edda_perdido():
    pass


def load_choucas_hikes():
    pass



    
def get_data_from_artfl_tei(file_path, filename):
    file_id = filename[:-4]
    d = []
    try:
        volume = filename[6:8] 
        number = filename[9:-4] 
        head = ''
        normClass = ''
        author = ''
        txtContent = ''
        root = etree.parse(file_path+filename).getroot()
        div1 = root.find('./text/body/div1')
        if len(div1):
            for elt in div1:
                if elt.tag == 'p':
                    txtContent += ''.join(elt.itertext())
                    txtContent = txtContent.replace('\n', ' ').strip()
                elif elt.tag == 'index':
                    if elt.get('type') == 'normclass':
                        normClass = elt.get('value')
                    if elt.get('type') == 'head':
                        head = elt.get('value')
                    if elt.get('type') == 'author':
                        author = elt.get('value')
        d = [filename, volume, number, head, normClass, author, txtContent]
    except etree.XMLSyntaxError as e:
        pass
        #print(filename + ': ' + str(e))
    return d