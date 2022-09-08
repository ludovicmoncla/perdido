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
    description = 'The description of the dataset will be available soon!'
    return load_pickle_perdidocollection('data/edda_perdido/edda_perdido_vol7_' + dataset +'_dataset.pickle', description)


def load_choucas_perdido() -> Dict:
    description = 'The description of the dataset will be available soon!'
    return load_pickle_perdidocollection('data/choucas/choucas_perdido.pickle', description)


def load_pickle_perdidocollection(path:str, description:str) -> Dict:
    
    d = {}
    filepath = pkg_resources.resource_filename(__name__, path)

    collection = PerdidoCollection()
    collection.load(filepath)
    
    d['data'] = collection
    d['description'] = description

    return d



