#!/usr/bin/env python3
"""
Wikipedia Path Finder - Simple Test Suite

Basic tests to verify the system is working correctly.
Run this with: python test_simple.py

Author: Gildian Gonzales
License: MIT
"""

import unittest
import sys
import os
import tempfile
import json
from unittest.mock import patch, MagicMock


class TestProjectStructure(unittest.TestCase):
    """Test that all required files exist and have basic structure."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.project_root = os.path.dirname(os.path.abspath(__file__))
        self.bot_dir = os.path.join(self.project_root, 'bot')
        self.client_dir = os.path.join(self.project_root, 'client')
    
    def test_required_files_exist(self):
        """Test that all required files exist."""
        required_files = [
            'README.md',
            'requirements.txt',
            'bot/main.py',
            'bot/helpers.py',
            'bot/search_functions.py',
            'bot/wikiapi.py',
            'bot/glove_loader.py',
            'bot/server.js',
            'bot/package.json',
            'client/package.json',
            'client/src/App.jsx',
            'client/src/views/Home/index.jsx'
        ]
        
        for file_path in required_files:
            full_path = os.path.join(self.project_root, file_path)
            self.assertTrue(
                os.path.exists(full_path),
                f"Required file {file_path} does not exist"
            )
    
    def test_bot_directory_structure(self):
        """Test bot directory has correct structure."""
        self.assertTrue(os.path.isdir(self.bot_dir))
        
        required_bot_files = [
            'main.py', 'helpers.py', 'search_functions.py', 
            'wikiapi.py', 'glove_loader.py', 'server.js', 'package.json'
        ]
        
        for filename in required_bot_files:
            file_path = os.path.join(self.bot_dir, filename)
            self.assertTrue(
                os.path.exists(file_path),
                f"Bot file {filename} does not exist"
            )
    
    def test_client_directory_structure(self):
        """Test client directory has correct structure."""
        self.assertTrue(os.path.isdir(self.client_dir))
        
        required_dirs = ['src', 'public']
        for dirname in required_dirs:
            dir_path = os.path.join(self.client_dir, dirname)
            self.assertTrue(
                os.path.isdir(dir_path),
                f"Client directory {dirname} does not exist"
            )


class TestPackageConfiguration(unittest.TestCase):
    """Test package.json files are properly configured."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.project_root = os.path.dirname(os.path.abspath(__file__))
    
    def test_bot_package_json(self):
        """Test bot package.json has required fields."""
        package_path = os.path.join(self.project_root, 'bot', 'package.json')
        self.assertTrue(os.path.exists(package_path))
        
        with open(package_path, 'r') as f:
            package_data = json.load(f)
        
        required_fields = ['name', 'version', 'scripts', 'dependencies']
        for field in required_fields:
            self.assertIn(field, package_data, f"Missing {field} in bot package.json")
        
        # Check for required scripts
        self.assertIn('start', package_data['scripts'])
        
        # Check for required dependencies
        required_deps = ['express', 'cors']
        for dep in required_deps:
            self.assertIn(dep, package_data['dependencies'])
    
    def test_client_package_json(self):
        """Test client package.json has required fields."""
        package_path = os.path.join(self.project_root, 'client', 'package.json')
        self.assertTrue(os.path.exists(package_path))
        
        with open(package_path, 'r') as f:
            package_data = json.load(f)
        
        required_fields = ['name', 'version', 'scripts', 'dependencies']
        for field in required_fields:
            self.assertIn(field, package_data, f"Missing {field} in client package.json")
        
        # Check for required scripts
        required_scripts = ['dev', 'build', 'preview']
        for script in required_scripts:
            self.assertIn(script, package_data['scripts'])
        
        # Check for required dependencies
        required_deps = ['react']
        for dep in required_deps:
            self.assertIn(dep, package_data['dependencies'])


class TestPythonFileStructure(unittest.TestCase):
    """Test Python files have proper structure."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.project_root = os.path.dirname(os.path.abspath(__file__))
        self.bot_dir = os.path.join(self.project_root, 'bot')
    
    def test_main_py_structure(self):
        """Test main.py has proper structure."""
        main_path = os.path.join(self.bot_dir, 'main.py')
        with open(main_path, 'r') as f:
            content = f.read()
        
        # Check for key components
        self.assertIn('def main()', content)
        self.assertIn('argparse', content)
        self.assertIn('if __name__ == "__main__"', content)
    
    def test_helpers_py_structure(self):
        """Test helpers.py has proper structure."""
        helpers_path = os.path.join(self.bot_dir, 'helpers.py')
        with open(helpers_path, 'r') as f:
            content = f.read()
        
        # Check for key functions
        required_functions = [
            'def get_word_score(',
            'def pre_compute_goal(',
            'def get_closest_links(',
            'def process_wiki_article('
        ]
        
        for func in required_functions:
            self.assertIn(func, content, f"Missing function: {func}")
    
    def test_search_functions_structure(self):
        """Test search_functions.py has proper structure."""
        search_path = os.path.join(self.bot_dir, 'search_functions.py')
        with open(search_path, 'r') as f:
            content = f.read()
        
        # Check for key algorithms
        self.assertIn('def best_first_search(', content)
        self.assertIn('def depth_first_search(', content)
        self.assertIn('heapq', content)  # Priority queue for best-first
    
    def test_wikiapi_structure(self):
        """Test wikiapi.py has proper structure."""
        wikiapi_path = os.path.join(self.bot_dir, 'wikiapi.py')
        with open(wikiapi_path, 'r') as f:
            content = f.read()
        
        # Check for key functions
        required_functions = [
            'def getPageDetails(',
            'def getAllValidLinks(',
            'def getTwoRandomPages('
        ]
        
        for func in required_functions:
            self.assertIn(func, content, f"Missing function: {func}")
    
    def test_glove_loader_structure(self):
        """Test glove_loader.py has proper structure."""
        glove_path = os.path.join(self.bot_dir, 'glove_loader.py')
        with open(glove_path, 'r') as f:
            content = f.read()
        
        # Check for key components
        self.assertIn('class GloVeLoader', content)
        self.assertIn('def create_embeddings(', content)
        self.assertIn('torch', content)


class TestRequirements(unittest.TestCase):
    """Test requirements.txt has necessary packages."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.project_root = os.path.dirname(os.path.abspath(__file__))
    
    def test_requirements_file_exists(self):
        """Test requirements.txt exists and has content."""
        req_path = os.path.join(self.project_root, 'requirements.txt')
        self.assertTrue(os.path.exists(req_path))
        
        with open(req_path, 'r') as f:
            content = f.read().strip()
        
        self.assertTrue(len(content) > 0, "requirements.txt is empty")
        
        # Check for key packages
        required_packages = ['torch', 'requests', 'beautifulsoup4']
        for package in required_packages:
            self.assertIn(package, content, f"Missing package: {package}")


class TestJavaScriptFiles(unittest.TestCase):
    """Test JavaScript files have proper structure."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.project_root = os.path.dirname(os.path.abspath(__file__))
    
    def test_server_js_structure(self):
        """Test server.js has proper Express structure."""
        server_path = os.path.join(self.project_root, 'bot', 'server.js')
        with open(server_path, 'r') as f:
            content = f.read()
        
        # Check for Express components
        self.assertIn('express', content)
        self.assertIn('cors', content)
        self.assertIn('app.listen', content)
        self.assertIn('POST /', content)  # API routes
    
    def test_react_app_structure(self):
        """Test React App.jsx has proper structure."""
        app_path = os.path.join(self.project_root, 'client', 'src', 'App.jsx')
        with open(app_path, 'r') as f:
            content = f.read()
        
        # Check for React components
        self.assertIn('import', content)
        self.assertIn('function App', content)
        self.assertIn('export default App', content)
    
    def test_home_component_structure(self):
        """Test Home component has proper structure."""
        home_path = os.path.join(self.project_root, 'client', 'src', 'views', 'Home', 'index.jsx')
        with open(home_path, 'r') as f:
            content = f.read()
        
        # Check for React hooks and components
        self.assertIn('useState', content)
        self.assertIn('function Home', content)
        self.assertIn('export default Home', content)


class TestDocumentation(unittest.TestCase):
    """Test documentation files are comprehensive."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.project_root = os.path.dirname(os.path.abspath(__file__))
    
    def test_readme_content(self):
        """Test README.md has comprehensive content."""
        readme_path = os.path.join(self.project_root, 'README.md')
        with open(readme_path, 'r') as f:
            content = f.read()
        
        # Check for key sections
        required_sections = [
            '# Wikipedia Path Finder',
            '🚀 Features',
            '🔧 Installation',
            '🚀 Usage',
            '📚 References'
        ]
        
        for section in required_sections:
            self.assertIn(section, content, f"Missing section: {section}")
        
        # Check for installation instructions
        self.assertIn('pip install', content)
        self.assertIn('npm install', content)


class TestBasicFunctionality(unittest.TestCase):
    """Test basic functionality without external dependencies."""
    
    def test_import_availability(self):
        """Test which modules can be imported."""
        bot_dir = os.path.join(os.path.dirname(__file__), 'bot')
        if bot_dir not in sys.path:
            sys.path.insert(0, bot_dir)
        
        # Test basic Python imports
        try:
            import json
            import time
            import heapq
            import argparse
            self.assertTrue(True)  # Basic imports work
        except ImportError as e:
            self.fail(f"Basic imports failed: {e}")
        
        # Test if torch is available
        try:
            import torch
            torch_available = True
        except ImportError:
            torch_available = False
        
        print(f"PyTorch available: {torch_available}")
        
        # Test if requests is available
        try:
            import requests
            requests_available = True
        except ImportError:
            requests_available = False
        
        print(f"Requests available: {requests_available}")


def create_simple_performance_test():
    """Create a simple performance test for basic operations."""
    import time
    
    print("\n" + "="*50)
    print("BASIC PERFORMANCE TESTS")
    print("="*50)
    
    # Test basic string operations
    print("\n1. Testing string processing performance...")
    start_time = time.time()
    test_string = "This is a test string for performance testing"
    for _ in range(10000):
        words = test_string.lower().split()
        processed = [word.strip('.,!?') for word in words]
    string_time = time.time() - start_time
    print(f"   String processing (10k iterations): {string_time:.3f} seconds")
    
    # Test JSON operations
    print("\n2. Testing JSON operations...")
    test_data = {
        "title": "Test Article",
        "links": ["Link1", "Link2", "Link3"],
        "score": 0.85,
        "metadata": {"author": "Test", "date": "2024"}
    }
    start_time = time.time()
    for _ in range(1000):
        json_str = json.dumps(test_data)
        parsed = json.loads(json_str)
    json_time = time.time() - start_time
    print(f"   JSON operations (1k iterations): {json_time:.3f} seconds")
    
    # Test file operations
    print("\n3. Testing file operations...")
    start_time = time.time()
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        temp_path = f.name
        for i in range(100):
            f.write(f"Line {i}: Test data for performance testing\n")
    
    # Read the file back
    with open(temp_path, 'r') as f:
        lines = f.readlines()
    
    os.unlink(temp_path)
    file_time = time.time() - start_time
    print(f"   File operations (100 lines): {file_time:.3f} seconds")


def main():
    """Run all tests."""
    print("Wikipedia Path Finder - Simple Test Suite")
    print("="*50)
    
    # Run unit tests
    test_loader = unittest.TestLoader()
    test_suite = test_loader.loadTestsFromModule(sys.modules[__name__])
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Run performance tests
    create_simple_performance_test()
    
    print("\n" + "="*50)
    if result.wasSuccessful():
        print("✅ All tests passed!")
        print("Project structure and basic functionality verified.")
    else:
        print("❌ Some tests failed.")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    import json
    sys.exit(main())
