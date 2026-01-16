# scraper for hours -> daily scraper at X time in lambda using eventbridge

import requests
import os
from bs4 import BeautifulSoup, NavigableString, Tag
from dotenv import load_dotenv
from supabase import create_client, Client
import re
from datetime import date

load_dotenv()

supabase_url: str = os.environ.get("SUPABASE_URL")
supabase_key: str = os.environ.get("SUPABASE_SECRET_KEY")
supabase: Client = create_client(supabase_url, supabase_key)


# supabase pipeline

'''
grab the table with the summary "This table shows the facility hours for Recreational Sports facilities"

loop through all trs in the table for each facility, look at the a tag in the thing and see if it matches
if it does -> check the next few tds
if theres 1 td -> check the hours for TODAY! (that day) -> map the day specifically and the closed/open state
if theres 4 tds -> check the hours for mon-thu (1), fri (2), sat (3), sun (4)

add smart funcitnoalities to decipher time and whatnot properly, then insert to supabase
and u got it from there!

once this is in supabase with data, and it works, we can thorw it into lamnda as an eventbridge scraper

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

# on special holidays, grab the date as needed
def extract_special_date(nine_div) -> date | None:
    """
    Extracts the special date from the header banner.
    Returns a datetime.date or None if not found.
    """
    try:
        header_table = nine_div.find_next("table")
        header_text = header_table.find_next("tr").find("th").get_text(strip=True)
        # Example: "Martin Luther King, Jr. Day - 1/19 - 1/19/26"

        m = re.search(r'(\d{1,2})/(\d{1,2})/(\d{2})', header_text)
        if not m:
            return None

        month, day, year = map(int, m.groups())
        return date(2000 + year, month, day)

    except Exception:
        return None

def normalize_facility_name(name: str) -> str:
    """
    Normalizes facility names so that hyphenated and space-separated
    versions resolve to the same canonical form.
    """
    if not name:
        return name

    # Replace hyphens between letters with a space
    name = re.sub(r'(?<=[A-Za-z])-(?=[A-Za-z])', ' ', name)

    # Collapse multiple spaces
    name = re.sub(r'\s+', ' ', name)

    return name.strip()


facilities = (
    supabase.table("facilities")
    .select("id, name")
    .execute()
)

facility_names = []
facility_id_by_name = {
    normalize_facility_name(f["name"]) : f["id"]
    for f in facilities.data
}

url = "https://www.utrecsports.org/hours"
html = requests.get(url).text
soup = BeautifulSoup(html, "lxml")

info_table = soup.find("table", summary="This table shows the facility hours for Recreational Sports facilities.")
nine_div = soup.find("div", class_="nine columns")
table_body = info_table.find_next("tbody")



special_date = None
results = {}
for row in table_body.find_all("tr"):
    tds = row.find_all("td")

    # for now, we'll start with len being < 5 -> move to 2 bridge afterwards
    if len(tds) < 2:
        continue


    link = tds[0].find("a")
    if not link:
        continue

    facility_name = normalize_facility_name(link.get_text(strip=True))

    #print(facility_name)

    if facility_name not in facility_id_by_name:
        continue

    facility_id = facility_id_by_name[facility_name]

    hours_cells = [
        normalize_timeslots(td.get_text(separator="|", strip=True))
        for td in tds[1:]
    ]

    if len(hours_cells) == 1:
        if special_date is None:
            special_date = extract_special_date(nine_div)

        if special_date:
            response = (
                supabase.table("facility_hours")
                .update({
                    "special_date": special_date.isoformat(),
                    "special_hours": hours_cells[0]
                })
                .eq("facility_id", facility_id)
                .execute()
            )
        continue

    if len(hours_cells) == 4:
        response = (
            supabase.table("facility_hours")
            .update({
                "mon": hours_cells[0],
                "tue": hours_cells[0],
                "wed": hours_cells[0],
                "thu": hours_cells[0],
                "fri": hours_cells[1],
                "sat": hours_cells[2],
                "sun": hours_cells[3],
                # clear any stale special data
                "special_date": None,
                "special_hours": None,
            })
            .eq("facility_id", facility_id)
            .execute()
        )





