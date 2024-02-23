import sys 
from bestfirst import best_first_search
from closestpage import solve_wiki_game
from helpers import wiki_wiki
    
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
    
    path_taken = []
    path_taken.append(start_article)
    sys.stdout.write("Processing: ")
    
    # Uncomment the algo you want to use
    # best_first_search(start_article.lower(), end_article.lower())
    solve_wiki_game(start_article.lower(), end_article.lower(), depth, path_taken)
    print(path_taken)