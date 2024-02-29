import heapq
from helpers import get_closest_links,get_closest_link, spinner, DEBUG_MODE
import sys
from wikiapi import getPageDetails
import time

# Best first uses a queue to store the current best path, and will keep switching to the best option if the current path becomes worse
# This usually finds a short path at the cost of taking longer
def best_first_search(start_page, goal_page, start_time):
    queue = []
    heapq.heappush(queue, (0, [start_page]))  # priority queue to store the pages to be explored
    visited = set()  # set to store the visited pages
    while len(queue) != 0:
        if DEBUG_MODE: print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        if time.time() - start_time >= 120:
            print("Time limit exceeded! Best First could not find solution within 120 seconds")
            return "NO SOLUTION"
        sys.stdout.write('\b')
        sys.stdout.write(next(spinner))
        sys.stdout.flush()  # code to add a spinner to the console so the user can tell its working
        current_pages = heapq.heappop(queue)  # get the pages with the highest priority
        score, current_page_list = current_pages
        page_details = getPageDetails(current_page_list[-1])
        if page_details["exists"]:
            current_page_list[-1] = page_details["title"]
            if page_details["title"].lower() == goal_page.lower():  # if the current page is the goal page, return the path
                return current_page_list
            current_page = page_details["title"]
            if current_page not in visited:  # if the current page has not been visited
                if DEBUG_MODE: print("current list:",current_page_list)
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

# Depth first searches the page for the best link and follows it. Depth first does not back track, and will keep going until it finds a solution or runs out of pages.
# Depth first usually finds a path quickly, but it will not always be the shortest
def depth_first_search(current_page, end_page, path_taken, start_time): # recursive function for solving the game, it is what is called to get the search started
    if time.time() - start_time >= 120:
            print("Time limit exceeded! Best First could not find solution within 120 seconds")
            return "NO SOLUTION"
    sys.stdout.write('\b')
    sys.stdout.write(next(spinner))
    sys.stdout.flush()  # code to add a spinner to the console so the user can tell its working
    if current_page.lower() == end_page.lower():    # base case for if the current page is our goal page
        return path_taken
    closest_link = get_closest_link(current_page, end_page, path_taken) # finds the next best page using the above function
    path_taken.append(closest_link[0])  # updates the path taken with the new best page
    if DEBUG_MODE: print("current path:",path_taken)
    if closest_link[0].lower() == end_page.lower(): # case for if the closest link is our solution to the game
        return path_taken
    else:
        return depth_first_search(closest_link[0], end_page, path_taken, start_time)    # recursive call to check the next level for a result