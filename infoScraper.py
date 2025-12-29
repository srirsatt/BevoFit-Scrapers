# one time scraper -> just scrapes the static page of activities&features at a facility

# first pull desired webpage

# easy example

import requests
import os
from bs4 import BeautifulSoup, NavigableString, Tag
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

supabase_url: str = os.environ.get("SUPABASE_URL")
supabase_key: str = os.environ.get("SUPABASE_SECRET_KEY")

# supabase pipeline
'''
query the url from the DB (prelisted)
access the url, feed it to bs4, return 
    Facility Addr
    Facility Activities
    Facility Features
and add these all back into the supabase db under their respective columns
'''

supabase: Client = create_client(supabase_url, supabase_key)

#url = "https://www.utrecsports.org/facilities/facility/bellmont-hall"

facilities = (
    supabase.table("facilities")
    .select("id", "facility_url", "slug")
    .execute()
)

for facility in facilities.data:
    facility_id = facility["id"]
    url = facility["facility_url"]
    slug = facility["slug"]
    print(slug, url) # slug is for MY debug idenfication, id is for tracking through the supabase, and url is the url

    # run the bs4 scraper
    html = requests.get(url).text

    soup = BeautifulSoup(html, "lxml")
    # soup is a dom tree
    div_main = soup.find("div", role="main")
    div_info = div_main.find("div", class_="nine columns")
    addr_h5 = div_info.find("h5", string=lambda s: s and "Facility Address" in s)
    addr_para = addr_h5.find_next("p")

    lines = []
    for node in addr_para.contents:
        if isinstance(node, Tag) and node.name =='a':
            break # stops at a tag
        if isinstance(node, NavigableString):
            text = node.strip()
            if text:
                lines.append(text)

    address = ", ".join(lines).replace("\xa0", " ")
    print(address)

    # add back to supabase
    response = (
        supabase.table("facilities")
        .update({"addr": address})
        .eq("id", facility_id)
        .execute()
    )




'''
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

'''


