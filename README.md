# Perdido Geoparser Python library


[http://erig.univ-pau.fr/PERDIDO/](http://erig.univ-pau.fr/PERDIDO/)


[![PyPI](https://img.shields.io/pypi/v/perdido)](https://pypi.org/project/perdido)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](http://colab.research.google.com/github/ludovicmoncla/perdido/blob/main/notebooks/demo_Geoparser.ipynb)
![PyPI - License](https://img.shields.io/pypi/l/perdido?color=yellow)

## Installation

To install the latest stable version, you can use:
```bash
pip install --upgrade perdido
```


## Demonstration

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](http://colab.research.google.com/github/ludovicmoncla/perdido/blob/main/notebooks/demo_Geoparser.ipynb)



# Perdido Geoparser Web Services

[http://choucas.univ-pau.fr/docs#](http://choucas.univ-pau.fr/docs#/)

```python
import requests

parameters = {'api_key': 'demo', 'content':'Je visite la ville de Lyon, Annecy et le Mont-Blanc.'}
r = requests.post('http://choucas.univ-pau.fr/PERDIDO/api/geoparsing/', params=parameters)
print(r.text)
```

``perdido`` is an active project still under developpement.