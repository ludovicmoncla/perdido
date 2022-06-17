# Perdido Geoparser Python library


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

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/ludovicmoncla/perdido/main?labpath=notebooks%2Fdemo_Geoparser.ipynb)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](http://colab.research.google.com/github/ludovicmoncla/perdido/blob/main/notebooks/demo_Geoparser.ipynb)

#### Import

```python
from perdido.geoparser import Geoparser
```

#### Run geoparser

```python
geoparser = Geoparser(lang='fr')
doc = geoparser('Je visite la ville de Lyon, Annecy et Chamonix.')
```

#### Get tokens

```python
for token in doc:
    print(f'{token.text}\tlemma: {token.lemma}\tpos: {token.pos}')
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
for entity in doc.named_entities:
    print(f'entity: {entity.text}\ttag: {entity.tag}')
    if entity.tag == 'place':
        for t in entity.toponyms:
            print(f' latitude: {t.lat}\tlongitude: {t.lng}\tsource {t.source}')
```

#### Get the list of nested named entities

```python
for nestedEntity in doc.nested_named_entities:
    print(f'entity: {nestedEntity.text}\ttag: {nestedEntity.tag}')
    if nestedEntity.tag == 'place':
        for t in nestedEntity.toponyms:
            print(f' latitude: {t.lat}\tlongitude: {t.lng}\tsource {t.source}')
```


#### Shows named entities and nested named entities using the displacy library from spaCy

```python
displacy.render(doc.to_spacy_doc(), style="ent", jupyter=True)
```

```python
displacy.render(doc.to_spacy_doc(), style="span", jupyter=True)
```




### Geocoding

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/ludovicmoncla/perdido/main?labpath=notebooks%2Fdemo_Geocoder.ipynb)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](http://colab.research.google.com/github/ludovicmoncla/perdido/blob/main/notebooks/demo_Geocoder.ipynb)

#### Import

```python
from perdido.geocoder import Geocoder
```

#### Geocode a single place name

```python
geocoder = Geocoder()
doc = geocoder('Lyon')
```

#### Geocode a list of place names

```python
geocoder = Geocoder()
doc = geocoder(['Lyon', 'Annecy', 'Chamonix'])
```

#### Get the geojson result

```python
print(doc.geojson)
```

#### Get the list of toponym candidates

```python
for t in doc.toponyms: 
    print(f'lat: {t.lat}\tlng: {t.lng}\tsource {t.source}\tsourceName {t.source_name}')
```







# Perdido Geoparser REST APIs

[http://choucas.univ-pau.fr/docs#](http://choucas.univ-pau.fr/docs#/)


## Example: call REST API in Python

```python
import requests

url = 'http://choucas.univ-pau.fr/PERDIDO/api/'
service = 'geoparsing'
data = {'content': 'Je visite la ville de Lyon, Annecy et le Mont-Blanc.'}
parameters = {'api_key': 'demo'}

r = requests.post(url+service, params=parameters, json=data)

print(r.text)
```



# Acknowledgements

``Perdido`` is an active project still under developpement.

This work was partially supported by the following projects:
* [GEODE](https://geode-project.github.io) (2020-2024): [LabEx ASLAN](https://aslan.universite-lyon.fr) (ANR-10-LABX-0081)
* [GeoDISCO](https://www.msh-lse.fr/projets/geodisco/) (2019-2020): [MSH Lyon St-Etienne](https://www.msh-lse.fr) (ANR‐16‐IDEX‐0005)
* [CHOUCAS](http://choucas.ign.fr) (2017-2022): [ANR](https://anr.fr/Projet-ANR-16-CE23-0018) (ANR-16-CE23-0018)
* [PERDIDO](http://erig.univ-pau.fr/PERDIDO/) (2012-2015): [CDAPP](https://www.pau.fr/) and [IGN](https://www.ign.fr)