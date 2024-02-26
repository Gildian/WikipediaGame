import wikipediaapi
import torch
import torchtext
import re
import sys
import requests
import wikipediaapi
import concurrent.futures

def create_embeddings():
    return torchtext.vocab.GloVe(name="6B", # trained on Wikipedia 2014 corpus
                                 dim=300)    # embedding size = 300
    
glove = create_embeddings()


DEBUG_MODE = False  # Set this to True for debug output, such as search results, scores, and more clerical info. 
if DEBUG_MODE:
    wikipediaapi.log.setLevel(level=wikipediaapi.logging.DEBUG)
    out_hdlr=wikipediaapi.logging.StreamHandler(sys.stderr)
    out_hdlr.setFormatter(wikipediaapi.logging.Formatter('%(asctime)s %(message)s'))
    out_hdlr.setLevel(wikipediaapi.logging.DEBUG)
    wikipediaapi.log.addHandler(out_hdlr)

wiki_wiki = wikipediaapi.Wikipedia('WikipediaBot','en')
def spinning_cursor(): # spinning cursor helper code
    while True:
        for cursor in '|/-\\':
            yield cursor

spinner = spinning_cursor()

def get_word_score(target, unit): # function for getting the score of two words
    # split target here to prevent repetition in code
    unsqueezed_unit = glove[unit.lower()].unsqueeze(0)
    target_split = target.split()
    target_score = 0
    target_count = 0
    for names in target_split:
        unsqueezed_target = glove[names.lower()].unsqueeze(0)
        score = torch.nn.functional.cosine_similarity(unsqueezed_target,unsqueezed_unit)
        if score != 0:
            target_score += score
            target_count += 1
    converted_score = 0
    if target_count != 0: converted_score = target_score / target_count
    return converted_score

def get_closest_link(page, goal_page, path_taken):
    html_cleaner = re.compile('<.*?>')
    page_py = wiki_wiki.page(page)  # first, grab the current page from wikipediai
    links = getAllValidLinks(page_py)    # get links off of page
    closest_match = ["",-1]   # stores whatever the best result was from the process below
    if DEBUG_MODE: print(f"goal:{goal_page}\ncurrent:{page}\nlink count:{len(links)}")
    for link in links:  # this will loop over all links that we got earlier to find which is the closest to the goal
        link_name = link["*"].lower()
        if link_name == goal_page:  # this check sees if the goal page is on our current page, if it is just go straight to it
            closest_match[0] = link["*"]
            closest_match[1] = 1
            break
        link_name_split = link_name.split() # splits up the link title into its individual words to process since glove cannot handle more than 1 word
        blacklist_words = ["wikipedia:","template:","category:","template talk:","(disambiguation)"] # black listed words, these will almost always lead to the wrong answer
        if any(blword in link_name for blword in blacklist_words):
            continue
        elif link["*"] in path_taken or link_name == page_py.displaytitle.lower():
            continue
        else:
            name_value = 0
            name_count = 0
            for name in link_name_split:
                current_score = get_word_score(goal_page,name)
                if current_score != 0:
                    name_value += current_score
                    name_count += 1
                    if DEBUG_MODE: print(name, float(current_score))
            converted_score = 0
            if name_count != 0: converted_score = name_value / name_count
            if closest_match[1] < converted_score: # updates the closest match if it has a better score, the path hasnt been traveled, and it exists
                closest_page = wiki_wiki.page(link["*"])
                if closest_page.exists() and closest_page.displaytitle not in path_taken:
                    closest_match[0] = re.sub(html_cleaner,'',closest_page.displaytitle)
                    closest_match[1] = converted_score
    if DEBUG_MODE: print("printing closest match:",closest_match)
    if closest_match[0] == "":  # error state for if we get to a page with no links on it
        print("COULD NOT FIND NEXT PAGE")
        exit()
    return closest_match

def get_closest_links(page, goal_page, path_taken):
    page_py = wiki_wiki.page(page)
    links = getAllValidLinks(page_py)
    best_links = []
    if DEBUG_MODE:
        print(f"goal:{goal_page}\ncurrent:{page}\nlink count:{len(links)}")
    for link in links:
        link_name = link["*"].lower()
        if link_name == goal_page:
            best_links.insert(0, (link["*"], 1))
            break
        link_name_split = link_name.split()
        blacklist_words = ["wikipedia:", "template:", "category:", "template talk:", "(disambiguation)"]
        if any(blword in link_name for blword in blacklist_words) or link["*"] in path_taken:
            continue
        else:
            name_value = 0
            name_count = 0
            for name in link_name_split:
                current_score = get_word_score(goal_page, name)
                if current_score != 0:
                    name_value += current_score
                    name_count += 1
            converted_score = -1 if name_count == 0 else name_value / name_count
            best_links.append((link["*"], converted_score))
            if DEBUG_MODE:
                print(link["*"], float(converted_score))
    if not best_links:
        print("COULD NOT FIND NEXT PAGE")
        exit()
    return sorted(best_links, key=lambda tup: tup[1], reverse=True)

def get_closest_links_greedy(page, goal_page, path_taken):
    page_py = wiki_wiki.page(page)
    links = getAllValidLinks(page_py)
    best_links = []
    if DEBUG_MODE:
        print(f"goal:{goal_page}\ncurrent:{page}\nlink count:{len(links)}")
    for link in links:
        link_name = link["*"].lower()
        if link_name == goal_page:
            best_links.insert(0, (link["*"], 1))
            break
        link_name_split = link_name.split()
        blacklist_words = ["wikipedia:", "template:", "category:", "template talk:", "(disambiguation)"]
        if any(blword in link_name for blword in blacklist_words) or link in path_taken:
            continue
        else:
            name_value = 0
            name_count = 0
            for name in link_name_split:
                current_score = get_word_score(goal_page, name)
                if current_score != 0:
                    name_value += current_score
                    name_count += 1
            converted_score = -1 if name_count == 0 else name_value / name_count
            best_links.append((link["*"], converted_score))
            if DEBUG_MODE:
                print(link["*"], float(converted_score))
    return sorted(best_links, key=lambda tup: tup[1], reverse=True)

# Section for getting valid URLs
URL = "https://en.wikipedia.org/w/api.php"
BLACKLISTED_SECTIONS = ["References","External links"]
def getLinksBySection(page: wikipediaapi.WikipediaPage,section: int,valid_links):
    session = requests.Session()
    PARAMS = {
        "action":"parse",
        "page":page.title.replace(" ","_"),
        "prop":"links",
        "section":section,
        "format":"json"
    }
    response = session.get(url=URL,params=PARAMS)
    DATA = response.json()
    for link in DATA["parse"]["links"]:
        if link["ns"] == 0:
            valid_links.append(link)

def getAllValidLinks(page: wikipediaapi.WikipediaPage):
    valid_links = []
    if DEBUG_MODE: print("Getting all valid URLS in ",len(page.sections)," sections")
    pool = concurrent.futures.ThreadPoolExecutor(max_workers=25)
    for section in page.sections:
        if section.title in BLACKLISTED_SECTIONS:
            continue
        else:
            pool.submit(getLinksBySection,page,page.sections.index(section),valid_links)
            if DEBUG_MODE: print("submitted to queue")
    pool.shutdown(wait=True)
    if DEBUG_MODE: print("Pool empty, current list:",valid_links)
    return valid_links