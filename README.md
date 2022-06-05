# Perdido Geoparser Python library

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](http://colab.research.google.com/github/ludovicmoncla/perdido/blob/main/notebooks/demo_Geoparser.ipynb)
[![PyPI](https://img.shields.io/pypi/v/perdido)](https://pypi.org/project/perdido)
[![PyPI - License](https://img.shields.io/pypi/l/perdido?color=yellow)](https://github.com/ludovicmoncla/perdido/blob/main/LICENSE)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/perdido)


[http://erig.univ-pau.fr/PERDIDO/](http://erig.univ-pau.fr/PERDIDO/)


## Installation

To install the latest stable version, you can use:
```bash
pip install --upgrade perdido
```


## Quick start


### Geoparsing

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](http://colab.research.google.com/github/ludovicmoncla/perdido/blob/main/notebooks/demo_Geoparser.ipynb)

#### Import

```python
from perdido.geoparser import Geoparser
```

#### Run geoparser

```python
geoparser = Geoparser(lang='fr')
doc = geoparser('Je visite la ville de Lyon, Annecy et le Mont-Blanc.')
```

#### Get tokens

```python
for token in doc:
    print(f'token: {token.text}\tlemma: {token.lemma}\tpos: {token.pos}')
```

#### Print the XML-TEI output

```python
print(doc.tei)
```

#### Print the GeoJSON output

```python
print(doc.geojson)
```

#### Get the list of named entities

```python
for entity in doc.ne:
    print(f'entity: {entity.text}\ttag: {entity.tag}')
    if entity.tag == 'place':
        for t in entity.toponyms:
            print(f' latitude: {t.lat}\tlongitude: {t.lng}\tsource {t.source}')
```

#### Get the list of nested named entities

```python
for nestedEntity in doc.nne:
    print(f'entity: {nestedEntity.text}\ttag: {nestedEntity.tag}')
    if nestedEntity.tag == 'place':
        for t in nestedEntity.toponyms:
            print(f' latitude: {t.lat}\tlongitude: {t.lng}\tsource {t.source}')
```



# Perdido Geoparser REST APIs

[http://choucas.univ-pau.fr/docs#](http://choucas.univ-pau.fr/docs#/)


## Example: call REST API in Python

```python
import requests

url = 'http://choucas.univ-pau.fr/PERDIDO/api/'
service = 'geoparsing'
content = 'Je visite la ville de Lyon, Annecy et le Mont-Blanc.'
parameters = {'api_key': 'demo', 'content': content}

r = requests.post(url+service, params=parameters)

print(r.text)
```



# Acknowledgements

``Perdido`` is an active project still under developpement.

This work was partially supported by the following projects:
* [GEODE](https://geode-project.github.io) (2020-2024): [LabEx ASLAN](https://aslan.universite-lyon.fr) (ANR-10-LABX-0081)
* [GeoDISCO](https://www.msh-lse.fr/projets/geodisco/) (2019-2020): [MSH Lyon St-Etienne](https://www.msh-lse.fr) (ANR‐16‐IDEX‐0005)
* [CHOUCAS](http://choucas.ign.fr) (2017-2022): [ANR](https://anr.fr/Projet-ANR-16-CE23-0018) (ANR-16-CE23-0018)
* [PERDIDO](http://erig.univ-pau.fr/PERDIDO/) (2012-2015): [CDAPP](https://www.pau.fr/) and [IGN](https://www.ign.fr)