"""
URL Shortener - CRUD module for managing short URLs and their mappings.

This module provides basic Create, Read, Update, Delete operations
for a URL shortening service.
"""

import json
import os
from typing import Optional, Dict


class URLShortener:
    """Manages short URL to original URL mappings with persistent storage."""

    def __init__(self, storage_file: str = "urls.json"):
        """
        Initialize the URL shortener.
        
        Args:
            storage_file: Path to JSON file for persistent storage
        """
        self.storage_file = storage_file
        self.urls: Dict[str, str] = {}
        self._load_from_disk()

    def _load_from_disk(self) -> None:
        """Load URL mappings from disk if file exists."""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    self.urls = json.load(f)
                print(f"Loaded {len(self.urls)} URLs from {self.storage_file}")
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load {self.storage_file}: {e}")
                self.urls = {}
        else:
            print(f"No existing storage found. Starting fresh.")
            self.urls = {}

    def _save_to_disk(self) -> None:
        """Persist URL mappings to disk."""
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(self.urls, f, indent=2)
        except IOError as e:
            raise RuntimeError(f"Failed to save to {self.storage_file}: {e}")

    def _generate_short_code(self, original_url: str) -> str:
        """
        Generate a simple short code from the original URL.
        
        In production, this would use hashing or a counter.
        For now, we use first 6 chars of the URL's hash.
        
        Args:
            original_url: The URL to shorten
            
        Returns:
            A short code string
        """
        import hashlib
        hash_obj = hashlib.md5(original_url.encode())
        # Take first 6 chars of hex digest
        return hash_obj.hexdigest()[:6]

    def create(self, original_url: str, custom_short_code: Optional[str] = None) -> str:
        """
        Create a new short URL mapping.
        
        Args:
            original_url: The full URL to shorten
            custom_short_code: Optional custom short code (if not provided, auto-generate)
            
        Returns:
            The short code (custom or auto-generated)
            
        Raises:
            ValueError: If original_url is empty or short code already exists
        """
        if not original_url or not isinstance(original_url, str):
            raise ValueError("original_url must be a non-empty string")

        short_code = custom_short_code or self._generate_short_code(original_url)

        if short_code in self.urls:
            raise ValueError(f"Short code '{short_code}' already exists")

        self.urls[short_code] = original_url
        self._save_to_disk()
        return short_code

    def read(self, short_code: str) -> Optional[str]:
        """
        Retrieve the original URL for a short code.
        
        Args:
            short_code: The short code to look up
            
        Returns:
            The original URL, or None if not found
        """
        return self.urls.get(short_code)

    def update(self, short_code: str, new_original_url: str) -> None:
        """
        Update the original URL for an existing short code.
        
        Args:
            short_code: The short code to update
            new_original_url: The new original URL
            
        Raises:
            ValueError: If short code doesn't exist or new_original_url is invalid
        """
        if short_code not in self.urls:
            raise ValueError(f"Short code '{short_code}' not found")

        if not new_original_url or not isinstance(new_original_url, str):
            raise ValueError("new_original_url must be a non-empty string")

        self.urls[short_code] = new_original_url
        self._save_to_disk()

    def delete(self, short_code: str) -> None:
        """
        Delete a short code mapping.
        
        Args:
            short_code: The short code to delete
            
        Raises:
            ValueError: If short code doesn't exist
        """
        if short_code not in self.urls:
            raise ValueError(f"Short code '{short_code}' not found")

        del self.urls[short_code]
        self._save_to_disk()

    def list_all(self) -> Dict[str, str]:
        """
        Return all short code to original URL mappings.
        
        Returns:
            Dictionary of all mappings
        """
        return self.urls.copy()

    def __len__(self) -> int:
        """Return the number of stored mappings."""
        return len(self.urls)
