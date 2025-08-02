#!/usr/bin/env python3
"""
GloVe Embeddings Loader

A modern replacement for torchtext's GloVe loader that downloads and caches
Stanford's pre-trained word embeddings for semantic similarity calculations.

This module provides a drop-in replacement for the legacy torchtext.vocab.GloVe
functionality with improved error handling, caching, and progress tracking.

Author: Gildian Gonzales
License: MIT
"""

import os
import urllib.request
import zipfile
import torch
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Union
import time
import hashlib


class ProgressReporter:
    """Simple progress reporter for downloads."""
    
    def __init__(self, total_size: int):
        self.total_size = total_size
        self.downloaded = 0
        self.last_report = 0
        
    def update(self, chunk_size: int):
        self.downloaded += chunk_size
        current_time = time.time()
        
        # Report progress every 2 seconds
        if current_time - self.last_report > 2:
            percent = (self.downloaded / self.total_size) * 100
            mb_downloaded = self.downloaded / (1024 * 1024)
            mb_total = self.total_size / (1024 * 1024)
            print(f"📥 Downloaded {mb_downloaded:.1f}/{mb_total:.1f} MB ({percent:.1f}%)")
            self.last_report = current_time


class GloVeLoader:
    """
    A modern GloVe embeddings loader with caching and error handling.
    
    This class downloads, caches, and loads Stanford's GloVe word embeddings,
    providing the same interface as the legacy torchtext implementation.
    """
    
    def __init__(self, name: str = "6B", dim: int = 300, cache_dir: str = "glove_cache"):
        """
        Initialize the GloVe loader.
        
        Args:
            name: GloVe dataset name (e.g., "6B", "42B", "840B")
            dim: Embedding dimensions (50, 100, 200, or 300 for 6B)
            cache_dir: Directory to store downloaded files
        """
        self.name = name
        self.dim = dim
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Validate parameters
        if name == "6B" and dim not in [50, 100, 200, 300]:
            raise ValueError(f"Invalid dimension {dim} for GloVe {name}. Must be 50, 100, 200, or 300.")
        
        # File paths
        self.url = f"https://nlp.stanford.edu/data/glove.{name}.zip"
        self.zip_path = self.cache_dir / f"glove.{name}.zip"
        self.txt_path = self.cache_dir / f"glove.{name}.{dim}d.txt"
        self.cache_path = self.cache_dir / f"glove.{name}.{dim}d.pt"
        
        # Embeddings data
        self.vectors: Optional[torch.Tensor] = None
        self.word_to_idx: Dict[str, int] = {}
        self.idx_to_word: Dict[int, str] = {}
        self._loaded = False
        
        # Stats
        self.vocab_size = 0
        
    def _download_with_progress(self) -> None:
        """Download GloVe vectors with progress reporting."""
        print(f"📡 Downloading GloVe {self.name} vectors from Stanford...")
        print(f"🌐 URL: {self.url}")
        
        def progress_hook(block_num: int, block_size: int, total_size: int):
            if not hasattr(progress_hook, 'reporter'):
                progress_hook.reporter = ProgressReporter(total_size)
            progress_hook.reporter.update(block_size)
        
        try:
            urllib.request.urlretrieve(self.url, self.zip_path, progress_hook)
            print("✅ Download completed!")
        except Exception as e:
            print(f"❌ Download failed: {e}")
            if self.zip_path.exists():
                self.zip_path.unlink()
            raise
    
    def _verify_file_integrity(self) -> bool:
        """Verify downloaded file isn't corrupted."""
        try:
            with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
                # Test the zip file
                bad_file = zip_ref.testzip()
                if bad_file:
                    print(f"❌ Corrupted file in zip: {bad_file}")
                    return False
            return True
        except zipfile.BadZipFile:
            print("❌ Downloaded file is not a valid zip archive")
            return False
    
    def _extract_vectors(self) -> None:
        """Extract GloVe vectors from zip file."""
        if not self.txt_path.exists():
            print("📦 Extracting GloVe vectors...")
            
            if not self._verify_file_integrity():
                print("🔄 Re-downloading due to corruption...")
                self.zip_path.unlink()
                self._download_with_progress()
            
            try:
                with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
                    zip_ref.extractall(self.cache_dir)
                print("✅ Extraction completed!")
            except Exception as e:
                print(f"❌ Extraction failed: {e}")
                raise
    
    def _build_cache(self) -> None:
        """Build tensor cache from text file."""
        print(f"🔧 Building vector cache for {self.dim}d embeddings...")
        
        vectors = []
        words = []
        invalid_lines = 0
        
        start_time = time.time()
        
        try:
            with open(self.txt_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if line_num % 100000 == 0:
                        print(f"📊 Processed {line_num:,} lines...")
                    
                    parts = line.strip().split()
                    if len(parts) < 2:
                        continue
                        
                    word = parts[0]
                    try:
                        vector = [float(x) for x in parts[1:]]
                        
                        if len(vector) == self.dim:
                            words.append(word)
                            vectors.append(vector)
                        else:
                            invalid_lines += 1
                            
                    except ValueError:
                        invalid_lines += 1
                        continue
            
            if not vectors:
                raise ValueError("No valid vectors found in file")
            
            print(f"✅ Loaded {len(words):,} word vectors")
            if invalid_lines > 0:
                print(f"⚠️  Skipped {invalid_lines} invalid lines")
            
            # Convert to tensors
            print("🧮 Converting to PyTorch tensors...")
            self.vectors = torch.tensor(vectors, dtype=torch.float32)
            self.word_to_idx = {word: i for i, word in enumerate(words)}
            self.idx_to_word = {i: word for i, word in enumerate(words)}
            self.vocab_size = len(words)
            
            # Save cache
            print("💾 Saving cache...")
            cache_data = {
                'vectors': self.vectors,
                'word_to_idx': self.word_to_idx,
                'idx_to_word': self.idx_to_word,
                'vocab_size': self.vocab_size,
                'dim': self.dim,
                'name': self.name,
                'version': '1.0'
            }
            torch.save(cache_data, self.cache_path)
            
            elapsed = time.time() - start_time
            print(f"✅ Cache built in {elapsed:.1f} seconds")
            
        except Exception as e:
            print(f"❌ Failed to build cache: {e}")
            raise
    
    def _load_from_cache(self) -> None:
        """Load vectors from cache file."""
        print("📂 Loading cached GloVe vectors...")
        
        try:
            cache_data = torch.load(self.cache_path, weights_only=True)
            
            # Verify cache compatibility
            if (cache_data.get('dim') != self.dim or 
                cache_data.get('name') != self.name):
                print("⚠️  Cache incompatible, rebuilding...")
                self._build_cache()
                return
            
            self.vectors = cache_data['vectors']
            self.word_to_idx = cache_data['word_to_idx']
            self.idx_to_word = cache_data['idx_to_word']
            self.vocab_size = cache_data.get('vocab_size', len(self.word_to_idx))
            
            print(f"✅ Loaded {self.vocab_size:,} cached vectors")
            
        except Exception as e:
            print(f"❌ Failed to load cache: {e}")
            print("🔄 Rebuilding cache...")
            self._build_cache()
    
    def load(self) -> None:
        """Load embeddings (download if necessary)."""
        if self._loaded:
            return
        
        print(f"🚀 Initializing GloVe {self.name} embeddings ({self.dim}d)")
        
        # Check if cache exists
        if self.cache_path.exists():
            self._load_from_cache()
        else:
            # Download if needed
            if not self.zip_path.exists():
                self._download_with_progress()
            
            # Extract vectors
            self._extract_vectors()
            
            # Build cache
            self._build_cache()
        
        self._loaded = True
        print(f"🎯 GloVe embeddings ready! Vocabulary: {self.vocab_size:,} words")
    
    def __getitem__(self, word: str) -> torch.Tensor:
        """
        Get embedding vector for a word.
        
        Args:
            word: Word to look up
            
        Returns:
            Embedding tensor (zeros if word not found)
        """
        if not self._loaded:
            self.load()
        
        if word in self.word_to_idx:
            idx = self.word_to_idx[word]
            return self.vectors[idx]
        else:
            # Return zero vector for unknown words
            return torch.zeros(self.dim, dtype=torch.float32)
    
    def __contains__(self, word: str) -> bool:
        """Check if word is in vocabulary."""
        if not self._loaded:
            self.load()
        return word in self.word_to_idx
    
    def get_word_similarity(self, word1: str, word2: str) -> float:
        """
        Calculate cosine similarity between two words.
        
        Args:
            word1: First word
            word2: Second word
            
        Returns:
            Cosine similarity score (-1 to 1)
        """
        vec1 = self[word1]
        vec2 = self[word2]
        
        # Handle zero vectors
        if torch.allclose(vec1, torch.zeros_like(vec1)) or torch.allclose(vec2, torch.zeros_like(vec2)):
            return 0.0
        
        return float(torch.nn.functional.cosine_similarity(
            vec1.unsqueeze(0), vec2.unsqueeze(0)
        ))
    
    def most_similar(self, word: str, top_k: int = 10) -> List[tuple]:
        """
        Find most similar words to the given word.
        
        Args:
            word: Target word
            top_k: Number of similar words to return
            
        Returns:
            List of (word, similarity_score) tuples
        """
        if not self._loaded:
            self.load()
        
        if word not in self:
            return []
        
        target_vec = self[word].unsqueeze(0)
        similarities = torch.nn.functional.cosine_similarity(target_vec, self.vectors)
        
        # Get top-k most similar (excluding the word itself)
        top_indices = similarities.topk(top_k + 1).indices[1:]  # Skip first (self)
        
        results = []
        for idx in top_indices:
            similar_word = self.idx_to_word[int(idx)]
            score = float(similarities[idx])
            results.append((similar_word, score))
        
        return results
    
    def __len__(self) -> int:
        """Return vocabulary size."""
        if not self._loaded:
            self.load()
        return self.vocab_size
    
    def __repr__(self) -> str:
        """String representation."""
        status = "loaded" if self._loaded else "not loaded"
        return f"GloVeLoader(name='{self.name}', dim={self.dim}, vocab_size={self.vocab_size:,}, status={status})"


def create_embeddings(name: str = "6B", dim: int = 300) -> GloVeLoader:
    """
    Create a GloVe embeddings loader (torchtext-compatible interface).
    
    Args:
        name: GloVe dataset name
        dim: Embedding dimensions
        
    Returns:
        GloVeLoader instance
    """
    return GloVeLoader(name=name, dim=dim)


# Module metadata
__version__ = "1.0.0"
__author__ = "Gildian Gonzales"

if __name__ == "__main__":
    # Demo usage
    print(f"GloVe Loader v{__version__}")
    print("Loading embeddings...")
    
    glove = create_embeddings()
    glove.load()
    
    # Test some words
    test_words = ["king", "queen", "man", "woman", "computer", "python"]
    print("\nTesting word embeddings:")
    
    for word in test_words:
        if word in glove:
            vec = glove[word]
            print(f"✅ '{word}': {vec.shape}")
        else:
            print(f"❌ '{word}': not found")
    
    # Test similarity
    if "king" in glove and "queen" in glove:
        similarity = glove.get_word_similarity("king", "queen")
        print(f"\n👑 Similarity between 'king' and 'queen': {similarity:.3f}")
    
    print(f"\n📊 Total vocabulary: {len(glove):,} words")
