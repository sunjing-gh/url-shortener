# URL Shortener

A simple Python application for creating and managing short URL mappings.

## Features

- **Create**: Generate short codes for long URLs (auto or custom)
- **Read**: Look up the original URL from a short code
- **Update**: Change the original URL for an existing short code
- **Delete**: Remove a short code mapping
- **Persist**: All mappings saved to JSON file automatically
- **List**: View all stored mappings

## Project Structure

```
url_shortener_project/
├── url_shortener.py          # Core CRUD module
├── test_url_shortener.py     # Unit tests
├── main.py                   # Interactive CLI
├── urls.json                 # Storage file (auto-created)
└── README.md                 # This file
```

## Quick Start

### 1. Run the Interactive CLI

```bash
python3 main.py
```

This launches an interactive menu where you can:
- Create short URLs
- Look up original URLs
- Update mappings
- Delete mappings
- View all stored URLs

### 2. Run the Tests

```bash
# With pytest (if installed)
python3 -m pytest test_url_shortener.py -v

# Without pytest (uses unittest)
python3 test_url_shortener.py
```

### 3. Use as a Module in Your Own Code

```python
from url_shortener import URLShortener

shortener = URLShortener()

# Create
code = shortener.create("https://github.com/anthropics/anthropic-sdk-python", "gh-api")

# Read
url = shortener.read("gh-api")
print(url)  # https://github.com/anthropics/anthropic-sdk-python

# Update
shortener.update("gh-api", "https://github.com/anthropics/new-url")

# Delete
shortener.delete("gh-api")

# List all
all_urls = shortener.list_all()
```

## API Reference

### URLShortener Class

#### `__init__(storage_file="urls.json")`
Initialize the shortener with optional custom storage file.

#### `create(original_url, custom_short_code=None) -> str`
Create a new mapping. Returns the short code.
- Auto-generates a short code if not provided
- Raises `ValueError` if short code already exists

#### `read(short_code) -> Optional[str]`
Retrieve the original URL. Returns None if not found.

#### `update(short_code, new_original_url) -> None`
Update the original URL for a short code.
- Raises `ValueError` if short code doesn't exist

#### `delete(short_code) -> None`
Delete a short code mapping.
- Raises `ValueError` if short code doesn't exist

#### `list_all() -> Dict[str, str]`
Return all mappings as a dictionary.

## Learning Points

This project demonstrates:

1. **CRUD Operations**: Create, Read, Update, Delete patterns
2. **File I/O**: Reading and writing JSON files
3. **Error Handling**: Raising and catching exceptions
4. **Type Hints**: Modern Python type annotations
5. **Documentation**: Docstrings and README
6. **Testing**: Unit tests with unittest
7. **Modularity**: Separating concerns (core module vs. CLI)

## Next Steps

Consider these enhancements:

- Validate URLs (check if they're valid HTTP/HTTPS)
- Add URL analytics (track how many times each short URL was accessed)
- Implement with a database (SQLite instead of JSON)
- Build a web API (Flask or FastAPI)
- Add CLI arguments instead of interactive menu
