# Getting Started - URL Shortener Project

## What You Have

You now have a **complete URL shortener application** with two ways to use it:

1. **Interactive CLI** (`main.py`) — Type in commands interactively
2. **Flask REST API** (`app.py`) — HTTP endpoints you can call from anywhere

## Quick Start (5 Minutes)

### Option A: Interactive CLI (Simplest)

**In VS Code terminal:**

```bash
python main.py
```

Then:
- Select option 1 → Enter `https://github.com` → Press Enter (auto-generate code)
- Select option 2 → Enter the code from step 1 → See the URL
- Try all the other options (update, delete, list all)

**This teaches you:** How CRUD operations work in the core module.

---

### Option B: Flask REST API (More Advanced)

**Terminal 1 (starts the server):**
```bash
python app.py
```

You'll see:
```
╔══════════════════════════════════════════════════════════════╗
║  URL SHORTENER - Flask REST API                            ║
║  Starting server at http://localhost:5000                   ║
```

**Terminal 2 (test the API):**

```bash
# Create a short URL
curl -X POST http://localhost:5000/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"original_url": "https://github.com", "custom_short_code": "gh"}'

# Look it up
curl http://localhost:5000/api/lookup/gh

# List all
curl http://localhost:5000/api/all

# Update it
curl -X PUT http://localhost:5000/api/update/gh \
  -H "Content-Type: application/json" \
  -d '{"original_url": "https://github.com/anthropics"}'

# Delete it
curl -X DELETE http://localhost:5000/api/delete/gh
```

**This teaches you:** How to build a web API, HTTP design, JSON responses.

---

## Full Project Structure

```
url_shortener_project/
├── url_shortener.py          ← Core module (CRUD logic)
├── test_url_shortener.py     ← Unit tests (13 tests, all passing)
├── main.py                   ← Interactive CLI
├── app.py                    ← Flask REST API (NEW)
├── urls.json                 ← Data storage (auto-created)
├── README.md                 ← Project overview
├── GETTING_STARTED.md        ← This file
└── API_TESTING.md            ← Testing guide for API
```

---

## Step-by-Step Learning Path

### Week 1: Understand the Core

1. ✅ Run tests: `python test_url_shortener.py`
2. ✅ Run CLI: `python main.py`
3. **Read through `url_shortener.py` line by line**
   - Look for Python patterns: type hints, docstrings, error handling
   - Compare with Java code you've written
   - Ask me questions on anything confusing

### Week 2: Learn the Web Layer

1. Install Flask: `pip install flask --break-system-packages`
2. Run the API: `python app.py`
3. Test it with curl commands (see `API_TESTING.md`)
4. **Read through `app.py` and understand:**
   - How HTTP verbs (POST, GET, PUT, DELETE) map to CRUD
   - How decorators (`@app.route`) work
   - How Flask wraps the core module
   - Error handling and status codes

### Week 3: Enhance & Deploy

1. Add features (see "Next Steps" section)
2. Push to GitHub
3. Test locally

---

## Common Questions

**Q: Why two files (`url_shortener.py` and `app.py`)?**

A: Separation of concerns.
- `url_shortener.py` = Business logic (the "what")
- `app.py` = Web interface (the "how it's accessed")

You can use the core module standalone, in a CLI, via REST API, or even in a desktop app—it doesn't care.

**Q: Why does `python` fail but `python3` works?**

A: On Mac/Linux, `python` is often Python 2 (old), `python3` is Python 3 (current). Always use `python3` to be safe.

**Q: Where is my data stored?**

A: In `urls.json` in the same folder. It's automatically created on first run and persists between sessions.

**Q: Can I change the filename?**

A: Yes! Open `main.py` and change:
```python
shortener = URLShortener()  # uses urls.json
```
to:
```python
shortener = URLShortener("my_urls.json")  # uses my_urls.json
```

**Q: Do I need to know HTTP to use the Flask API?**

A: No, but it helps. You need to know:
- `POST` = Create something
- `GET` = Read something
- `PUT` = Update something
- `DELETE` = Delete something

Status codes:
- `200` = Success
- `201` = Created (after POST)
- `400` = Your request was bad
- `404` = Not found
- `500` = Server error

---

## Next Steps (Pick One)

### Easy: Add URL Validation
Modify `url_shortener.py` to validate that URLs start with `http://` or `https://`:
```python
if not original_url.startswith(('http://', 'https://')):
    raise ValueError("URL must start with http:// or https://")
```

### Medium: Add Usage Tracking
Add a counter to track how many times each short URL is looked up:
```python
def read(self, short_code: str) -> Optional[str]:
    if short_code in self.urls:
        self.usage_count[short_code] += 1  # NEW: track
        self._save_to_disk()
    return self.urls.get(short_code)
```

### Hard: Use SQLite Instead of JSON
Replace JSON file storage with a proper database (SQLite):
```python
import sqlite3

class URLShortener:
    def __init__(self):
        self.db = sqlite3.connect("urls.db")
        self.cursor = self.db.cursor()
        self._create_table()
```

---

## Troubleshooting

**Error: `ModuleNotFoundError: No module named 'flask'`**

Solution:
```bash
pip install flask --break-system-packages
```

**Error: `Port 5000 already in use`**

Solution: Change the port in `app.py`, last line:
```python
app.run(debug=True, host='127.0.0.1', port=5001)  # Use 5001 instead
```

**Error: `FileNotFoundError: urls.json not found`**

This is OK—it creates the file on first run. Just run again.

**API returns `{"success": false, "error": "..."}`**

This is normal—you either sent bad data or tried an operation that failed. Check the error message and `API_TESTING.md` for examples.

---

## Ready to Learn?

1. **Pick Option A or B above** and run it
2. **Read the code** and ask questions as you go
3. **Try modifying the code** — change error messages, add print statements, see what breaks
4. **Push to GitHub** when you're ready

You've got this! 🚀
