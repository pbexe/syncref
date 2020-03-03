import os
import parser
from os import listdir
from os.path import isfile, join
from shutil import copyfile

from tqdm import tqdm

from grobextract import ExtractionError, content_negotiation, extract, py2bib

path = "./papers/frank-papers"

files = [f for f in listdir(path) if isfile(join(path, f))]
s = 0
f = 0
for file_ in tqdm(files):
    if file_.endswith(".pdf"):
        with open(join(path, file_), "rb") as pdf:
            info = extract(pdf)
            try:
                data = content_negotiation(*info)
                s+=1
                os.makedirs("extracted/" + file_ + ".d")
                with open("extracted/" + file_ + ".d/reference.bib", "w") as fp:
                    fp.write(data)
                copyfile(join(path, file_), "extracted/" + file_ + ".d/" + file_)                
            except ExtractionError as e:
                f += 1
                bibtex = {}
                bibtex["ID"] = "Unknown"
                bibtex["ENTRYTYPE"] = "misc"
                if info[0]:
                    bibtex["title"] = info[0]
                if info[1]:
                    bibtex["author"] = " and ".join(data[1])
                bibtex["comment"] = "ERROR: No candidate was found. This is all the data I could extract"
                print(py2bib([bibtex]))
                os.makedirs("extracted/" + file_ + ".d")
                with open("extracted/" + file_ + ".d/reference.bib", "w") as fp:
                    fp.write(py2bib([bibtex]))
                copyfile(join(path, file_), "extracted/" + file_ + ".d/" + file_)
            
print("S:", s)
print("F:", f)
