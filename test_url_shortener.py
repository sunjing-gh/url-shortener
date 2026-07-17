"""
Unit tests for URL Shortener module.

Run with: python3 -m pytest test_url_shortener.py -v
Or without pytest: python3 test_url_shortener.py
"""

import unittest
import os
import json
from url_shortener import URLShortener


class TestURLShortener(unittest.TestCase):
    """Test cases for URLShortener class."""

    def setUp(self):
        """Create a fresh URLShortener instance for each test."""
        # Use a test-specific file so tests don't interfere with each other
        self.test_storage = "test_urls.json"
        self.shortener = URLShortener(storage_file=self.test_storage)

    def tearDown(self):
        """Clean up test files after each test."""
        if os.path.exists(self.test_storage):
            os.remove(self.test_storage)

    def test_create_auto_generate_short_code(self):
        """Test creating a short URL with auto-generated code."""
        url = "https://www.example.com/very/long/path"
        short_code = self.shortener.create(url)
        
        # Should return a non-empty string
        self.assertIsInstance(short_code, str)
        self.assertTrue(len(short_code) > 0)

    def test_create_custom_short_code(self):
        """Test creating a short URL with custom code."""
        url = "https://github.com/anthropics/anthropic-sdk-python"
        short_code = self.shortener.create(url, custom_short_code="gh")
        
        self.assertEqual(short_code, "gh")

    def test_create_duplicate_short_code_raises_error(self):
        """Test that duplicate short codes raise an error."""
        url1 = "https://example.com/1"
        url2 = "https://example.com/2"
        
        self.shortener.create(url1, custom_short_code="dup")
        
        with self.assertRaises(ValueError) as context:
            self.shortener.create(url2, custom_short_code="dup")
        
        self.assertIn("already exists", str(context.exception))

    def test_create_empty_url_raises_error(self):
        """Test that empty URLs raise an error."""
        with self.assertRaises(ValueError):
            self.shortener.create("")

    def test_read_existing_url(self):
        """Test retrieving an existing URL."""
        url = "https://www.python.org"
        short_code = self.shortener.create(url, custom_short_code="py")
        
        retrieved_url = self.shortener.read("py")
        self.assertEqual(retrieved_url, url)

    def test_read_nonexistent_url(self):
        """Test that reading a nonexistent URL returns None."""
        result = self.shortener.read("nonexistent")
        self.assertIsNone(result)

    def test_update_existing_mapping(self):
        """Test updating an existing short code's URL."""
        short_code = "old"
        old_url = "https://old.example.com"
        new_url = "https://new.example.com"
        
        self.shortener.create(old_url, custom_short_code=short_code)
        self.shortener.update(short_code, new_url)
        
        self.assertEqual(self.shortener.read(short_code), new_url)

    def test_update_nonexistent_mapping_raises_error(self):
        """Test that updating a nonexistent mapping raises an error."""
        with self.assertRaises(ValueError) as context:
            self.shortener.update("nonexistent", "https://example.com")
        
        self.assertIn("not found", str(context.exception))

    def test_update_invalid_url_raises_error(self):
        """Test that updating with an invalid URL raises an error."""
        short_code = "test"
        self.shortener.create("https://example.com", custom_short_code=short_code)
        
        with self.assertRaises(ValueError):
            self.shortener.update(short_code, "")

    def test_delete_existing_mapping(self):
        """Test deleting an existing mapping."""
        short_code = "todel"
        self.shortener.create("https://example.com", custom_short_code=short_code)
        
        # Verify it exists
        self.assertIsNotNone(self.shortener.read(short_code))
        
        # Delete it
        self.shortener.delete(short_code)
        
        # Verify it's gone
        self.assertIsNone(self.shortener.read(short_code))

    def test_delete_nonexistent_mapping_raises_error(self):
        """Test that deleting a nonexistent mapping raises an error."""
        with self.assertRaises(ValueError) as context:
            self.shortener.delete("nonexistent")
        
        self.assertIn("not found", str(context.exception))

    def test_list_all_mappings(self):
        """Test listing all stored mappings."""
        urls = {
            "py": "https://python.org",
            "gh": "https://github.com",
            "so": "https://stackoverflow.com"
        }
        
        for short, full in urls.items():
            self.shortener.create(full, custom_short_code=short)
        
        all_mappings = self.shortener.list_all()
        self.assertEqual(len(all_mappings), 3)
        self.assertEqual(all_mappings["py"], urls["py"])

    def test_persistence_across_instances(self):
        """Test that data persists when creating a new instance."""
        # Create and save
        url = "https://persistent.example.com"
        short_code = self.shortener.create(url, custom_short_code="persist")
        
        # Create a new instance with the same storage file
        shortener2 = URLShortener(storage_file=self.test_storage)
        
        # Verify the data was loaded
        self.assertEqual(shortener2.read("persist"), url)
        self.assertEqual(len(shortener2), 1)


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)
