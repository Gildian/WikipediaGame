import requests
import concurrent.futures

DEBUG_MODE = False

URL = "https://en.wikipedia.org/w/api.php"
BLACKLISTED_SECTIONS = ["References", "External links"]
session = requests.Session()

def getPageDetails(page: str):
    PARAMS = {
        "action": "query",
        "titles": page,
        "format": "json",
        "indexpageids":"",
        "prop":"categories",
        "redirects":""
    }
    response = session.get(url=URL, params=PARAMS)
    DATA = response.json()
    if DEBUG_MODE: print("printing date for page:",page,"\n",DATA)
    clean_data = {}
    clean_data["exists"] = True if DATA["query"]["pageids"][0] != -1 else False
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
    response = session.get(url=URL, params=PARAMS)
    DATA = response.json()
    if DEBUG_MODE: print("printing data for:",page,"\n",DATA)
    if DEBUG_MODE: print(DATA["parse"]["sections"])
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
    response = session.get(url=URL, params=PARAMS)
    DATA = response.json()
    for link in DATA["parse"]["links"]:
        if link["ns"] == 0:
            valid_links.append(link)

def getAllValidLinks(page: str):
    valid_links = []
    sections = getAllSections(page)
    if DEBUG_MODE: print("Getting all valid URLS in ", len(sections), " sections")
    pool = concurrent.futures.ThreadPoolExecutor(max_workers=25)
    section_index = 0
    for section in sections:
        if section["line"] in BLACKLISTED_SECTIONS:
            section_index += 1
            continue
        else:
            pool.submit(getLinksBySection, page, section_index, valid_links)
            section_index += 1
            if DEBUG_MODE: print("submitted to queue")
    pool.shutdown(wait=True)
    if DEBUG_MODE: print("Pool empty, current list:", valid_links)
    return valid_links