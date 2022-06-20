from typing import Any, List, Tuple, Union, Dict
from lxml import etree
import pkg_resources
#import importlib.resources as pkg_resources
import pandas as pd
import os

from perdido.perdido import PerdidoCollection
from perdido.geoparser import Geoparser



def load_edda_artfl() -> Dict:
    filepath = pkg_resources.resource_stream(__name__, 'data/edda_artfl/edda_artf_dataset.csv')
    d = {}
    d['data'] = pd.read_csv(filepath, sep='\t')
    d['description'] = 'The description of the dataset will be available soon!'
    d['feature_names'] = ['filename', 'volume', 'number', 'head', 'normClass', 'author', 'text']

    return d


def load_edda_perdido(volume: str ='all') -> Dict:
    d = {}
    collection = PerdidoCollection()
    if volume == 'all':
        for vol in range(1,18):
            if vol < 10:
                vol_n = '0' + str(vol)
            else:
                vol_n = str(vol)
            filepath = pkg_resources.resource_filename(__name__, 'data/edda_perdido/edda_perdido_dataset' + vol_n + '.pickle')
            tmp = PerdidoCollection()
            tmp.load(filepath)
            collection.extend(tmp)

        d['data'] = collection
        d['description'] = 'The description of the dataset will be available soon!'
       
    else:
        filepath = pkg_resources.resource_filename(__name__, 'data/edda_perdido/edda_perdido_dataset_' + volume + '.pickle')
   
        
        collection.load(filepath)
        
        d['data'] = collection
        d['description'] = 'The description of the dataset will be available soon!'
    
    return d


def load_choucas_hikes() -> None:
    pass


def export_edda_artfl_as_csv() -> None:

    path = '../data/edda_artfl/'
    data = []
    for doc in os.listdir(path):
        if doc[-4:] == '.tei':
            data.append(get_data_from_artfl_tei(path, doc))
    df = pd.DataFrame(data, columns=['filename', 'volume', 'number', 'head', 'normClass', 'author', 'text'])
    df = df.dropna()
    df = df.sort_values(['volume', 'number']).reset_index(drop = True)

    df.to_csv(path + 'edda_artf_dataset.csv', sep='\t', index=False)


def get_data_from_artfl_tei(file_path: str, filename: str) -> List[str]:
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


def dump_edda_perdido() -> None:
    input_path = '/Users/lmoncla/Documents/Data/Corpus/EDDA/articles_all/test/'
    #input_path = '/Users/lmoncla/git/github.com/lmoncla/perdido/perdido/data/edda_artfl/'
    volumes = {}
    volume = 'volume00'
    for doc in os.listdir(input_path):
        if doc[-4:] == '.tei':
            if doc[:8] == volume:
                volumes[volume].append(get_data_from_artfl_tei(input_path, doc))
            else:
                volume = doc[:8]
                volumes[volume] = []
    
    for volume, data in volumes.items():
        df = pd.DataFrame(data, columns=['filename', 'volume', 'number', 'head', 'normClass', 'author', 'text'])
        df = df.dropna()
        df = df.sort_values(['volume', 'number']).reset_index(drop = True)
        
        geoparser = Geoparser(version = 'Encyclopedie')
        docs = geoparser(df.text)

        df = df.drop(['text'], axis=1)
        
        docs.metadata = df.to_dict('records')

        ouput_path = '/Users/lmoncla/git/github.com/lmoncla/perdido/perdido/data/edda_perdido/'
        docs.dump(ouput_path + 'edda_perdido117_dataset_' + volume + '.pickle')
    