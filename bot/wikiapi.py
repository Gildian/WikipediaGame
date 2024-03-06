import logging
import requests
from urllib.parse import unquote
from bs4 import BeautifulSoup

import concurrent.futures

DEBUG_MODE = False

URL = "https://en.wikipedia.org/w/api.php"
BLACKLISTED_SECTIONS = ["References", "External links"]
session = requests.Session()
logger = logging.getLogger(__name__)

def make_request(params):
    try:
        response = session.get(url=URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as http_err:
        logger.error(f'HTTP error occurred: {http_err}')
    except Exception as err:
        logger.error(f'Other error occurred: {err}')

def getTwoRandomPages():
    PARAMS = {
        "action": "query",
        "format": "json",
        "list": "random",
        "rnlimit": "2",
        "rnnamespace": "0"
    }
    DATA = make_request(PARAMS)
    return DATA["query"]["random"]

def getPageDetails(page: str):
    page = unquote(page)
    PARAMS = {
        "action": "query",
        "titles": page,
        "format": "json",
        "indexpageids": "",
        "prop": "categories",
        "cllimit": "max",
        "redirects": ""
    }
    if DEBUG_MODE: print("params:",PARAMS)
    DATA = make_request(PARAMS)
    clean_data = {}
    clean_data["exists"] = True if DATA["query"]["pageids"][0] != '-1' else False
    if clean_data["exists"]:
        clean_data["title"] = DATA["query"]["pages"][DATA["query"]["pageids"][0]]["title"]
        clean_data["categories"] = DATA["query"]["pages"][DATA["query"]["pageids"][0]]["categories"]
    return clean_data

def getAllSections(page: str):
    PARAMS = {
        "action": "parse",
        "page": page,
        "prop": "sections",
        "format": "json",
        "redirects": ""
    }
    DATA = make_request(PARAMS)
    return DATA["parse"]["sections"]

def getLinksBySection(page: str, section: int, valid_links):
    PARAMS = {
        "action": "parse",
        "page": page,
        "prop": "links",
        "section": section,
        "format": "json",
        "redirects": ""
    }
    DATA = make_request(PARAMS)
    valid_links.extend([link for link in DATA["parse"]["links"] if link["ns"] == 0])

def getLinksInLead(page: str, valid_links):
    PARAMS = {
        "action": "query",
        "format": "json",
        "prop": "info",
        "titles": page,
        "redirects": "",
        "indexpageids": "",
        "inprop": "url"
    }
    DATA = make_request(PARAMS)
    page_text = DATA["query"]["pages"][DATA["query"]["pageids"][0]]["fullurl"]
    full_page = session.get(url=page_text)
    soup = BeautifulSoup(full_page.text, features="html.parser")
    div_zone = soup.select("div.mw-content-ltr.mw-parser-output p")
    infobox_zone = soup.select("table.infobox")
    wikitable_zone = soup.select("table.wikitable")
    for data in wikitable_zone:
        for link in data.select("a[href]"):
            if "/wiki/" in link['href'] and not "File:" in link['href'] and not "Help:" in link["href"]:
                valid_links.append({'ns': 0, 'exists': '', '*': link['href'].replace("/wiki/", "").replace("_", " ")})
    for data in infobox_zone:
        for link in data.select("a[href]"):
            if "/wiki/" in link['href'] and not "File:" in link['href'] and not "Help:" in link["href"]:
                valid_links.append({'ns': 0, 'exists': '', '*': link['href'].replace("/wiki/", "").replace("_", " ")})
    for paragraph in div_zone:
        for link in paragraph.select("a[href]"):
            if "/wiki/" in link['href'] and not "File:" in link['href'] and not "Help:" in link["href"]:
                valid_links.append({'ns': 0, 'exists': '', '*': link['href'].replace("/wiki/", "").replace("_", " ")})

def getAllValidLinks(page: str):
    page = unquote(page)
    valid_links = []
    getLinksInLead(page, valid_links)
    sections = getAllSections(page)
    with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
        for i, section in enumerate(sections):
            if section["line"] not in BLACKLISTED_SECTIONS:
                executor.submit(getLinksBySection, page, i, valid_links)
    if DEBUG_MODE: print("Valid links:",valid_links)
    return valid_links
