#!/usr/bin/python

import sys
import requests

url = "https://doi.org/" + sys.argv[1]
headers = {
    'Accept': "application/x-bibtex"
    }

response = requests.request("GET", url, headers=headers)
print(response.text)