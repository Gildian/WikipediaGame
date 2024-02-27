import heapq
from helpers import get_closest_links,get_closest_link, spinner, DEBUG_MODE #, get_closest_links_greedy
import sys
from wikiapi import getPageDetails

# def greedy_search(start_page, goal_page):
#     queue = []
#     heapq.heappush(queue, (0, [start_page]))  # priority queue to store the pages to be explored
#     visited = set()  # set to store the visited pages
#     while queue:
#         sys.stdout.write('\b')
#         sys.stdout.write(next(spinner))
#         sys.stdout.flush()  # code to add a spinner to the console so the user can tell its working
#         _, current_page_list = heapq.heappop(queue)  # get the page with the highest priority
#         current_page = current_page_list[-1][0].lower()  # extract the string from the tuple and convert to lowercase
#         if current_page == goal_page.lower():  # if the current page is the goal page, return the path
#             return current_page_list
#         if current_page not in visited:  # if the current page has not been visited
#             visited.add(current_page)  # mark the current page as visited
#             closest_link = get_closest_links_greedy(current_page, goal_page, current_page_list)  # find the next best page
#             new_list = current_page_list.copy()
#             new_list.append(closest_link[0])
#             heapq.heappush(queue, (closest_link[1], new_list))  # add the next page to the priority queue
#             visited.add(closest_link[0][0].lower())  # mark the next page as visited
#     print("QUEUE EMPTY WITHOUT SOLUTION")
#     exit()

def best_first_search(start_page, goal_page, beam_width=3):
    queue = []
    heapq.heappush(queue, (0, [start_page]))  # priority queue to store the pages to be explored
    visited = set()  # set to store the visited pages
    while len(queue) != 0:
        if DEBUG_MODE: print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        sys.stdout.write('\b')
        sys.stdout.write(next(spinner))
        sys.stdout.flush()  # code to add a spinner to the console so the user can tell its working
        current_pages = heapq.heappop(queue)  # get the pages with the highest priority
        score, current_page_list = current_pages
        page_details = getPageDetails(current_page_list[-1])
        current_page_list[-1] = page_details["title"]
        if page_details["title"].lower() == goal_page.lower():  # if the current page is the goal page, return the path
            return current_page_list
        current_page = page_details["title"]
        if current_page not in visited:  # if the current page has not been visited
            visited.add(current_page)  # mark the current page as visited
            closest_links = get_closest_links(current_page, goal_page, current_page_list)  # find the next best page
            for links in closest_links:
                new_score = score - links[1]
                new_list = current_page_list.copy()
                new_list.append(links[0])
                new_score = new_score / len(new_list)
                if DEBUG_MODE: print(new_score,new_list)
                if new_score < 0:
                    heapq.heappush(queue, (new_score, new_list))  # add the next page to the priority queue
    print("QUEUE EMPTY WITHOUT SOLUTION")
    exit()

def solve_wiki_game(current_page, end_page, depth, path_taken): # recursive function for solving the game, it is what is called to get the search started
    sys.stdout.write('\b')
    sys.stdout.write(next(spinner))
    sys.stdout.flush()  # code to add a spinner to the console so the user can tell its working
    if depth < 0:   # base case for if over the set depth amount of paths has been traversed, meaning a solution was not found
        print("DEPTH REACHED 0")
        return path_taken
    if current_page.lower() == end_page.lower():    # base case for if the current page is our goal page
        return path_taken
    closest_link = get_closest_link(current_page, end_page, path_taken) # finds the next best page using the above function
    path_taken.append(closest_link[0])  # updates the path taken with the new best page
    if DEBUG_MODE: print("current path:",path_taken)
    depth -= 1  # counts down the depth so program doesnt run forever
    if closest_link[0].lower() == end_page.lower(): # case for if the closest link is our solution to the game
        return path_taken
    else:
        return solve_wiki_game(closest_link[0], end_page, depth, path_taken)    # recursive call to check the next level for a result