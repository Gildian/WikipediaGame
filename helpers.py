import torch
import torchtext
from wikiapi import getAllValidLinks, getPageDetails
import re

def create_embeddings():
    return torchtext.vocab.GloVe(name="6B", dim=300)
glove = create_embeddings()

DEBUG_MODE = False  # Set this to True for debug output, such as search results, scores, and more clerical info. 

def spinning_cursor():
    while True:
        for cursor in '|/-\\':
            yield cursor
spinner = spinning_cursor()

def process_wiki_article(name):
    article = getPageDetails(name)
    # check if wiki exists
    if not article["exists"]:
        print("That article doesn't exist!")
        exit()
    # check if valid page
    for category in article["categories"]:
        if "Category:Disambiguation pages" == category["title"]:
            print("You cannot use a Disambiguation page!")
            exit()
    # set to page title
    return article["title"]

def get_user_input(prompt):
    user_input = input(prompt)
    return process_wiki_article(user_input)

def validateWord(goal: str):
    goal,_ = re.subn('\\(|\\)|\\\'|\\\"|\\-',"",goal)
    goal_split = goal.split()
    for name in goal_split:
        if name.lower() in glove:
            return True
    return False

def get_word_score(target: str, unit: str): # function for getting the score of two words
    unit,_ = re.subn('\\(|\\)|\\\'|\\\"|\\-',"",unit) # sanitize unit
    unit_split = unit.lower().split()
    target,_ = re.subn('\\(|\\)|\\\'|\\\"|\\-',"",target)
    target_split = target.lower().split()
    word_score = 0
    word_count = 0 # these variables will be used for calulating the score of the two words
    for target_name in target_split:
        if target_name in glove:
            for unit_name in unit_split:
                if unit_name in glove:
                    # Get unsqueezed tenors of both names, which we know exist because of the previous if statements
                    unsqueezed_target = glove[target_name].unsqueeze(0)
                    unsqueezed_unit = glove[unit_name].unsqueeze(0)
                    score = torch.nn.functional.cosine_similarity(unsqueezed_target, unsqueezed_unit) # will give a result since both words are in glove vectors
                    word_score += score
                    word_count += 1
            
    converted_score = 0
    if word_count != 0:
        converted_score = word_score / word_count # gets the average score which should always be between 1 and -1, in if statement to prevent divide by 0 error
    return converted_score

blacklist_words = ["wikipedia:", "template:", "category:", "template talk:", "(disambiguation)"] # these are pages that we want to avoid since they give bad data
def get_closest_links(page, goal_page, path_taken):
    links = getAllValidLinks(page)
    best_links = []
    if DEBUG_MODE:
        print(f"goal:{goal_page}\ncurrent:{page}\nlink count:{len(links)}")
    for link in links: # iterate over every link
        link_name = link["*"].lower()
        if link_name == goal_page: # if this link is the goal page simply exit since we have accomplished the goal
            best_links.insert(0, (link["*"], 1))
            break
        if any(blword in link_name for blword in blacklist_words) or link["*"] in path_taken: # checks that the link isnt blacklisted or has already been traveled
            continue
        else:
            link_score = get_word_score(goal_page, link_name)
            best_links.append((link["*"], link_score))
            if DEBUG_MODE: print(link["*"], float(link_score))
    if len(best_links) == 0:
        print("COULD NOT FIND NEXT PAGE")
        print("Last page:",page)
        exit()
    return sorted(best_links, key=lambda tup: tup[1], reverse=True)

def get_closest_link(page, goal_page, path_taken):
    links = getAllValidLinks(page)
    closest_match = ["", -1]
    if DEBUG_MODE:
        print(f"goal:{goal_page}\ncurrent:{page}\nlink count:{len(links)}")
    for link in links:
        link_name = link["*"].lower()
        if link_name == goal_page: # checks if this link is the solution
            closest_match[0] = link["*"]
            closest_match[1] = 1
            break
        if any(blword in link_name for blword in blacklist_words): # checks if link is blacklisted
            continue
        elif link["*"] in path_taken or link_name == page.lower(): # checks if link has already been traveled or is the same page as the current one
            continue
        else:
            link_score = get_word_score(goal_page, link_name)
            if closest_match[1] < link_score: # if the page is better than our current page update it
                closest_page = getPageDetails(link["*"])
                if closest_page["exists"] and closest_page["title"] not in path_taken: # confirm the page exists
                    closest_match[0] = closest_page["title"]
                    closest_match[1] = link_score
    if DEBUG_MODE:
        print("printing closest match:", closest_match)
    if closest_match[0] == "":
        print("COULD NOT FIND NEXT PAGE")
        print("Last page:",page)
        exit()
    return closest_match