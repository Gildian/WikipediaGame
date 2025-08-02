#!/usr/bin/env python3
"""
Wikipedia API Interface

This module provides a clean interface to the Wikipedia API for retrieving
article information, links, and content needed for pathfinding.

Author: Gildian Gonzales
License: MIT
"""

import logging
import requests
from urllib.parse import unquote
from bs4 import BeautifulSoup
import concurrent.futures
from typing import Dict, List, Set, Any, Optional
import time

# Configuration
DEBUG_MODE = False
API_URL = "https://en.wikipedia.org/w/api.php"
REQUEST_TIMEOUT = 30  # seconds
MAX_WORKERS = 10  # For concurrent requests
RETRY_ATTEMPTS = 3
RETRY_DELAY = 1  # seconds

# Sections to skip when extracting links
BLACKLISTED_SECTIONS = [
    "References", "External links", "Further reading", 
    "See also", "Notes", "Bibliography", "Sources"
]

# Set up logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Create a session for connection pooling
session = requests.Session()
session.headers.update({
    'User-Agent': 'WikipediaPathFinder/1.0 (Educational Project; Contact: github.com/Gildian)'
})


def make_request(params: Dict[str, Any], retries: int = RETRY_ATTEMPTS) -> Optional[Dict[str, Any]]:
    """
    Make a request to the Wikipedia API with error handling and retries.
    
    Args:
        params: API parameters dictionary
        retries: Number of retry attempts
        
    Returns:
        JSON response data or None if failed
    """
    for attempt in range(retries):
        try:
            response = session.get(
                url=API_URL, 
                params=params, 
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Check for API errors
            if 'error' in data:
                logger.error(f"API error: {data['error']}")
                return None
                
            return data
            
        except requests.exceptions.Timeout:
            logger.warning(f"Request timeout (attempt {attempt + 1}/{retries})")
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
        except ValueError as e:
            logger.error(f"JSON decode error: {e}")
        
        if attempt < retries - 1:
            time.sleep(RETRY_DELAY * (attempt + 1))  # Exponential backoff
    
    logger.error(f"Failed to make request after {retries} attempts")
    return None


def getTwoRandomPages() -> List[Dict[str, str]]:
    """
    Get two random Wikipedia articles.
    
    Returns:
        List of dictionaries containing article information
    """
    params = {
        "action": "query",
        "format": "json", 
        "list": "random",
        "rnlimit": "2",
        "rnnamespace": "0"  # Main namespace only
    }
    
    data = make_request(params)
    if data and "query" in data and "random" in data["query"]:
        random_pages = data["query"]["random"]
        if DEBUG_MODE:
            print(f"🎲 Random pages: {[p['title'] for p in random_pages]}")
        return random_pages
    
    # Fallback if API fails
    logger.warning("Random page API failed, using fallback")
    return [
        {"title": "Python (programming language)"},
        {"title": "Machine learning"}
    ]


def getPageDetails(page: str) -> Dict[str, Any]:
    """
    Get detailed information about a Wikipedia page.
    
    Args:
        page: Article title
        
    Returns:
        Dictionary containing page existence, title, and categories
    """
    page = unquote(page)
    
    params = {
        "action": "query",
        "titles": page,
        "format": "json",
        "indexpageids": "",
        "prop": "categories",
        "cllimit": "max",
        "redirects": "",
        "clshow": "!hidden"  # Exclude hidden categories
    }
    
    if DEBUG_MODE:
        print(f"🔍 Getting details for: '{page}'")
    
    data = make_request(params)
    if not data:
        return {"exists": False, "title": page, "categories": []}
    
    clean_data = {}
    page_ids = data["query"]["pageids"]
    
    # Check if page exists
    clean_data["exists"] = page_ids[0] != '-1'
    
    if clean_data["exists"]:
        page_data = data["query"]["pages"][page_ids[0]]
        clean_data["title"] = page_data["title"]
        clean_data["categories"] = page_data.get("categories", [])
        
        if DEBUG_MODE:
            print(f"✅ Page exists: '{clean_data['title']}'")
            print(f"📁 Categories: {len(clean_data['categories'])}")
    else:
        clean_data["title"] = page
        clean_data["categories"] = []
        if DEBUG_MODE:
            print(f"❌ Page not found: '{page}'")
    
    return clean_data


def getAllSections(page: str) -> List[Dict[str, Any]]:
    """
    Get all sections of a Wikipedia page.
    
    Args:
        page: Article title
        
    Returns:
        List of section dictionaries
    """
    params = {
        "action": "parse",
        "page": page,
        "prop": "sections",
        "format": "json",
        "redirects": ""
    }
    
    data = make_request(params)
    if data and "parse" in data and "sections" in data["parse"]:
        sections = data["parse"]["sections"]
        if DEBUG_MODE:
            print(f"📖 Found {len(sections)} sections in '{page}'")
        return sections
    
    return []


def getLinksBySection(page: str, section: int, valid_links: Set[str]) -> None:
    """
    Extract links from a specific section of a Wikipedia page.
    
    Args:
        page: Article title
        section: Section number
        valid_links: Set to add found links to
    """
    params = {
        "action": "parse",
        "page": page,
        "prop": "links",
        "section": section,
        "format": "json",
        "redirects": ""
    }
    
    data = make_request(params)
    if data and "parse" in data and "links" in data["parse"]:
        for link in data["parse"]["links"]:
            # Only include main namespace articles (ns=0)
            if link["ns"] == 0:
                valid_links.add(link["*"])


def getLinksInLead(page: str, valid_links: Set[str]) -> None:
    """
    Extract links from the lead section and infoboxes using HTML parsing.
    
    Args:
        page: Article title
        valid_links: Set to add found links to
    """
    # Get page URL
    params = {
        "action": "query",
        "format": "json",
        "prop": "info",
        "titles": page,
        "redirects": "",
        "indexpageids": "",
        "inprop": "url"
    }
    
    data = make_request(params)
    if not data or "query" not in data:
        return
    
    page_ids = data["query"]["pageids"]
    if page_ids[0] == '-1':
        return
    
    try:
        page_url = data["query"]["pages"][page_ids[0]]["fullurl"]
        
        # Fetch the page HTML
        response = session.get(page_url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract links from different sections
        selectors = [
            "div.mw-content-ltr.mw-parser-output p",  # Main content paragraphs
            "table.infobox",                          # Infoboxes
            "table.wikitable"                         # Tables
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            _extract_links_from_elements(elements, valid_links)
            
    except Exception as e:
        if DEBUG_MODE:
            print(f"⚠️  Error extracting lead links from '{page}': {e}")


def _extract_links_from_elements(elements: List, valid_links: Set[str]) -> None:
    """
    Helper function to extract Wikipedia links from HTML elements.
    
    Args:
        elements: List of BeautifulSoup elements
        valid_links: Set to add found links to
    """
    for element in elements:
        for link in element.select("a[href]"):
            href = link.get('href', '')
            
            # Filter for Wikipedia article links
            if (href.startswith('/wiki/') and 
                not any(skip in href for skip in ['File:', 'Help:', 'Category:', 'Template:', 'User:'])):
                
                # Clean the link title
                clean_title = href.replace('/wiki/', '').replace('_', ' ')
                clean_title = unquote(clean_title)
                valid_links.add(clean_title)


def getAllValidLinks(page: str) -> Set[str]:
    """
    Get all valid Wikipedia links from a page using concurrent processing.
    
    Args:
        page: Article title
        
    Returns:
        Set of linked article titles
    """
    page = unquote(page)
    valid_links = set()
    
    if DEBUG_MODE:
        print(f"🔗 Extracting links from '{page}'")
    
    # Get page sections
    sections = getAllSections(page)
    
    # Use concurrent processing for faster link extraction
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Start with lead section
        executor.submit(getLinksInLead, page, valid_links)
        
        # Process each section concurrently
        for i, section in enumerate(sections):
            section_title = section.get("line", "")
            
            # Skip blacklisted sections
            if section_title not in BLACKLISTED_SECTIONS:
                executor.submit(getLinksBySection, page, i, valid_links)
    
    if DEBUG_MODE:
        print(f"✅ Found {len(valid_links)} valid links")
        if len(valid_links) > 0:
            print(f"📎 Sample links: {list(valid_links)[:5]}")
    
    return valid_links


# Module information
__version__ = "1.0.0"
__author__ = "Gildian Gonzales"

if DEBUG_MODE:
    print(f"🌐 Wikipedia API module loaded (v{__version__})")
    print(f"🔗 API URL: {API_URL}")
    print(f"⏱️  Timeout: {REQUEST_TIMEOUT}s")
