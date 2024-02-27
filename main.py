import sys 
from search_functions import best_first_search, solve_wiki_game # , greedy_search
from helpers import get_user_input
import time

if __name__ == "__main__":
    # get start article
    start_article = get_user_input("Enter the starting article:")
    
    # get end article
    end_article = get_user_input("Enter the ending article:")
    
    depth = 100

    print(f"Finding a path from {start_article} to {end_article} (within {depth} steps)")
    
    path_taken = [start_article]

    # Uncomment the algo you want to use
    start = time.time()
    sys.stdout.write("Processing Best First Search: ")
    start = time.time()
    print("\n",best_first_search(start_article, end_article))
    end = time.time()
    print("That took",end-start,"seconds")

    start = time.time()
    sys.stdout.write("Processing Closest Page: ")
    start = time.time()
    print("\n",solve_wiki_game(start_article, end_article, depth, path_taken))
    end = time.time()
    print("That took",end-start,"seconds")

    # sys.stdout.write("Processing Greedy Search: ")
    # print("\n",greedy_search(start_article.lower(), end_article.lower()))
