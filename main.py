import wikipediaapi
import torch
import torchtext
import sys 

DEBUG_MODE = False
path_taken = []
wiki_wiki = wikipediaapi.Wikipedia('WikipediaBot')

def create_embeddings():
    global glove
    glove = torchtext.vocab.GloVe(name="6B", # trained on Wikipedia 2014 corpus
                                 dim=300)    # embedding size = 50

def get_closest_link(page, goal_page):
    page_py = wiki_wiki.page(page)
    links = page_py.links.keys()
    unsqueezed_search = glove[goal_page].unsqueeze(0)
    closest_match = ["",-99999999999]
    if DEBUG_MODE: print(f"goal:{goal_page}\ncurrent:{page}\nlink count:{len(links)}")
    for link in links:
        link_name = link.lower()
        if link_name == goal_page:
            closest_match[0] = link
            closest_match[1] = current_score
            break
        link_name_split = link_name.split()
        blacklist_words = ["wikipedia:","template:","category:","template talk:"]
        if any(blword in link_name for blword in blacklist_words):
            continue
        else:
            for name in link_name_split:
                current_score = torch.nn.functional.cosine_similarity(unsqueezed_search,glove[name].unsqueeze(0))
                if DEBUG_MODE: print(name, float(current_score))
                if closest_match[1] < current_score and link not in path_taken and wiki_wiki.page(link).exists():
                    closest_match[0] = link
                    closest_match[1] = current_score
    if DEBUG_MODE: print(closest_match)
    if closest_match[0] == "":
        print("COULD NOT FIND NEXT PAGE")
        exit()
    return closest_match

def solve_wiki_game(current_page, end_page, depth):
    sys.stdout.write('\b')
    sys.stdout.write(next(spinner))
    sys.stdout.flush()
    if depth < 0:
        print("DEPTH REACHED 0")
        return
    if current_page.lower() == end_page.lower():
        return
    closest_link = get_closest_link(current_page, end_page)
    path_taken.append(closest_link[0])
    if DEBUG_MODE: print("current path:",path_taken)
    depth -= 1
    if closest_link[0].lower() == end_page.lower():
        return
    else:
        return solve_wiki_game(closest_link[0], end_page, depth)

def spinning_cursor():
    while True:
        for cursor in '|/-\\':
            yield cursor

spinner = spinning_cursor()

if __name__ == "__main__":
    start_article = input("Enter the starting article:")
    if not wiki_wiki.page(start_article).exists():
        print("That article doesn't exist!")
        exit()
    start_article = wiki_wiki.page(start_article).title
    end_article = input("Enter the ending article:")
    if not wiki_wiki.page(end_article).exists():
        print("That article doesn't exist!")
        exit()
    end_article = wiki_wiki.page(end_article).title
    depth = 100

    print(f"Finding a path from {start_article} to {end_article} (within {depth} steps)")

    create_embeddings()
    path_taken.append(start_article)
    sys.stdout.write("Processing: ")
    solve_wiki_game(start_article.lower(), end_article.lower(), depth)
    print(path_taken)