# one time scraper -> just scrapes the static page of activities&features at a facility

# first pull desired webpage

# easy example

import requests
from bs4 import BeautifulSoup, NavigableString, Tag
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url = "https://www.utrecsports.org/facilities/facility/bellmont-hall"

html = requests.get(url).text

# this should be replaced with a supabase grab and index pipeline

soup = BeautifulSoup(html, "lxml")

# soup is represented as a dom tree

div_main = soup.find("div", role="main")
div_info = div_main.find("div", class_="nine columns")

addr_h5 = div_info.find("h5", string=lambda s: s and "Facility Address" in s) # works well with typecasting
addr_para = addr_h5.find_next("p")

lines = []
for node in addr_para.contents:
    if isinstance(node, Tag) and node.name == 'a':
        break # stops at first a tag

    if isinstance(node, NavigableString):
        text = node.strip()
        if text: # otherwise, just appends my text where i need it if the node is simply text (skips br, for example)
            lines.append(text)
    
address = ", ".join(lines).replace("\xa0", " ") # for each new line, join with a comma, replace the weird formatting thingy with a blank
print(address)




