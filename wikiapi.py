import requests
import concurrent.futures
from bs4 import BeautifulSoup

DEBUG_MODE = False

URL = "https://en.wikipedia.org/w/api.php"
BLACKLISTED_SECTIONS = ["References", "External links"]
session = requests.Session()

def make_request(params):
    try:
        response = session.get(url=URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')

def getPageDetails(page: str):
    PARAMS = {
        "action": "query",
        "titles": page,
        "format": "json",
        "indexpageids":"",
        "prop":"categories",
        "redirects":""
    }
    DATA = make_request(PARAMS)
    clean_data = {}
    clean_data["exists"] = True if DATA["query"]["pageids"][0] != '-1' else False
    if clean_data["exists"]: clean_data["title"] = DATA["query"]["pages"][DATA["query"]["pageids"][0]]["title"]
    if clean_data["exists"]: clean_data["categories"] = DATA["query"]["pages"][DATA["query"]["pageids"][0]]["categories"]
    return clean_data

def getAllSections(page: str):
    PARAMS = {
        "action": "parse",
        "page": page,
        "prop": "sections",
        "format": "json",
        "redirects":""
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
        "redirects":""
    }
    DATA = make_request(PARAMS)
    valid_links.extend([link for link in DATA["parse"]["links"] if link["ns"] == 0])

def getLinksInLead(page: str, valid_links):
    PARAMS = {
        "action":"parse",
        "format":"json",
        "prop":"text",
        "page":page,
        "redirects":"",
        "section":"0"
    }
    DATA = make_request(PARAMS)
    page_text = DATA["parse"]["text"]["*"]
    soup = BeautifulSoup(page_text,features="html.parser")
    div_zone = soup.select("div.mw-content-ltr.mw-parser-output p")
    # print(div_zone)
    for paragraph in div_zone:
        for link in paragraph.select("a[href]"):
            if "/wiki/" in link['href']:
                valid_links.append({'ns':0,'exists':'','*':link['href'].replace("/wiki/","").replace("_"," ")})
    

def getAllValidLinks(page: str):
    valid_links = []
    getLinksInLead(page, valid_links)
    sections = getAllSections(page)
    with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
        for i, section in enumerate(sections):
            if section["line"] not in BLACKLISTED_SECTIONS:
                executor.submit(getLinksBySection, page, i, valid_links)
    return valid_links