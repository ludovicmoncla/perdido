# Perdido Geoparser Python library



[![PyPI](https://img.shields.io/pypi/v/perdido)](https://pypi.org/project/perdido)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](http://colab.research.google.com/github/ludovicmoncla/perdido/blob/main/notebooks/demo_Geoparser.ipynb)
[![PyPI - License](https://img.shields.io/pypi/l/perdido?color=yellow)](https://github.com/ludovicmoncla/perdido/blob/main/LICENSE)

[http://erig.univ-pau.fr/PERDIDO/](http://erig.univ-pau.fr/PERDIDO/)

## Installation

To install the latest stable version, you can use:
```bash
pip install --upgrade perdido
```


## Demonstration

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](http://colab.research.google.com/github/ludovicmoncla/perdido/blob/main/notebooks/demo_Geoparser.ipynb)



# Perdido Geoparser REST APIs

[http://choucas.univ-pau.fr/docs#](http://choucas.univ-pau.fr/docs#/)


```python
from perdido import geoparser

p = geoparser.Geoparser()
doc = p.parse('Je visite la ville de Lyon, Annecy et le Mont-Blanc.')

print(' -- tokens -- ')
for token in doc.tokens:
    print(token.text, token.lemma, token.pos)

print(' -- tei -- ')
doc.tei

print(' -- geojson -- ')
doc.geojson

print(' -- named entities -- ')
for entity in doc.ne:
    print(entity.text, '[' + entity.tag + ']')
    if entity.tag == 'place':
        entity.print_toponyms()

print(' -- nested named entities -- ')
for nestedEntity in doc.nne:
    print(nestedEntity.text, '[' + nestedEntity.tag + ']')
    if nestedEntity.tag == 'place':
        nestedEntity.print_toponyms()
```


## Example: call REST API in Python

```python
import requests

url = 'http://choucas.univ-pau.fr/PERDIDO/api/'
service = 'geoparsing'
content = 'Je visite la ville de Lyon, Annecy et le Mont-Blanc.'
parameters = {'api_key': 'demo', 'content':content}

r = requests.post(url+service, params=parameters)

print(r.text)
```



# Acknowledgements

``Perdido`` is an active project still under developpement.

This work was partially supported by the following projects:
* [GEODE](https://geode-project.github.io) (2020-2024): [LabEx ASLAN](https://aslan.universite-lyon.fr) (ANR-10-LABX-0081)
* [GeoDISCO](https://www.msh-lse.fr/projets/geodisco/) (2019-2020): [MSH Lyon St-Etienne](https://www.msh-lse.fr) (ANR‐16‐IDEX‐0005)
* [CHOUCAS](http://choucas.ign.fr) (2017-2022): [ANR](https://anr.fr/Projet-ANR-16-CE23-0018) (ANR-16-CE23-0018)
* [PERDIDO](http://erig.univ-pau.fr/PERDIDO/) (2012-2015): [CDAPP](https://www.pau.fr/) and [IGN](https://www.ign.fr).