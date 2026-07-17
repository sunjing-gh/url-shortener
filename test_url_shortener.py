"""
URL Shortener with SQLite Database Backend.

This module provides CRUD operations for URL shortening using SQLite for
persistent storage instead of JSON files. Suitable for production deployment.

Usage:
    from url_shortener_sqlite import URLShortener
    shortener = URLShortener(db_path="urls.db")
    code = shortener.create("https://example.com")
"""

import sqlite3
import hashlib
import os
import logging
from typing import Optional, Dict
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class URLShortener:
    """Manages short URLs using SQLite database."""

    def __init__(self, db_path: str = "urls.db", debug: bool = False):
        """
        Initialize the URL shortener with SQLite database.
        
        Args:
            db_path: Path to SQLite database file
            debug: Enable debug logging
        """
        self.db_path = db_path
        self.debug = debug
        
        if debug:
            logging.basicConfig(level=logging.DEBUG)
        
        # Create database and schema if not exists
        self._init_database()
        logger.info(f"URLShortener initialized with database: {db_path}")

    @contextmanager
    def _get_connection(self):
        """
        Context manager for database connections.
        Ensures connection is closed properly.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Access rows as dictionaries
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()

    def _init_database(self) -> None:
        """Create database schema if it doesn't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Create urls table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS urls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    short_code TEXT UNIQUE NOT NULL,
                    original_url TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    lookup_count INTEGER DEFAULT 0
                )
            """)
            
            # Create index for faster lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_short_code 
                ON urls(short_code)
            """)
            
            logger.debug("Database schema initialized")

    def _generate_short_code(self, original_url: str) -> str:
        """
        Generate a unique short code from the original URL.
        
        Args:
            original_url: The URL to shorten
            
        Returns:
            A short code string
        """
        hash_obj = hashlib.md5(original_url.encode())
        return hash_obj.hexdigest()[:6]

    def create(self, original_url: str, custom_short_code: Optional[str] = None) -> str:
        """
        Create a new short URL mapping.
        
        Args:
            original_url: The full URL to shorten
            custom_short_code: Optional custom short code
            
        Returns:
            The short code
            
        Raises:
            ValueError: If URL is invalid or short code already exists
        """
        if not original_url or not isinstance(original_url, str):
            raise ValueError("original_url must be a non-empty string")

        short_code = custom_short_code or self._generate_short_code(original_url)

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO urls (short_code, original_url) VALUES (?, ?)",
                    (short_code, original_url)
                )
            
            logger.info(f"Created: {short_code} -> {original_url}")
            return short_code
        
        except sqlite3.IntegrityError:
            raise ValueError(f"Short code '{short_code}' already exists")

    def read(self, short_code: str) -> Optional[str]:
        """
        Retrieve the original URL for a short code.
        
        Args:
            short_code: The short code to look up
            
        Returns:
            The original URL, or None if not found
        """
        if not short_code:
            return None

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT original_url FROM urls WHERE short_code = ?",
                (short_code,)
            )
            row = cursor.fetchone()
            
            if row:
                # Increment lookup count
                cursor.execute(
                    "UPDATE urls SET lookup_count = lookup_count + 1 WHERE short_code = ?",
                    (short_code,)
                )
                logger.info(f"Lookup: {short_code}")
                return row[0]
            
            logger.debug(f"Lookup failed: {short_code} not found")
            return None

    def update(self, short_code: str, new_original_url: str) -> None:
        """
        Update the original URL for an existing short code.
        
        Args:
            short_code: The short code to update
            new_original_url: The new original URL
            
        Raises:
            ValueError: If short code doesn't exist or URL is invalid
        """
        if not short_code:
            raise ValueError("short_code is required")
        
        if not new_original_url or not isinstance(new_original_url, str):
            raise ValueError("new_original_url must be a non-empty string")

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE urls SET original_url = ? WHERE short_code = ?",
                (new_original_url, short_code)
            )
            
            if cursor.rowcount == 0:
                raise ValueError(f"Short code '{short_code}' not found")
            
            logger.info(f"Updated: {short_code} -> {new_original_url}")

    def delete(self, short_code: str) -> None:
        """
        Delete a short code mapping.
        
        Args:
            short_code: The short code to delete
            
        Raises:
            ValueError: If short code doesn't exist
        """
        if not short_code:
            raise ValueError("short_code is required")

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM urls WHERE short_code = ?", (short_code,))
            
            if cursor.rowcount == 0:
                raise ValueError(f"Short code '{short_code}' not found")
            
            logger.info(f"Deleted: {short_code}")

    def list_all(self) -> Dict[str, str]:
        """
        Return all short code to original URL mappings.
        
        Returns:
            Dictionary of all mappings
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT short_code, original_url FROM urls ORDER BY created_at DESC")
            rows = cursor.fetchall()
            
            return {row[0]: row[1] for row in rows}

    def get_stats(self, short_code: str) -> Optional[Dict]:
        """
        Get usage statistics for a short code.
        
        Args:
            short_code: The short code
            
        Returns:
            Dictionary with stats or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT short_code, original_url, created_at, lookup_count FROM urls WHERE short_code = ?",
                (short_code,)
            )
            row = cursor.fetchone()
            
            if row:
                return {
                    "short_code": row[0],
                    "original_url": row[1],
                    "created_at": row[2],
                    "lookup_count": row[3]
                }
            return None

    def __len__(self) -> int:
        """Return the total number of stored mappings."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM urls")
            return cursor.fetchone()[0]
        
# --- Put this at the very bottom of test.py ---
if __name__ == "__main__":
    print("--- Starting URL Shortener Test ---")
    
    # 1. Initialize the shortener in debug mode to see database logs
    shortener = URLShortener(db_path="test_urls.db", debug=True)
    
    # 2. Test creating a short link
    try:
        my_code = shortener.create("https://google.com")
        print(f"Success! Generated code: {my_code}")
        
        # 3. Test reading it back
        original = shortener.read(my_code)
        print(f"Retrieved original URL: {original}")
        
        # 4. Check how many items are in the DB
        print(f"Total links stored: {len(shortener)}")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        
    finally:
        # Cleanup the test database file afterwards if you want
        if os.path.exists("test_urls.db"):
            os.remove("test_urls.db")