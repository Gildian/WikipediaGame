import torch
import torchtext
from wikiapi import getAllValidLinks, getPageDetails

def create_embeddings():
    return torchtext.vocab.GloVe(name="6B", dim=300)

glove = create_embeddings()


DEBUG_MODE = True  # Set this to True for debug output, such as search results, scores, and more clerical info. 

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

def get_word_score(target, unit): # function for getting the score of two words
    # split target here to prevent repetition in code
    unsqueezed_unit = glove[unit.lower()].unsqueeze(0)
    target_split = target.split()
    target_score = 0
    target_count = 0
    for names in target_split:
        unsqueezed_target = glove[names.lower()].unsqueeze(0)
        score = torch.nn.functional.cosine_similarity(unsqueezed_target, unsqueezed_unit)
        if score != 0:
            target_score += score
            target_count += 1
    converted_score = 0
    if target_count != 0:
        converted_score = target_score / target_count
    return converted_score

def get_closest_links(page, goal_page, path_taken):
    links = getAllValidLinks(page)
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
    if len(best_links) == 0:
        print("COULD NOT FIND NEXT PAGE")
        exit()
    return sorted(best_links, key=lambda tup: tup[1], reverse=True)

def get_closest_link(page, goal_page, path_taken):
    links = getAllValidLinks(page)
    closest_match = ["", -1]
    if DEBUG_MODE:
        print(f"goal:{goal_page}\ncurrent:{page}\nlink count:{len(links)}")
    for link in links:
        link_name = link["*"].lower()
        if link_name == goal_page:
            closest_match[0] = link["*"]
            closest_match[1] = 1
            break
        link_name_split = link_name.split()
        blacklist_words = ["wikipedia:", "template:", "category:", "template talk:", "(disambiguation)"]
        if any(blword in link_name for blword in blacklist_words):
            continue
        elif link["*"] in path_taken or link_name == page.lower():
            continue
        else:
            name_value = 0
            name_count = 0
            for name in link_name_split:
                current_score = get_word_score(goal_page, name)
                if current_score != 0:
                    name_value += current_score
                    name_count += 1
                    if DEBUG_MODE: print(name, float(current_score))
            converted_score = 0
            if name_count != 0:
                converted_score = name_value / name_count
            if closest_match[1] < converted_score:
                closest_page = getPageDetails(link["*"])
                if closest_page["exists"] and closest_page["title"] not in path_taken:
                    closest_match[0] = closest_page["title"]
                    closest_match[1] = converted_score
    if DEBUG_MODE:
        print("printing closest match:", closest_match)
    if closest_match[0] == "":
        print("COULD NOT FIND NEXT PAGE")
        exit()
    return closest_match