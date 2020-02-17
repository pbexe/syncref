import requests
from bs4 import BeautifulSoup
import sys


files = {'input': (open(sys.argv[1], 'rb'))}
r = requests.post("http://localhost:8070/api/processHeaderDocument", files=files)

try:
    soup = BeautifulSoup(r.text, "xml")
    print("Title:", soup.find("title").string)
except AttributeError:
    print("Title not found")

a = []
try:
    authors = soup.find_all("author")
    for author in authors:
        try:
            a.append(author.persName.forename.string + " " + author.persName.surname.string)
        except AttributeError:
            # print("Not valid author")
            ...
except AttributeError:
    print("No authors found")

print("\n".join(list(set(a))))
# print(len(list(set(a))))
# print(r.text)