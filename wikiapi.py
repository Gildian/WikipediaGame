import requests
import concurrent.futures

DEBUG_MODE = True

URL = "https://en.wikipedia.org/w/api.php"
BLACKLISTED_SECTIONS = ["References", "External links"]
session = requests.Session()

ACTION = "action"
FORMAT = "format"
JSON = "json"
REDIRECTS = "redirects"

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
        ACTION: "query",
        "titles": page,
        FORMAT: JSON,
        "indexpageids":"",
        "prop":"categories",
        REDIRECTS:""
    }
    DATA = make_request(PARAMS)
    clean_data = {}
    clean_data["exists"] = True if DATA["query"]["pageids"][0] != '-1' else False
    if clean_data["exists"]: clean_data["title"] = DATA["query"]["pages"][DATA["query"]["pageids"][0]]["title"]
    if clean_data["exists"]: clean_data["categories"] = DATA["query"]["pages"][DATA["query"]["pageids"][0]]["categories"]
    return clean_data

def getAllSections(page: str):
    PARAMS = {
        ACTION: "parse",
        "page": page,
        "prop": "sections",
        FORMAT: JSON,
        REDIRECTS:""
    }
    DATA = make_request(PARAMS)
    return DATA["parse"]["sections"]

def getLinksBySection(page: str, section: int, valid_links):
    PARAMS = {
        ACTION: "parse",
        "page": page,
        "prop": "links",
        "section": section,
        FORMAT: JSON,
        REDIRECTS:""
    }
    DATA = make_request(PARAMS)
    valid_links.extend([link for link in DATA["parse"]["links"] if link["ns"] == 0])

def getAllValidLinks(page: str):
    valid_links = []
    sections = getAllSections(page)
    with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
        for i, section in enumerate(sections):
            if section["line"] not in BLACKLISTED_SECTIONS:
                executor.submit(getLinksBySection, page, i, valid_links)
    return valid_links