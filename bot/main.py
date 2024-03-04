import sys 
from search_functions import best_first_search, depth_first_search
from helpers import get_user_input, process_wiki_article, validateWord
from wikiapi import getTwoRandomPages
import time

def get_articles():
    if len(sys.argv) == 2 and sys.argv[1] == "random":
        pages = getTwoRandomPages()
        start_article = pages[0]["title"]
        end_article = pages[1]["title"]
    elif len(sys.argv) == 3:
        start_article = process_wiki_article(sys.argv[1])
        end_article = process_wiki_article(sys.argv[2])
    else:
        start_article = get_user_input("Enter the starting article:")
        end_article = get_user_input("Enter the ending article:")
    return start_article, end_article

def perform_search(search_function, start_article, end_article, file):
    print(f"Finding a path from {start_article} to {end_article}")
    start_time = time.time()
    sys.stdout.write(f"Processing {search_function.__name__}: ")
    path_taken = [start_article]
    if search_function == best_first_search:
        search_result = search_function(start_article, end_article, start_time)
    else:
        search_result = search_function(start_article, end_article, path_taken, start_time)
    print("\n", search_result)
    end_time = time.time()
    if search_result != "NO SOLUTION":
        print("That took", round(end_time - start_time), "seconds and found a solution", len(search_result), "articles long")

    file.write(f"{search_function.__name__}: ")
    file.write(str(search_result))
    file.write(f"\n That took {round(end_time - start_time)} seconds and found a solution {len(search_result)} articles long")
    file.write("\n\n")

if __name__ == "__main__":
    start_article, end_article = get_articles()

    if not validateWord(end_article):
        print("End Article not present in GloVe vectors! Solution impossible to find!")
        exit()

    with open("path.txt", "w") as file:
        file.write(f"Start Article: {start_article}\nEnd Article: {end_article}\n\n")
        
        # perform_search(best_first_search, start_article, end_article, file)
        perform_search(depth_first_search, start_article, end_article, file)
