import sys 
import re
from bestfirst import best_first_search
from closestpage import solve_wiki_game
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

if __name__ == "__main__":
    # get start article
    
    start_article = input("Enter the starting article:")
    start_article = process_wiki_article(start_article)

    # get end article
    end_article = input("Enter the ending article:")
    end_article = process_wiki_article(end_article)
    
    depth = 100

    print(f"Finding a path from {start_article} to {end_article} (within {depth} steps)")
    
    path_taken = []
    path_taken.append(start_article)

    # Uncomment the algo you want to use
    print("Best First Search")
    sys.stdout.write("Processing: ")
    print("\n",best_first_search(start_article.lower(), end_article.lower()))
    print("Closest Page")
    sys.stdout.write("Processing: ")
    print("\n",solve_wiki_game(start_article.lower(), end_article.lower(), depth, path_taken))
