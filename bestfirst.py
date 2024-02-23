import heapq
from helpers import get_closest_link

def best_first_search(start_page, goal_page, path_taken):
    queue = []
    heapq.heappush(queue, (0, start_page))  # priority queue to store the pages to be explored
    visited = set()  # set to store the visited pages
    while queue:
        _, current_page = heapq.heappop(queue)  # get the page with the highest priority
        if current_page.lower() == goal_page.lower():  # if the current page is the goal page, return the path
            return path_taken
        if current_page.lower() not in visited:  # if the current page has not been visited
            visited.add(current_page.lower())  # mark the current page as visited
            closest_link = get_closest_link(current_page, goal_page)  # find the next best page
            path_taken.append(closest_link[0])  # update the path taken
            heapq.heappush(queue, (closest_link[1], closest_link[0]))  # add the next page to the priority queue
    return None  # if no path is found