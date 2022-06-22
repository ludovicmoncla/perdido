from typing import Dict

import pkg_resources
#import importlib.resources as pkg_resources
import pandas as pd

from perdido.perdido import PerdidoCollection


def load_edda_artfl() -> Dict:
    filepath = pkg_resources.resource_stream(__name__, 'data/edda_artfl/edda_artf_dataset.csv')
    d = {}
    d['data'] = pd.read_csv(filepath, sep='\t')
    d['description'] = 'The description of the dataset will be available soon!'
    d['feature_names'] = ['filename', 'volume', 'number', 'head', 'normClass', 'author', 'text']

    return d


def load_edda_perdido(dataset:str = 'nominatim') -> Dict:
    d = {}
    collection = PerdidoCollection()
    
    filepath = pkg_resources.resource_filename(__name__, 'data/edda_perdido/' + dataset + '/edda_perdido_vol7_' + dataset +'_dataset.pickle')
    
    collection.load(filepath)
    
    d['data'] = collection
    d['description'] = 'The description of the dataset will be available soon!'
    
    return d


def load_choucas_hikes() -> None:
    pass




