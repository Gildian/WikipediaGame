import wikipediaapi
import torch
from generatevectors import glove

DEBUG_MODE = False  # Set this to True for debug output, such as search results, scores, and more clerical info. 
wiki_wiki = wikipediaapi.Wikipedia('WikipediaBot')

def spinning_cursor(): # spinning cursor helper code
    while True:
        for cursor in '|/-\\':
            yield cursor

spinner = spinning_cursor()

def get_word_score(target, unit): # function for getting the score of two words
    unsqueezed_target = glove[target.lower()].unsqueeze(0)
    unsqueezed_unit = glove[unit.lower()].unsqueeze(0)
    score = torch.nn.functional.cosine_similarity(unsqueezed_target,unsqueezed_unit)
    return score

def get_closest_link(page, goal_page, path_taken):
    page_py = wiki_wiki.page(page)  # first, grab the current page from wikipediai
    links = page_py.links.keys()    # get links off of page
    closest_match = ["",-1]   # stores whatever the best result was from the process below
    if DEBUG_MODE: print(f"goal:{goal_page}\ncurrent:{page}\nlink count:{len(links)}")
    for link in links:  # this will loop over all links that we got earlier to find which is the closest to the goal
        link_name = link.lower()
        if link_name == goal_page:  # this check sees if the goal page is on our current page, if it is just go straight to it
            closest_match[0] = link
            closest_match[1] = 1
            break
        link_name_split = link_name.split() # splits up the link title into its individual words to process since glove cannot handle more than 1 word
        blacklist_words = ["wikipedia:","template:","category:","template talk:"] # black listed words, these will almost always lead to the wrong answer
        if any(blword in link_name for blword in blacklist_words):
            continue
        else:
            for name in link_name_split:
                current_score = get_word_score(goal_page,name)
                if DEBUG_MODE: print(name, float(current_score))
                if closest_match[1] < current_score and link not in path_taken and wiki_wiki.page(link).exists(): # updates the closest match if it has a better score, the path hasnt been traveled, and it exists
                    closest_match[0] = link
                    closest_match[1] = current_score
    if DEBUG_MODE: print(closest_match)
    if closest_match[0] == "":  # error state for if we get to a page with no links on it
        print("COULD NOT FIND NEXT PAGE")
        exit()
    return closest_match