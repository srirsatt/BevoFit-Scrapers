import requests
import os
from bs4 import BeautifulSoup, NavigableString, Tag
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

supabase_url: str = os.environ.get("SUPABASE_URL")
supabase_key: str = os.environ.get("SUPABASE_SECRET_KEY")

supabase: Client = create_client(supabase_url, supabase_key)

link = "https://www.utrecsports.org/intramurals"
html = requests.get(link).text

soup = BeautifulSoup(html, "lxml")

div_main = soup.find("div", role="main")
div_nine_cols = div_main.find("div", class_="nine columns")

team_sport_table = div_nine_cols.find("table", summary="table showing intramural team sport leagues and their registration details")
single_double_table = div_nine_cols.find("table", summary="table showing intramural singles and doubles sport leagues and their registration details")
one_day_table = div_nine_cols.find("table", summary="Table showing one day intramural tournaments")
special_events_table = div_nine_cols.find("table", summary="Table showing special events for intramural sports")
tables = {
    "Team Sport Leagues": team_sport_table,
    "Singles and Doubles Leagues": single_double_table,
    "One-Day Tournaments": one_day_table,
    "Special Events": special_events_table
}

for table_name, table in tables.items(): # traversing through hashmap
    table_body = table.find_next("tbody")
    for row in table_body.find_all("tr"):
        # team sport rows
        tds = row.find_all("td")

        link = tds[0].find("a")
        if not link: 
            continue

        activity_name = link.get_text(strip=True)
        print(table_name)
        print(activity_name)

        registration_dates = tds[1].get_text(strip=True)
        print(registration_dates)

        event_start = tds[2].get_text(strip=True)

        fee = tds[3].get_text(strip=True)

        response = (
            supabase.table("intramurals")
            .insert({
                "category": table_name,
                "event_name": activity_name,
                "event_fee": fee,
                "reg_dates": registration_dates,
                "event_dates": event_start
            })
            .execute()
        )





        



        


