# scrapes general TexErcise schedule from https://www.utrecsports.org/fitness-and-wellness/texercise-class-schedule#s365


import requests
import os
from bs4 import BeautifulSoup, NavigableString, Tag
from dotenv import load_dotenv
from supabase import create_client, Client
import re
from datetime import date
import uuid


load_dotenv()

supabase_url: str = os.environ.get("SUPABASE_URL")
supabase_key: str = os.environ.get("SUPABASE_SECRET_KEY")

supabase: Client = create_client(supabase_url, supabase_key)

link = "https://www.utrecsports.org/fitness-and-wellness/texercise-class-schedule#s365"
html = requests.get(link).text

soup = BeautifulSoup(html, "lxml")

# structure for navigating website

'''
div_main -> div "twelve columns" -> 
table "summary=facilityhours" && a tag says "Spring 2026 Schedule - 1/12/26 - 4/27/26" -> 
next div after with class "unseen" -> tbody -> day (SCRAPE!) -> loop thru trs and scrape all info -> 
push to supabase
'''

# to normalize times
def normalize_timeslots(s: str) -> str:

    # Normalize "Closed" (case-insensitive, trimmed)
    s = re.sub(r'\bclosed\b', 'Closed', s, flags=re.IGNORECASE)


    # Handle words first
    s = re.sub(r'\bNoon\b', '12:00 PM', s, flags=re.IGNORECASE)
    s = re.sub(r'\bMidnight\b', '12:00 AM', s, flags=re.IGNORECASE)

    # Convert tokens like:
    #   6a, 6 a, 6:59a, 6:05p, 12p
    # into:
    #   6:00 AM, 6:59 AM, 6:05 PM, 12:00 PM
    #
    # Groups:
    #   hour = 1-2 digits
    #   min  = optional :00-:59
    #   ap   = a or p (case-insensitive)
    pattern = re.compile(r'\b(?P<h>\d{1,2})(?P<m>:\d{2})?\s*(?P<ap>[ap])\b', re.IGNORECASE)

    def repl(match: re.Match) -> str:
        h = match.group('h')
        m = match.group('m') or ':00'
        ap = match.group('ap').upper()
        return f"{h}{m} { 'AM' if ap == 'A' else 'PM' }"

    return pattern.sub(repl, s)



div_main = soup.find("div", role="main")

div_row = div_main.find_all("div", class_="row", id=False)[1]

div_twelveouter = div_row.find("div", class_="twelve columns")

div_twelveinner = div_twelveouter.find("div", class_="twelve columns")

table = div_twelveinner.find_all("table", summary="Texercise Hours")[1]

# table is table of all events for spring

records = []


for tr in table.find_all("tr"):
    if tr.get("class") == ['defaultShowing']:
        # insert day into supabase
        day = tr.find("td").get_text(strip = True)
        day = day.replace("s", "")
        #print(day)

        for next_tr in tr.find_next_siblings("tr"):
            if next_tr.get("class") == ['shrinkText']:
                data_points = next_tr.find_all("td")
                time = data_points[0].get_text(strip=True)

                time = normalize_timeslots(time)

                class_name = data_points[1].get_text(strip=True)
                facility = data_points[2].get_text(strip=True)
                name = data_points[3].get_text(strip=True)

                print(day, time, class_name, facility, name)

                # supabase add
                response = (
                    supabase.table("classes")
                    .insert({
                        "day": day,
                        "time": time,
                        "name": class_name,
                        "studio": facility,
                        "instructor": name
                    })
                    .execute()
                )

        # loop thru all following, push massive into supabase



#print(table)