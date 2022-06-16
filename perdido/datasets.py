from typing import Any, List, Tuple, Union, Dict
from lxml import etree
import pkg_resources
import pandas as pd
import os




def load_edda_artfl() -> Dict:
    filepath = pkg_resources.resource_stream(__name__, 'datasets/edda_artfl/edda_artf_dataset.csv')
    d = {}
    d['data'] = pd.read_csv(filepath, sep='\t')
    d['description'] = 'The description of the dataset will be available soon!'
    d['feature_names'] = ['filename', 'volume', 'number', 'head', 'normClass', 'author', 'text']

    return d


def load_edda_perdido():
    pass


def load_choucas_hikes():
    pass


def export_edda_artfl_as_csv():

    path = '../datasets/edda_artfl/'
    data = []
    for doc in os.listdir(path):
        if doc[-4:] == '.tei':
            data.append(get_data_from_artfl_tei(path, doc))
    df = pd.DataFrame(data, columns=['filename', 'volume', 'number', 'head', 'normClass', 'author', 'text'])
    df = df.dropna()
    df = df.sort_values(['volume', 'number']).reset_index(drop = True)

    df.to_csv(path + 'edda_artf_dataset.csv', sep='\t', index=False)


def get_data_from_artfl_tei(file_path: str, filename: str):
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