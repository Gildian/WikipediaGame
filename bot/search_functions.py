#!/usr/bin/env python3
"""
Wikipedia Path Finder - Search Algorithms

This module implements two graph search algorithms for finding paths between
Wikipedia articles using semantic similarity as a heuristic.

Author: Gildian Gonzales
License: MIT
"""

import heapq
import sys
import time
from typing import List, Union, Optional
from helpers import get_closest_links, get_closest_link, spinner, DEBUG_MODE
from wikiapi import getPageDetails

# Configuration
TIME_LIMIT = 120  # Maximum search time in seconds
MAX_QUEUE_SIZE = 10000  # Maximum priority queue size to prevent memory issues


def best_first_search(start_page: str, goal_page: str, start_time: float) -> Union[List[str], str]:
    """
    Best-First Search algorithm using semantic similarity as heuristic.
    
    This algorithm uses a priority queue to explore the most promising paths first,
    often finding shorter solutions at the cost of longer execution time.
    
    Args:
        start_page: Starting Wikipedia article title
        goal_page: Target Wikipedia article title  
        start_time: Search start timestamp for timeout handling
        
    Returns:
        List of article titles forming the path, or "NO SOLUTION" if failed
    """
    # Priority queue: (negative_score, path_list)
    # Negative score because heapq is a min-heap, but we want max similarity
    queue = []
    heapq.heappush(queue, (0, [start_page]))
    
    visited = set()  # Track explored articles to avoid cycles
    iterations = 0
    
    if DEBUG_MODE:
        print(f"🚀 Starting Best-First Search: '{start_page}' → '{goal_page}'")
    
    while queue:
        # Check timeout
        if time.time() - start_time >= TIME_LIMIT:
            print(f"\n⏰ Time limit exceeded! Best-First Search could not find solution within {TIME_LIMIT} seconds")
            return "NO SOLUTION"
        
        # Check queue size to prevent memory issues
        if len(queue) > MAX_QUEUE_SIZE:
            print(f"\n🔴 Queue size exceeded limit ({MAX_QUEUE_SIZE}). Terminating search.")
            return "NO SOLUTION"
        
        # Progress indicator
        iterations += 1
        if iterations % 50 == 0:  # Less frequent updates for performance
            sys.stdout.write('\b')
            sys.stdout.write(next(spinner))
            sys.stdout.flush()
        
        # Get highest priority path
        current_score, current_path = heapq.heappop(queue)
        current_page_title = current_path[-1]
        
        # Validate current page exists
        page_details = getPageDetails(current_page_title)
        if not page_details["exists"]:
            continue
            
        # Update path with canonical title
        current_path[-1] = page_details["title"]
        current_page = page_details["title"]
        
        # Check if we reached the goal
        if current_page.lower() == goal_page.lower():
            if DEBUG_MODE:
                print(f"\n🎉 Goal reached! Path length: {len(current_path)}")
            return current_path
        
        # Skip if already visited (cycle detection)
        if current_page in visited:
            continue
            
        visited.add(current_page)
        
        if DEBUG_MODE:
            print(f"\n📍 Exploring: {current_page} (visited: {len(visited)})")
            print(f"🔄 Current path: {' → '.join(current_path)}")
        
        try:
            # Get all promising links from current page
            closest_links = get_closest_links(current_page, goal_page.lower(), current_path)
            
            # Add each promising link to the queue
            for link_title, link_score in closest_links:
                new_path = current_path.copy()
                new_path.append(link_title)
                
                # Calculate priority: negative of (score / path_length) for balanced exploration
                new_priority = -link_score / len(new_path)
                
                heapq.heappush(queue, (new_priority, new_path))
                
                if DEBUG_MODE and link_score > 0.3:
                    print(f"  ➕ Queued: {link_title} (score: {link_score:.3f}, priority: {new_priority:.3f})")
        
        except Exception as e:
            if DEBUG_MODE:
                print(f"⚠️  Error exploring {current_page}: {e}")
            continue
    
    print(f"\n❌ No solution found. Explored {len(visited)} articles.")
    return "NO SOLUTION"


def depth_first_search(
    current_page: str, 
    end_page: str, 
    path_taken: List[str], 
    start_time: float
) -> Union[List[str], str]:
    """
    Depth-First Search algorithm with greedy best-link selection.
    
    This recursive algorithm always chooses the most semantically similar next link,
    leading to fast execution but potentially suboptimal paths.
    
    Args:
        current_page: Current Wikipedia article title
        end_page: Target Wikipedia article title
        path_taken: List of articles visited so far
        start_time: Search start timestamp for timeout handling
        
    Returns:
        List of article titles forming the path, or "NO SOLUTION" if failed
    """
    # Check timeout
    if time.time() - start_time >= TIME_LIMIT:
        print(f"\n⏰ Time limit exceeded! Depth-First Search could not find solution within {TIME_LIMIT} seconds")
        return "NO SOLUTION"
    
    # Check maximum path length to prevent infinite recursion
    if len(path_taken) > 50:  # Reasonable maximum path length
        if DEBUG_MODE:
            print(f"⚠️  Maximum path length reached: {len(path_taken)}")
        return "NO SOLUTION"
    
    # Progress indicator
    sys.stdout.write('\b')
    sys.stdout.write(next(spinner))
    sys.stdout.flush()
    
    # Base case: reached the goal
    if current_page.lower() == end_page.lower():
        if DEBUG_MODE:
            print(f"\n🎉 Goal reached! Final path: {' → '.join(path_taken)}")
        return path_taken
    
    if DEBUG_MODE:
        print(f"\n📍 Current: {current_page} (depth: {len(path_taken)})")
    
    try:
        # Find the best next link
        closest_link_title, closest_link_score = get_closest_link(
            current_page, end_page.lower(), path_taken
        )
        
        # Add the best link to our path
        path_taken.append(closest_link_title)
        
        if DEBUG_MODE:
            print(f"  ➡️  Next: {closest_link_title} (score: {closest_link_score:.3f})")
            print(f"  🛤️  Path: {' → '.join(path_taken)}")
        
        # Check if we found the goal
        if closest_link_title.lower() == end_page.lower():
            if DEBUG_MODE:
                print(f"🎉 Goal found! Path length: {len(path_taken)}")
            return path_taken
        
        # Recursive search from the new page
        return depth_first_search(closest_link_title, end_page, path_taken, start_time)
        
    except Exception as e:
        if DEBUG_MODE:
            print(f"⚠️  Error in depth-first search from {current_page}: {e}")
        return "NO SOLUTION"


# Algorithm metadata for reporting
ALGORITHM_INFO = {
    "best_first_search": {
        "name": "Best-First Search",
        "description": "Uses priority queue to explore most promising paths first",
        "advantages": ["Often finds shorter paths", "Systematic exploration"],
        "disadvantages": ["Higher memory usage", "Longer execution time"]
    },
    "depth_first_search": {
        "name": "Depth-First Search", 
        "description": "Greedily selects best next link at each step",
        "advantages": ["Fast execution", "Low memory usage"],
        "disadvantages": ["May find suboptimal paths", "Can get stuck in local maxima"]
    }
}


def get_algorithm_info(algorithm_name: str) -> dict:
    """Get metadata about a search algorithm."""
    return ALGORITHM_INFO.get(algorithm_name, {})


if DEBUG_MODE:
    print("🔍 Search algorithms loaded:")
    for name, info in ALGORITHM_INFO.items():
        print(f"  • {info['name']}: {info['description']}")