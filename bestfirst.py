import heapq
from helpers import get_closest_links, spinner, DEBUG_MODE
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