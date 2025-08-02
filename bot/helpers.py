#!/usr/bin/env python3
"""
Wikipedia Path Finder - Helper Functions

This module contains utility functions for article processing, semantic analysis,
and pathfinding logic using GloVe word embeddings.

Author: Gildian Gonzales
License: MIT
"""

import torch
import re
from typing import Set, Tuple, Dict, Any, Optional, List
from glove_loader import create_embeddings
from wikiapi import getAllValidLinks, getPageDetails

# Global state
cosine_dict: Dict[str, float] = {}
goal_vector_data: Dict[str, torch.Tensor] = {}

# Configuration
DEBUG_MODE = False  # Set to True for debug output
SIMILARITY_THRESHOLD = 0.0  # Range: [-1, 1), set to -1 to allow all articles

# Blacklisted page types to avoid during search
BLACKLIST_WORDS = [
    "wikipedia:", "template:", "category:", "template talk:", 
    "(disambiguation)", "user:", "talk:", "(identifier)",
    "file:", "help:", "portal:", "special:"
]

# Initialize GloVe embeddings
print("🧠 Loading GloVe word embeddings...")
glove = create_embeddings()

# Regex pattern for cleaning article titles
title_pattern = re.compile(r'[()\"]+')


def spinning_cursor():
    """Generator for terminal spinner animation."""
    while True:
        for cursor in '|/-\\':
            yield cursor


spinner = spinning_cursor()


def process_wiki_article(name: str) -> str:
    """
    Process and validate a Wikipedia article name.
    
    Args:
        name: Raw article name from user input
        
    Returns:
        Cleaned and validated article title
        
    Raises:
        SystemExit: If article doesn't exist or is invalid
    """
    article = getPageDetails(name)
    
    if not article["exists"]:
        print(f"❌ Article '{name}' doesn't exist!")
        exit(1)
    
    # Check if it's a disambiguation page
    for category in article["categories"]:
        if "Category:Disambiguation pages" == category["title"]:
            print(f"❌ Cannot use disambiguation page: '{name}'!")
            exit(1)
    
    if DEBUG_MODE:
        print(f"✅ Validated article: {article['title']}")
        
    return article["title"]


def get_user_input(prompt: str) -> str:
    """
    Get and process user input for article names.
    
    Args:
        prompt: Input prompt to display
        
    Returns:
        Processed and validated article title
    """
    user_input = input(f"{prompt} ")
    return process_wiki_article(user_input)


def pre_compute_goal(goal: str) -> None:
    """
    Pre-compute word embeddings for the target article to optimize search.
    
    Args:
        goal: Target article title
    """
    global goal_vector_data
    
    if DEBUG_MODE:
        print(f"🎯 Pre-computing embeddings for goal: '{goal}'")
    
    # Clean the goal title
    goal_clean = title_pattern.sub(" ", goal)
    goal_words = set(word for word in goal_clean.lower().split() if word in glove)
    
    if not goal_words:
        print(f"⚠️  Warning: No embeddings found for goal '{goal}'")
        goal_vector_data = {"vectors": [], "mean": torch.zeros(300)}
        return
    
    # Get embeddings for each word
    goal_vectors = [glove[word].unsqueeze(0) for word in goal_words]
    goal_mean = torch.mean(torch.vstack(goal_vectors), dim=0)
    
    goal_vector_data = {
        "vectors": goal_vectors,
        "mean": goal_mean
    }
    
    if DEBUG_MODE:
        print(f"✅ Pre-computed {len(goal_vectors)} word vectors")


def get_word_score(unit: str) -> float:
    """
    Calculate semantic similarity score between an article and the goal.
    
    Uses cosine similarity between GloVe word embeddings to determine
    how semantically related an article is to the target article.
    
    Args:
        unit: Article title to score
        
    Returns:
        Similarity score between -1 and 1 (higher is more similar)
    """
    global cosine_dict
    
    # Return cached score if available
    if unit in cosine_dict:
        return cosine_dict[unit]
    
    # Clean the article title
    unit_clean = title_pattern.sub(" ", unit)
    unit_words = set(word for word in unit_clean.lower().split() if word in glove)
    
    if not unit_words:
        cosine_dict[unit] = -1.0
        return -1.0
    
    # Get embeddings for each word
    unit_vectors = [glove[word].unsqueeze(0) for word in unit_words]
    
    # Calculate individual word similarities
    scores = set()
    for unit_vector in unit_vectors:
        for target_vector in goal_vector_data["vectors"]:
            score = torch.nn.functional.cosine_similarity(unit_vector, target_vector)
            # Prevent perfect matches (which indicate same word)
            scores.add(0.75 if score == 1.0 else float(score))
    
    # Calculate similarity between mean vectors
    unit_mean = torch.mean(torch.vstack(unit_vectors), dim=0)
    combined_score = torch.nn.functional.cosine_similarity(
        unit_mean.unsqueeze(0), 
        goal_vector_data["mean"].unsqueeze(0)
    )
    
    # Take the best score from individual words or combined meaning
    best_score = max(max(scores, default=-1), float(combined_score))
    
    # Cache the result
    cosine_dict[unit] = best_score
    
    if DEBUG_MODE and best_score > 0.5:
        print(f"🎯 High similarity: '{unit}' -> {best_score:.3f}")
    
    return best_score


def get_closest_links(page: str, goal_page: str, path_taken: List[str]) -> Set[Tuple[str, float]]:
    """
    Find all promising links from the current page for best-first search.
    
    Args:
        page: Current Wikipedia page
        goal_page: Target page (lowercased)
        path_taken: List of pages already visited
        
    Returns:
        Set of (link_title, similarity_score) tuples above threshold
    """
    links = getAllValidLinks(page)
    best_links = set()
    
    if DEBUG_MODE:
        print(f"🔍 Analyzing {len(links)} links from '{page}'")
    
    for link in links:
        link_name = link.lower()
        
        # Check if this is the goal
        if link_name == goal_page:
            best_links.add((link, 1.0))
            if DEBUG_MODE:
                print(f"🎉 Found goal: '{link}'")
            break
        
        # Skip blacklisted or already visited pages
        if (any(blword in link_name for blword in BLACKLIST_WORDS) or 
            link in path_taken):
            continue
        
        # Calculate similarity score
        link_score = get_word_score(link_name)
        if link_score > SIMILARITY_THRESHOLD:
            best_links.add((link, link_score))
            if DEBUG_MODE and link_score > 0.3:
                print(f"  📎 Promising link: '{link}' ({link_score:.3f})")
    
    if len(best_links) == 0:
        print(f"❌ No valid links found from '{page}'")
        exit(1)
    
    if DEBUG_MODE:
        print(f"✅ Found {len(best_links)} promising links")
    
    return best_links


def get_closest_link(page: str, goal_page: str, path_taken: List[str]) -> Tuple[str, float]:
    """
    Find the single best link from the current page for depth-first search.
    
    Args:
        page: Current Wikipedia page
        goal_page: Target page (lowercased)  
        path_taken: List of pages already visited
        
    Returns:
        Tuple of (best_link_title, similarity_score)
    """
    links = getAllValidLinks(page)
    closest_match = ["", -1.0]
    
    if DEBUG_MODE:
        print(f"🔍 Finding best link from '{page}' among {len(links)} options")
    
    for link in links:
        link_name = link.lower()
        
        # Check if this is the goal
        if link_name == goal_page:
            closest_match = [link, 1.0]
            if DEBUG_MODE:
                print(f"🎉 Found goal: '{link}'")
            break
        
        # Skip blacklisted pages
        if any(blword in link_name for blword in BLACKLIST_WORDS):
            continue
            
        # Skip already visited pages or current page
        if link in path_taken or link_name == page.lower():
            continue
        
        # Calculate similarity and update best match
        link_score = get_word_score(link_name)
        if closest_match[1] < link_score:
            # Verify the page exists
            closest_page = getPageDetails(link)
            if closest_page["exists"] and closest_page["title"] not in path_taken:
                closest_match = [closest_page["title"], link_score]
                if DEBUG_MODE:
                    print(f"  🎯 New best: '{closest_page['title']}' ({link_score:.3f})")
    
    if DEBUG_MODE:
        print(f"✅ Selected: '{closest_match[0]}' with score {closest_match[1]:.3f}")
    
    if closest_match[0] == "":
        print(f"❌ No valid next page found from '{page}'")
        exit(1)
    
    return tuple(closest_match)


# Module initialization
if DEBUG_MODE:
    print("🔧 Helper functions initialized")
    print(f"📊 Similarity threshold: {SIMILARITY_THRESHOLD}")
    print(f"🚫 Blacklisted patterns: {len(BLACKLIST_WORDS)}")