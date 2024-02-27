import wikipediaapi
import torch
import torchtext
import re
import requests
from bs4 import BeautifulSoup


def create_embeddings():
    return torchtext.vocab.GloVe(name="6B", # trained on Wikipedia 2014 corpus
                                 dim=300)    # embedding size = 300
    
glove = create_embeddings()


DEBUG_MODE = False  # Set this to True for debug output, such as search results, scores, and more clerical info. 
wiki_wiki = wikipediaapi.Wikipedia('WikipediaBot')

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


def get_wikipedia_links(url):
    # Send a GET request to the URL
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all anchor tags (links)
        links = soup.find_all('a', href=True)
        
        # Extract the URLs from the anchor tags
        link_urls = [link['href'] for link in links if link['href'].startswith('/wiki/')]
        
        # Add Wikipedia domain to relative URLs
        link_urls = ['https://en.wikipedia.org' + link for link in link_urls]
        
        return link_urls
    else:
        print("Failed to retrieve the page:", response.status_code)
        return []

url = 'https://en.wikipedia.org/wiki/Python_(programming_language)'
links = get_wikipedia_links(url)
for link in links:
    print(link)

'''
def get_closest_links(page, goal_page, path_taken):
    page_py = wiki_wiki.page(page)
    links = page_py.links.keys()
    best_links = []
    if DEBUG_MODE:
        print(f"goal:{goal_page}\ncurrent:{page}\nlink count:{len(links)}")
    for link in links:
        link_name = link.lower()
        if link_name == goal_page:
            best_links.insert(0, (link, 1))
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
            best_links.append((link, converted_score))
            if DEBUG_MODE:
                print(link, float(converted_score))
    if not best_links:
        print("COULD NOT FIND NEXT PAGE")
        exit()
    return sorted(best_links, key=lambda tup: tup[1], reverse=True)
'''