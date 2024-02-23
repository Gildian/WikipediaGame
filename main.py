import wikipediaapi
import torch
import torchtext
import sys 
import heapq
DEBUG_MODE = False  # Set this to True for debug output, such as search results, scores, and more clerical info. 
path_taken = [] # Global variable for the path
wiki_wiki = wikipediaapi.Wikipedia('WikipediaBot')

def create_embeddings():
    global glove
    glove = torchtext.vocab.GloVe(name="6B", # trained on Wikipedia 2014 corpus
                                 dim=300)    # embedding size = 50

def get_closest_link(page, goal_page):
    page_py = wiki_wiki.page(page)  # first, grab the current page from wikipediai
    links = page_py.links.keys()    # get links off of page
    unsqueezed_search = glove[goal_page].unsqueeze(0)   # converts the Tensor so that we can do the Cosine Similarity later
    closest_match = ["",-99999999999]   # stores whatever the best result was from the process below
    if DEBUG_MODE: print(f"goal:{goal_page}\ncurrent:{page}\nlink count:{len(links)}")
    for link in links:  # this will loop over all links that we got earlier to find which is the closest to the goal
        link_name = link.lower()
        if link_name == goal_page:  # this check sees if the goal page is on our current page, if it is just go straight to it
            closest_match[0] = link
            closest_match[1] = current_score
            break
        link_name_split = link_name.split() # splits up the link title into its individual words to process since glove cannot handle more than 1 word
        blacklist_words = ["wikipedia:","template:","category:","template talk:"] # black listed words, these will almost always lead to the wrong answer
        if any(blword in link_name for blword in blacklist_words):
            continue
        else:
            for name in link_name_split:
                current_score = torch.nn.functional.cosine_similarity(unsqueezed_search,glove[name].unsqueeze(0))   # the actual scoring function for a given page title, the closer to 1 the better
                if DEBUG_MODE: print(name, float(current_score))
                if closest_match[1] < current_score and link not in path_taken and wiki_wiki.page(link).exists(): # updates the closest match if it has a better score, the path hasnt been traveled, and it exists
                    closest_match[0] = link
                    closest_match[1] = current_score
    if DEBUG_MODE: print(closest_match)
    if closest_match[0] == "":  # error state for if we get to a page with no links on it
        print("COULD NOT FIND NEXT PAGE")
        exit()
    return closest_match

def solve_wiki_game(current_page, end_page, depth): # recursive function for solving the game, it is what is called to get the search started
    sys.stdout.write('\b')
    sys.stdout.write(next(spinner))
    sys.stdout.flush()  # code to add a spinner to the console so the user can tell its working
    if depth < 0:   # base case for if over the set depth amount of paths has been traversed, meaning a solution was not found
        print("DEPTH REACHED 0")
        return
    if current_page.lower() == end_page.lower():    # base case for if the current page is our goal page
        return
    closest_link = get_closest_link(current_page, end_page) # finds the next best page using the above function
    path_taken.append(closest_link[0])  # updates the path taken with the new best page
    if DEBUG_MODE: print("current path:",path_taken)
    depth -= 1  # counts down the depth so program doesnt run forever
    if closest_link[0].lower() == end_page.lower(): # case for if the closest link is our solution to the game
        return
    else:
        return solve_wiki_game(closest_link[0], end_page, depth)    # recursive call to check the next level for a result

def best_first_search(start_page, goal_page):
    queue = []
    heapq.heappush(queue, (0, start_page))  # priority queue to store the pages to be explored
    visited = set()  # set to store the visited pages
    while queue:
        _, current_page = heapq.heappop(queue)  # get the page with the highest priority
        if current_page.lower() == goal_page.lower():  # if the current page is the goal page, return the path
            return path_taken
        if current_page.lower() not in visited:  # if the current page has not been visited
            visited.add(current_page.lower())  # mark the current page as visited
            closest_link = get_closest_link(current_page, goal_page)  # find the next best page
            path_taken.append(closest_link[0])  # update the path taken
            heapq.heappush(queue, (closest_link[1], closest_link[0]))  # add the next page to the priority queue
    return None  # if no path is found

def spinning_cursor(): # spinning cursor helper code
    while True:
        for cursor in '|/-\\':
            yield cursor

spinner = spinning_cursor()

if __name__ == "__main__":
    # get start article
    start_article = input("Enter the starting article:")
    start_article = wiki_wiki.page(start_article)
    # check if wiki exists
    if not start_article.exists():
        print("That article doesn't exist!")
        exit()
    # check if valid page
    if "Category:Disambiguation pages" in start_article.categories.keys():
        print("You cannot use a Disambiguation page!")
        exit()
    # set to page title
    start_article = start_article.displaytitle

    # get end article
    end_article = input("Enter the ending article:")
    end_article = wiki_wiki.page(end_article)
    # check if wiki exists
    if not end_article.exists():
        print("That article doesn't exist!")
        exit()
    # check if valid page
    if "Category:Disambiguation pages" in end_article.categories.keys():
        print("You cannot use a Disambiguation page!")
        exit()
    # set to page title
    end_article = end_article.displaytitle

    depth = 100

    print(f"Finding a path from {start_article} to {end_article} (within {depth} steps)")
    
    create_embeddings()
    path_taken.append(start_article)
    sys.stdout.write("Processing: ")
    best_first_search(start_article.lower(), end_article.lower())
    print(path_taken)