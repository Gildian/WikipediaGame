import sys 
import re
from search_functions import best_first_search, solve_wiki_game, greedy_search
from helpers import wiki_wiki

def process_wiki_article(name):
    html_cleaner = re.compile('<.*?>')
    article = wiki_wiki.page(name)
    
    # check if wiki exists
    if not article.exists():
        print("That article doesn't exist!")
        exit()
    
    # check if valid page
    if "Category:Disambiguation pages" in article.categories.keys():
        print("You cannot use a Disambiguation page!")
        exit()
    
    # set to page title
    return re.sub(html_cleaner,'',article.displaytitle)

def get_user_input(prompt):
    user_input = input(prompt)
    return process_wiki_article(user_input)

if __name__ == "__main__":
    # get start article
    start_article = get_user_input("Enter the starting article:")
    
    # get end article
    end_article = get_user_input("Enter the ending article:")
    
    depth = 100

    print(f"Finding a path from {start_article} to {end_article} (within {depth} steps)")
    
    path_taken = [start_article]

    # Uncomment the algo you want to use
    sys.stdout.write("Processing Best First Search: ")
    print("\n",best_first_search(start_article.lower(), end_article.lower()))

    sys.stdout.write("Processing Closest Page: ")
    print("\n",solve_wiki_game(start_article.lower(), end_article.lower(), depth, path_taken))

    sys.stdout.write("Processing Greedy Search: ")
    print("\n",greedy_search(start_article.lower(), end_article.lower()))
