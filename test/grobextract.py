import requests
files = {'input': (open('better.pdf', 'rb'))}
r = requests.post("http://localhost:8070/api/processHeaderDocument", files=files)
print(r.text)