import parser
from os import listdir
from os.path import isfile, join

from tqdm import tqdm

from grobextract import ExtractionError, content_negotiation, extract, py2bib

path = "./papers/frank-papers"

files = [f for f in listdir(path) if isfile(join(path, f))]
s = 0
f = 0
for file_ in tqdm(files):
    info = extract(open(join(path, file_), "rb"))
    try:
        data = content_negotiation(*info)
        s+=1
        print(data)
    except ExtractionError as e:
        f += 1
        bibtex = {}
        bibtex["ID"] = "Unknown"
        bibtex["ENTRYTYPE"] = "misc"
        if info[0]:
            bibtex["title"] = info[0]
        if info[1]:
            bibtex["author"] = " and ".join(data[1])
        print(py2bib([bibtex]))
        
        # print(e)
        # if info[0] or info[1]:
        #     print("Extracted info:", info)
        # else:
        #     print("No info extracted")
print("S:", s)
print("F:", f)
