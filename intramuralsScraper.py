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

