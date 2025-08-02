#!/usr/bin/env python3
"""
Wikipedia Path Finder - Main Application

A sophisticated bot that finds the shortest path between two Wikipedia articles
using advanced NLP techniques and graph search algorithms.

Author: Gildian Gonzales
License: MIT
"""

import sys
import time
import json
import argparse
from pathlib import Path
from typing import Tuple, Dict, Any, Optional

# Local imports
from search_functions import best_first_search, depth_first_search
from helpers import get_user_input, process_wiki_article, pre_compute_goal
from wikiapi import getTwoRandomPages

# Configuration
OUTPUT_FILE = "path.json"
DEFAULT_ARTICLES = {
    "start": "minecraft",
    "end": "pizza"
}


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Find the shortest path between Wikipedia articles",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Interactive mode
  %(prog)s random                   # Random articles
  %(prog)s "Python" "Machine Learning"  # Specific articles
  %(prog)s client random best_first_search  # Client mode
        """
    )
    
    parser.add_argument(
        "start_article", 
        nargs="?", 
        help="Starting Wikipedia article (or 'random' for random selection)"
    )
    parser.add_argument(
        "end_article", 
        nargs="?", 
        help="Target Wikipedia article"
    )
    parser.add_argument(
        "algorithm", 
        nargs="?", 
        choices=["best_first_search", "depth_first_search", "both_algo"],
        default="both_algo",
        help="Search algorithm to use (default: both_algo)"
    )
    parser.add_argument(
        "--client", 
        action="store_true",
        help="Run in client mode for web interface"
    )
    parser.add_argument(
        "--output", 
        default=OUTPUT_FILE,
        help=f"Output JSON file (default: {OUTPUT_FILE})"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    return parser.parse_args()


def get_articles_from_args(args: argparse.Namespace) -> Tuple[str, str]:
    """
    Get start and end articles based on command line arguments.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Tuple of (start_article, end_article)
    """
    # Handle client mode
    if args.client:
        if args.start_article == "random":
            pages = getTwoRandomPages()
            # Use default articles for demo, or use random pages
            start_article = DEFAULT_ARTICLES["start"]  # pages[0]["title"]
            end_article = DEFAULT_ARTICLES["end"]      # pages[1]["title"]
        else:
            start_article = process_wiki_article(args.start_article)
            end_article = process_wiki_article(args.end_article)
        return start_article, end_article
    
    # Handle standard mode
    if args.start_article == "random":
        pages = getTwoRandomPages()
        start_article = pages[0]["title"]
        end_article = pages[1]["title"]
    elif args.start_article and args.end_article:
        start_article = process_wiki_article(args.start_article)
        end_article = process_wiki_article(args.end_article)
    else:
        # Interactive mode
        start_article = get_user_input("Enter the starting article:")
        end_article = get_user_input("Enter the ending article:")
    
    return start_article, end_article


def perform_search(
    search_function, 
    start_article: str, 
    end_article: str,
    verbose: bool = False
) -> Dict[str, Any]:
    """
    Execute a search algorithm and return results.
    
    Args:
        search_function: The search algorithm function to use
        start_article: Starting Wikipedia article
        end_article: Target Wikipedia article
        verbose: Whether to print verbose output
        
    Returns:
        Dictionary containing search results
    """
    if verbose:
        print(f"🔍 Finding path from '{start_article}' to '{end_article}'")
        
    start_time = time.time()
    
    if verbose:
        print(f"⚙️  Running {search_function.__name__.replace('_', ' ').title()}...")
    
    sys.stdout.write(f"Processing {search_function.__name__}: ")
    path_taken = [start_article]
    
    try:
        if search_function == best_first_search:
            search_result = search_function(start_article, end_article, start_time)
        else:
            search_result = search_function(start_article, end_article, path_taken, start_time)
        
        end_time = time.time()
        duration = round(end_time - start_time)
        
        if verbose:
            print(f"\n✅ Result: {search_result}")
        
        if search_result != "NO SOLUTION":
            if verbose:
                print(f"⏱️  Duration: {duration} seconds")
                print(f"📏 Path length: {len(search_result)} articles")
        else:
            if verbose:
                print("❌ No solution found")
        
        return {
            "algo": search_function.__name__,
            "path": str(search_result),
            "time": duration,
            "length": len(search_result) if search_result != "NO SOLUTION" else -1,
            "success": search_result != "NO SOLUTION"
        }
        
    except Exception as e:
        print(f"\n❌ Error during search: {e}")
        return {
            "algo": search_function.__name__,
            "path": "ERROR",
            "time": 0,
            "length": -1,
            "success": False,
            "error": str(e)
        }


def save_results(
    start_article: str, 
    end_article: str, 
    results: list, 
    output_file: str = OUTPUT_FILE
) -> None:
    """
    Save search results to JSON file.
    
    Args:
        start_article: Starting article
        end_article: Target article  
        results: List of search results
        output_file: Output file path
    """
    output_data = {
        "start": start_article,
        "end": end_article,
        "timestamp": time.time(),
        "results": results
    }
    
    try:
        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(output_data, file, indent=2, ensure_ascii=False)
        print(f"💾 Results saved to {output_file}")
    except Exception as e:
        print(f"❌ Error saving results: {e}")


def main() -> None:
    """Main application entry point."""
    try:
        args = parse_arguments()
        
        # Get articles
        start_article, end_article = get_articles_from_args(args)
        
        # Pre-compute goal embeddings for efficiency
        print("🧠 Pre-computing semantic embeddings...")
        pre_compute_goal(end_article)
        
        # Determine which algorithms to run
        algorithms_to_run = []
        if args.algorithm == "both_algo" and not args.client:
            algorithms_to_run = [best_first_search, depth_first_search]
        elif args.algorithm == "best_first_search":
            algorithms_to_run = [best_first_search]
        elif args.algorithm == "depth_first_search":
            algorithms_to_run = [depth_first_search]
        else:
            algorithms_to_run = [best_first_search, depth_first_search]
        
        # Run searches
        results = []
        for algorithm in algorithms_to_run:
            result = perform_search(algorithm, start_article, end_article, args.verbose)
            results.append(result)
        
        # Save results
        save_results(start_article, end_article, results, args.output)
        
        # Print summary
        if args.verbose and len(results) > 1:
            print("\n📊 Summary:")
            for result in results:
                status = "✅" if result["success"] else "❌"
                print(f"  {status} {result['algo']}: {result['length']} steps, {result['time']}s")
        
    except KeyboardInterrupt:
        print("\n\n🛑 Search interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()