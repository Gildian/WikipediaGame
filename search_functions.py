import heapq
from helpers import get_closest_links,get_closest_link, spinner, DEBUG_MODE
import sys

def best_first_search(start_page, goal_page):
    queue = []
    heapq.heappush(queue, (0, [start_page]))  # priority queue to store the pages to be explored
    visited = set()  # set to store the visited pages
    while queue:
        if DEBUG_MODE: print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        sys.stdout.write('\b')
        sys.stdout.write(next(spinner))
        sys.stdout.flush()  # code to add a spinner to the console so the user can tell its working
        score, current_page_list = heapq.heappop(queue)  # get the page with the highest priority
        if current_page_list[-1].lower() == goal_page.lower():  # if the current page is the goal page, return the path
            return current_page_list
        if current_page_list[-1].lower() not in visited:  # if the current page has not been visited
            visited.add(current_page_list[-1].lower())  # mark the current page as visited
            closest_links = get_closest_links(current_page_list[-1], goal_page, current_page_list)  # find the next best page
            for links in closest_links:
                new_score = score + -links[1]
                new_list = current_page_list.copy()
                new_list.append(links[0])
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