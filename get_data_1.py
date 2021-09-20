import subprocess
import urllib3
from bs4 import BeautifulSoup

link = 'http://www.healthdata.org/covid/data-downloads'

http = urllib3.PoolManager()

response = http.request('GET', link)

soup = BeautifulSoup(response.data, 'html.parser')

data = soup.find_all('a')

file_links = []

for i in range(len(data)):
    try:
        if '.zip' in str(data[i]['href']):
            file_links.append(data[i])
    except:
        continue

print(file_links[0].find(text=True))

for i in range(len(file_links)):
    if i < len(file_links) - 3:
        link = str(file_links[i]['href'])
    else:
        link = 'http://www.healthdata.org' + str(file_links[i]['href'])

    subprocess.call(['wget', link, '-O temp' + str(i) + '.zip'])

subprocess.call(['unzip', '*.zip'])
