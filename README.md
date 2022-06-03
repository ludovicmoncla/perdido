# Perdido Geoparser Python library



[![PyPI](https://img.shields.io/pypi/v/perdido)](https://pypi.org/project/perdido)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](http://colab.research.google.com/github/ludovicmoncla/perdido/blob/main/notebooks/demo_Geoparser.ipynb)
[![PyPI - License](https://github.com/ludovicmoncla/perdido/blob/main/LICENSE)](https://img.shields.io/pypi/l/perdido?color=yellow)

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


# How to cite Perdido

``perdido`` is an active project still under developpement.