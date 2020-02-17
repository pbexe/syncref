import requests
from bs4 import BeautifulSoup
import sys
from habanero import Crossref, cn

def extract(fp):
    files = {"input": fp,
             "consolidateHeader": "1"}
    r = requests.post("http://localhost:8080/api/processHeaderDocument", files=files, data={
        "consolidateHeader": "1"
    })
    title = ""
    print(r.text)
    try:
        soup = BeautifulSoup(r.text, "xml")
        print("Title:", soup.find("title").string)
        title = soup.find("title").string
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


    cr = Crossref(mailto="miles@budden.net")
    print("Query:", title + " " + " ".join(list(set(a))))
    r = cr.works(query=title + " " + " ".join(list(set(a))))
    if r["status"] == "ok":
        print("Result Title:", r["message"]["items"][0]["title"][0])
        # print("DOI:", r["message"]["items"][0]["DOI"])
        print("\n=========================\n")
        print(cn.content_negotiation(ids = r["message"]["items"][0]["DOI"], format = "bibentry"))
    else:
        ... # Uh oh



if __name__ == "__main__":
    with open(sys.argv[1], "rb") as fp:
        extract(fp)
# print(len(list(set(a))))
# print(r.text)