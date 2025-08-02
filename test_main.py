#!/usr/bin/env python3
"""
Wikipedia Path Finder - Test Suite

Comprehensive tests for the pathfinding algorithms, API interfaces,
and helper functions.

Author: Gildian Gonzales
License: MIT
"""

import unittest
import sys
import os
import time
from unittest.mock import patch, MagicMock
import torch

# Add the bot directory to the path
bot_dir = os.path.join(os.path.dirname(__file__), 'bot')
if bot_dir not in sys.path:
    sys.path.insert(0, bot_dir)

# Import modules to test
try:
    import helpers
    import search_functions
    import wikiapi
    import glove_loader
    
    from helpers import (
        process_wiki_article, get_word_score, pre_compute_goal,
        get_closest_links, get_closest_link
    )
    from search_functions import best_first_search, depth_first_search
    from wikiapi import getPageDetails, getTwoRandomPages
    from glove_loader import GloVeLoader, create_embeddings
    
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some modules could not be imported: {e}")
    print("Some tests may be skipped. Make sure you're running this from the project root directory")
    MODULES_AVAILABLE = False


class TestGloVeLoader(unittest.TestCase):
    """Test the GloVe embeddings loader."""
    
    @unittest.skipUnless(MODULES_AVAILABLE, "Modules not available")
    def setUp(self):
        """Set up test fixtures."""
        self.loader = glove_loader.GloVeLoader(name="6B", dim=50)  # Use smaller dim for testing
    
    @unittest.skipUnless(MODULES_AVAILABLE, "Modules not available")
    def test_initialization(self):
        """Test GloVe loader initialization."""
        self.assertEqual(self.loader.name, "6B")
        self.assertEqual(self.loader.dim, 50)
        self.assertIsNone(self.loader.vectors)
    
    @unittest.skipUnless(MODULES_AVAILABLE, "Modules not available")
    def test_invalid_dimension(self):
        """Test error handling for invalid dimensions."""
        with self.assertRaises(ValueError):
            glove_loader.GloVeLoader(name="6B", dim=999)
    
    @unittest.skipUnless(MODULES_AVAILABLE, "Modules not available")
    def test_contains_method(self):
        """Test word vocabulary checking."""
        # Mock the vectors to avoid downloading
        self.loader.vectors = torch.zeros(10, 50)
        self.loader.word_to_idx = {"test": 0, "word": 1}
        self.loader._loaded = True
        
        self.assertTrue("test" in self.loader)
        self.assertFalse("nonexistent" in self.loader)
    
    @unittest.skipUnless(MODULES_AVAILABLE, "Modules not available")
    def test_getitem_method(self):
        """Test word vector retrieval."""
        # Mock the vectors
        self.loader.vectors = torch.ones(10, 50)
        self.loader.word_to_idx = {"test": 0}
        self.loader._loaded = True
        
        vector = self.loader["test"]
        self.assertEqual(vector.shape, (50,))
        self.assertTrue(torch.allclose(vector, torch.ones(50)))
        
        # Test unknown word
        zero_vector = self.loader["unknown"]
        self.assertEqual(zero_vector.shape, (50,))
        self.assertTrue(torch.allclose(zero_vector, torch.zeros(50)))


class TestHelperFunctions(unittest.TestCase):
    """Test helper functions for pathfinding."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock GloVe embeddings to avoid downloading
        self.mock_glove = MagicMock()
        self.mock_glove.__contains__ = lambda _, word: word in ["test", "word", "python", "machine", "learning"]
        self.mock_glove.__getitem__ = lambda _, word: torch.randn(300)
    
    @patch('helpers.glove')
    def test_pre_compute_goal(self, mock_glove_global):
        """Test goal vector pre-computation."""
        mock_glove_global.__contains__ = lambda word: word in ["machine", "learning"]
        mock_glove_global.__getitem__ = lambda word: torch.randn(300)
        
        pre_compute_goal("Machine Learning")
        
        # Should not raise any errors
        self.assertTrue(True)
    
    @patch('helpers.glove')
    @patch('helpers.goal_vector_data')
    def test_get_word_score(self, mock_goal_data, mock_glove_global):
        """Test semantic similarity scoring."""
        # Mock goal data
        mock_goal_data.__getitem__ = lambda key: {
            "vectors": [torch.randn(1, 300)],
            "mean": torch.randn(300)
        }[key]
        
        mock_glove_global.__contains__ = lambda word: word in ["test", "word"]
        mock_glove_global.__getitem__ = lambda word: torch.randn(300)
        
        score = get_word_score("test word")
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, -1.0)
        self.assertLessEqual(score, 1.0)
    
    @patch('helpers.getPageDetails')
    def test_process_wiki_article_success(self, mock_get_details):
        """Test successful article processing."""
        mock_get_details.return_value = {
            "exists": True,
            "title": "Test Article",
            "categories": []
        }
        
        result = process_wiki_article("test")
        self.assertEqual(result, "Test Article")
    
    @patch('helpers.getPageDetails')
    def test_process_wiki_article_not_exists(self, mock_get_details):
        """Test handling of non-existent articles."""
        mock_get_details.return_value = {"exists": False}
        
        with self.assertRaises(SystemExit):
            process_wiki_article("nonexistent")
    
    @patch('helpers.getPageDetails')
    def test_process_wiki_article_disambiguation(self, mock_get_details):
        """Test handling of disambiguation pages."""
        mock_get_details.return_value = {
            "exists": True,
            "title": "Test (disambiguation)",
            "categories": [{"title": "Category:Disambiguation pages"}]
        }
        
        with self.assertRaises(SystemExit):
            process_wiki_article("test disambiguation")


class TestWikipediaAPI(unittest.TestCase):
    """Test Wikipedia API interface functions."""
    
    @patch('wikiapi.make_request')
    def test_get_page_details_exists(self, mock_request):
        """Test getting details for existing page."""
        mock_request.return_value = {
            "query": {
                "pageids": ["123"],
                "pages": {
                    "123": {
                        "title": "Test Page",
                        "categories": []
                    }
                }
            }
        }
        
        result = getPageDetails("Test Page")
        self.assertTrue(result["exists"])
        self.assertEqual(result["title"], "Test Page")
    
    @patch('wikiapi.make_request')
    def test_get_page_details_not_exists(self, mock_request):
        """Test getting details for non-existent page."""
        mock_request.return_value = {
            "query": {
                "pageids": ["-1"]
            }
        }
        
        result = getPageDetails("Nonexistent Page")
        self.assertFalse(result["exists"])
    
    @patch('wikiapi.make_request')
    def test_get_two_random_pages(self, mock_request):
        """Test getting random pages."""
        mock_request.return_value = {
            "query": {
                "random": [
                    {"title": "Random Page 1"},
                    {"title": "Random Page 2"}
                ]
            }
        }
        
        result = getTwoRandomPages()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["title"], "Random Page 1")
        self.assertEqual(result[1]["title"], "Random Page 2")


class TestSearchAlgorithms(unittest.TestCase):
    """Test pathfinding algorithms."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.start_time = time.time()
    
    @patch('search_functions.get_closest_links')
    @patch('search_functions.getPageDetails')
    def test_best_first_search_simple(self, mock_get_details, mock_get_links):
        """Test best-first search with simple path."""
        # Mock page details
        mock_get_details.return_value = {"exists": True, "title": "Test"}
        
        # Mock links - return goal directly
        mock_get_links.return_value = {("Goal", 1.0)}
        
        result = best_first_search("Start", "goal", self.start_time)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
    
    @patch('search_functions.get_closest_link')
    def test_depth_first_search_direct(self, mock_get_link):
        """Test depth-first search direct to goal."""
        # Mock getting the goal directly
        mock_get_link.return_value = ("Goal", 1.0)
        
        result = depth_first_search("Start", "goal", ["Start"], self.start_time)
        self.assertIsInstance(result, list)
        self.assertIn("Goal", result)
    
    def test_search_timeout(self):
        """Test search timeout functionality."""
        # Use a time from the past to trigger timeout
        past_time = time.time() - 200
        
        result = best_first_search("Start", "Goal", past_time)
        self.assertEqual(result, "NO SOLUTION")
        
        result = depth_first_search("Start", "Goal", ["Start"], past_time)
        self.assertEqual(result, "NO SOLUTION")


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system."""
    
    @patch('helpers.glove')
    @patch('wikiapi.getAllValidLinks')
    @patch('wikiapi.getPageDetails')
    def test_full_pathfinding_pipeline(self, mock_get_details, mock_get_links, mock_glove):
        """Test the complete pathfinding pipeline."""
        # Mock GloVe
        mock_glove.__contains__ = lambda word: True
        mock_glove.__getitem__ = lambda word: torch.randn(300)
        
        # Mock page details
        mock_get_details.return_value = {"exists": True, "title": "Test"}
        
        # Mock links
        mock_get_links.return_value = {"Intermediate", "Goal"}
        
        # Pre-compute goal
        pre_compute_goal("Goal")
        
        # Test getting closest links
        links = get_closest_links("Start", "goal", ["Start"])
        self.assertIsInstance(links, set)
        
        # Test getting single closest link
        link = get_closest_link("Start", "goal", ["Start"])
        self.assertIsInstance(link, tuple)
        self.assertEqual(len(link), 2)


def run_performance_tests():
    """Run performance benchmarks."""
    print("\n" + "="*50)
    print("PERFORMANCE TESTS")
    print("="*50)
    
    # Test GloVe loading time (if vectors exist)
    print("\n1. Testing GloVe loader performance...")
    start_time = time.time()
    try:
        loader = create_embeddings()
        if hasattr(loader, '_loaded') and not loader._loaded:
            print("   GloVe vectors not cached - skipping load test")
        else:
            loader.load()
            load_time = time.time() - start_time
            print(f"   GloVe load time: {load_time:.2f} seconds")
            
            # Test word lookup speed
            test_words = ["test", "word", "python", "machine", "learning"]
            lookup_start = time.time()
            for word in test_words * 100:  # 500 lookups
                _ = loader[word]
            lookup_time = time.time() - lookup_start
            print(f"   Word lookup time (500 words): {lookup_time:.3f} seconds")
            
    except Exception as e:
        print(f"   GloVe performance test failed: {e}")
    
    print("\n2. Testing similarity calculation performance...")
    try:
        # Mock similarity calculations
        start_time = time.time()
        for _ in range(1000):
            vec1 = torch.randn(300)
            vec2 = torch.randn(300)
            _ = torch.nn.functional.cosine_similarity(vec1.unsqueeze(0), vec2.unsqueeze(0))
        calc_time = time.time() - start_time
        print(f"   Similarity calculations (1000): {calc_time:.3f} seconds")
    except Exception as e:
        print(f"   Similarity performance test failed: {e}")


def main():
    """Run all tests."""
    print("Wikipedia Path Finder - Test Suite")
    print("="*50)
    
    # Run unit tests
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run performance tests
    run_performance_tests()
    
    print("\n" + "="*50)
    print("All tests completed!")


if __name__ == "__main__":
    main()
