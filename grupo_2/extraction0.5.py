# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

url = 'https://www.omie.es/en/file-access-list?parents%5B0%5D=/&parents%5B1%5D=Day-ahead%20Market&parents%5B2%5D=3.%20Curves&dir=Monthly%20files%20with%20aggregate%20supply%20and%20demand%20curves%20of%20Day-ahead%20market%20including%20bid%20units&realdir=curva_pbc_uof'
html = requests.get(url).content
soup = BeautifulSoup(html, 'lxml')
keywords = ["curva_pbc_uof&"]
links = []
for a_tag in soup.find_all('a'):
    href = a_tag.get('href')
    if href and any(word in href for word in keywords):
        links.append(href)
base_url = url
cleaned_links = [urljoin(base_url, link) for link in links]
for link in cleaned_links:
    print(link)