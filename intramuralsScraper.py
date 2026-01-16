import requests
import os
from bs4 import BeautifulSoup, NavigableString, Tag
from dotenv import load_dotenv
from supabase import create_client, Client