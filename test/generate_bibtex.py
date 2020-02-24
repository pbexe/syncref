from os import listdir
from os.path import isfile, join
import parser
from grobextract import extract, ExtractionError, content_negotiation


path = "./papers/mendelay-papers"

files = [f for f in listdir(path) if isfile(join(path, f))]
for file_ in files:
    info = extract(open(join(path, file_), "rb"))
    try:
        data = content_negotiation(*info)
        print(data)
    except ExtractionError as e:
        print(e)
        if info[0] or info[1]:
            print("Extracted info:", info)
        else:
            print("No info extracted")