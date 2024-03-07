import torch
import torchtext
from wikiapi import getAllValidLinks, getPageDetails
import re

cosine_dict = {}

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
    if not article["exists"]:
        print("That article doesn't exist!")
        exit()
    for category in article["categories"]:
        if "Category:Disambiguation pages" == category["title"]:
            print("You cannot use a Disambiguation page!")
            exit()
    if DEBUG_MODE: print(article)
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

# Compile the regular expression pattern
pattern = re.compile('\\(|\\)|\\\"')
def get_word_score(target: str, unit: str):
    if unit in cosine_dict:
        return cosine_dict[unit]
    unit_clean = pattern.sub(" ", unit)
    target_clean = pattern.sub(" ", target)
    unit_split = set(word for word in unit_clean.lower().split() if word in glove)
    target_split = set(word for word in target_clean.lower().split() if word in glove)
    if not unit_split:
        return -1
    # Pre-calculate unsqueeze(0) for each word
    unit_vectors = [glove[word].unsqueeze(0) for word in unit_split]
    target_vectors = [glove[word].unsqueeze(0) for word in target_split]
    # calculate scores
    scores = [torch.nn.functional.cosine_similarity(unit_vector, target_vector) 
            for unit_vector in unit_vectors for target_vector in target_vectors]
    # combine words 
    unit_mean = torch.mean(torch.vstack(unit_vectors), dim=0)
    target_mean = torch.mean(torch.vstack(target_vectors), dim=0)
    # get score of new tensors using cosine similarity
    combined_score = torch.nn.functional.cosine_similarity(unit_mean.unsqueeze(0), target_mean.unsqueeze(0))
    # find the best score
    best_score = max(max(scores, default=-1), combined_score)
    cosine_dict[unit] = best_score
    return best_score

blacklist_words = ["wikipedia:", "template:", "category:", "template talk:", "(disambiguation)","user:","talk:","(identifier)"] # these are pages that we want to avoid since they give bad data
def get_closest_links(page, goal_page, path_taken):
    THRESHOLD = 0.0 # set to -1 to effectivly allow all articles. valid range is [-1,1)
    links = getAllValidLinks(page)
    best_links = set()
    if DEBUG_MODE:
        print(f"goal:{goal_page}\ncurrent:{page}\nlink count:{len(links)}")
    for link in links: # iterate over every link
        link_name = link.lower()
        if link_name == goal_page: # if this link is the goal page simply exit since we have accomplished the goal
            best_links.add((link, 1))
            break
        if any(blword in link_name for blword in blacklist_words) or link in path_taken: # checks that the link isnt blacklisted or has already been traveled
            continue
        else:
            link_score = get_word_score(goal_page, link_name)
            if link_score > THRESHOLD:
                best_links.add((link, link_score))
            if DEBUG_MODE: print(link, float(link_score))
    if len(best_links) == 0:
        print("COULD NOT FIND NEXT PAGE")
        print("Last page:",page)
        exit()
    return best_links

def get_closest_link(page, goal_page, path_taken):
    links = getAllValidLinks(page)
    closest_match = ["", -1]
    if DEBUG_MODE:
        print(f"goal:{goal_page}\ncurrent:{page}\nlink count:{len(links)}")
    for link in links:
        link_name = link.lower()
        if link_name == goal_page: # checks if this link is the solution
            closest_match[0] = link
            closest_match[1] = 1
            break
        if any(blword in link_name for blword in blacklist_words): # checks if link is blacklisted
            continue
        elif link in path_taken or link_name == page.lower(): # checks if link has already been traveled or is the same page as the current one
            continue
        else:
            link_score = get_word_score(goal_page, link_name)
            if closest_match[1] < link_score: # if the page is better than our current page update it
                closest_page = getPageDetails(link)
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