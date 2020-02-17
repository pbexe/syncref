#!/usr/bin/python

import sys
import requests

url = "https://doi.org/" + sys.argv[1]
headers = {
    'Accept': "application/x-bibtex"
    }

response = requests.get(url, headers=headers)
print(response.text)