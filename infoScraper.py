# one time scraper -> just scrapes the static page of activities&features at a facility

# first pull desired webpage

# easy example

import requests
from bs4 import BeautifulSoup

url = "https://www.utrecsports.org/facilities/facility/bellmont-hall"

html = requests.get(url).text

# this should be replaced with a supabase grab and index pipeline

soup = BeautifulSoup(html, "lxml")

# soup is represented as a dom tree

div_main = soup.find("div", role="main")
div_info = div_main.find("div", class_="nine columns")

addr_h5 = div_info.find("h5", string=lambda s: s and "Facility Address" in s) # works well with typecasting
addr_para = addr_h5.find_next("p")

print(addr_para)




