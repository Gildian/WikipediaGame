import sys 
from search_functions import best_first_search, depth_first_search
from helpers import get_user_input, process_wiki_article, validateWord
from wikiapi import getTwoRandomPages
import time

if __name__ == "__main__":
    start_article = ""
    end_article = ""

    if len(sys.argv) == 2 and sys.argv[1] == "random":
        # get two random articles
        pages = getTwoRandomPages()
        start_article = pages[0]["title"]
        end_article = pages[1]["title"]
    elif len(sys.argv) == 3:
        start_article = process_wiki_article(sys.argv[1])
        end_article = process_wiki_article(sys.argv[2])
    else:
        # get start article
        start_article = get_user_input("Enter the starting article:")
        # get end article
        end_article = get_user_input("Enter the ending article:")
    
    if not validateWord(end_article):
        print("End Article not present in GloVe vectors! Solution impossible to find!")
        exit()
    
    print(f"Finding a path from {start_article} to {end_article}")

    # Best First Search
    start = time.time()
    sys.stdout.write("Processing Best First Search: ")
    start = time.time()
    result = best_first_search(start_article, end_article, start)
    print("\n",result)
    end = time.time()
    if result != "NO SOLUTION":
        print("That took",round(end-start),"seconds and found a solution",len(result),"articles long")

    # Depth First Search
    start = time.time()
    sys.stdout.write("Processing Depth First Search: ")
    start = time.time()
    path_taken = [start_article]
    result = depth_first_search(start_article, end_article, path_taken, start)
    print("\n",result)
    end = time.time()
    if result != "NO SOLUTION":
        print("That took",round(end-start),"seconds and found a solution",len(result),"articles long")