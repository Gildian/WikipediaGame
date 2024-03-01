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

def get_word_score(target: str, unit: str):
    # Sanitize input strings
    unit = re.sub('\\(|\\)|\\\'|\\\"|\\-', "", unit)
    target = re.sub('\\(|\\)|\\\'|\\\"|\\-', "", target)

    # Split strings into individual words
    unit_split = [word for word in unit.lower().split() if word in glove]

    # Check if the target is in the glove dictionary
    if target.lower() in glove:
        target_vectors = [glove[target.lower()]]
    else:
        # If the target is not in the glove dictionary, split it into individual words
        target_split = [word for word in target.lower().split() if word in glove]
        if len(target_split) > 1:
            # If the target is multiple words, calculate the average of their vectors
            target_vectors = [torch.mean(torch.stack([glove[word] for word in target_split]), dim=0)]
        else:
            target_vectors = [glove[word] for word in target_split]

    # Calculate word scores
    scores = [torch.nn.functional.cosine_similarity(target_vector.unsqueeze(0), glove[unit_name].unsqueeze(0))
              for target_vector in target_vectors for unit_name in unit_split]

    # Calculate average score
    converted_score = sum(scores) / len(scores) if scores else 0

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