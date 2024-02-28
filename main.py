import sys 
from search_functions import best_first_search, depth_first_search # , greedy_search
from helpers import get_user_input, process_wiki_article
import time

if __name__ == "__main__":
    start_article = ""
    end_article = ""
    if len(sys.argv) == 3:
        start_article = process_wiki_article(sys.argv[1])
        end_article = process_wiki_article(sys.argv[2])
    else:
        # get start article
        start_article = get_user_input("Enter the starting article:")
        # get end article
        end_article = get_user_input("Enter the ending article:")

    depth = 100
    print(f"Finding a path from {start_article} to {end_article}")
    path_taken = [start_article]

    # Uncomment the algo you want to use
    start = time.time()
    sys.stdout.write("Processing Best First Search: ")
    start = time.time()
    result = best_first_search(start_article, end_article)
    print("\n",result)
    end = time.time()
    print("That took",round(end-start),"seconds and found a solution",len(result),"articles long")

    start = time.time()
    sys.stdout.write("Processing Depth First Search: ")
    start = time.time()
    result = depth_first_search(start_article, end_article, depth, path_taken)
    print("\n",result)
    end = time.time()
    print("That took",round(end-start),"seconds and found a solution",len(result),"articles long")

    # sys.stdout.write("Processing Greedy Search: ")
    # print("\n",greedy_search(start_article.lower(), end_article.lower()))
