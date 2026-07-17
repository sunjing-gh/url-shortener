# URL Shortener API - Testing Guide

This guide shows how to test the Flask REST API using `curl` commands from your terminal.

## Prerequisites

1. **Install Flask** (required to run the API):
   ```bash
   pip install flask
   ```

2. **Start the server** in one terminal:
   ```bash
   cd url_shortener_project
   python3 app.py
   ```

   You should see:
   ```
   ╔══════════════════════════════════════════════════════════════╗
   ║  URL SHORTENER - Flask REST API                            ║
   ║  Starting server at http://localhost:5000                   ║
   ...
   ```

3. **Open a second terminal** for testing (keep the server running in the first)

---

## Testing Endpoints

### 1. Health Check

Test if the server is alive:

```bash
curl http://localhost:5000/health
```

**Expected response:**
```json
{
  "status": "ok",
  "total_urls": 0
}
```

---

### 2. Create a Short URL

**Create with auto-generated short code:**

```bash
curl -X POST http://localhost:5000/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"original_url": "https://github.com/anthropics/anthropic-sdk-python"}'
```

**Expected response (201 Created):**
```json
{
  "success": true,
  "data": {
    "short_code": "a1b2c3",
    "original_url": "https://github.com/anthropics/anthropic-sdk-python"
  }
}
```

**Create with custom short code:**

```bash
curl -X POST http://localhost:5000/api/shorten \
  -H "Content-Type: application/json" \
  -d '{
    "original_url": "https://www.python.org",
    "custom_short_code": "py"
  }'
```

**Expected response:**
```json
{
  "success": true,
  "data": {
    "short_code": "py",
    "original_url": "https://www.python.org"
  }
}
```

**Error - missing original_url:**

```bash
curl -X POST http://localhost:5000/api/shorten \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Expected response (400 Bad Request):**
```json
{
  "success": false,
  "error": "original_url is required"
}
```

---

### 3. Lookup a Short Code

```bash
curl http://localhost:5000/api/lookup/py
```

**Expected response (200 OK):**
```json
{
  "success": true,
  "data": {
    "short_code": "py",
    "original_url": "https://www.python.org"
  }
}
```

**Error - short code not found:**

```bash
curl http://localhost:5000/api/lookup/notexist
```

**Expected response (404 Not Found):**
```json
{
  "success": false,
  "error": "Short code 'notexist' not found"
}
```

---

### 4. Update a Short Code

```bash
curl -X PUT http://localhost:5000/api/update/py \
  -H "Content-Type: application/json" \
  -d '{"original_url": "https://python.org/docs"}'
```

**Expected response (200 OK):**
```json
{
  "success": true,
  "data": {
    "short_code": "py",
    "original_url": "https://python.org/docs"
  }
}
```

---

### 5. List All Mappings

```bash
curl http://localhost:5000/api/all
```

**Expected response (200 OK):**
```json
{
  "success": true,
  "data": {
    "count": 2,
    "urls": {
      "py": "https://python.org/docs",
      "a1b2c3": "https://github.com/anthropics/anthropic-sdk-python"
    }
  }
}
```

---

### 6. Delete a Short Code

```bash
curl -X DELETE http://localhost:5000/api/delete/py
```

**Expected response (200 OK):**
```json
{
  "success": true,
  "data": {
    "message": "Short code 'py' deleted"
  }
}
```

**Verify it's deleted:**

```bash
curl http://localhost:5000/api/lookup/py
```

**Expected response (404 Not Found):**
```json
{
  "success": false,
  "error": "Short code 'py' not found"
}
```

---

## Testing Flow (Step-by-Step)

Copy and paste these commands in order to test the complete workflow:

```bash
# 1. Check health
curl http://localhost:5000/health

# 2. Create first URL with custom code
curl -X POST http://localhost:5000/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"original_url": "https://github.com", "custom_short_code": "gh"}'

# 3. Create second URL with auto-generated code
curl -X POST http://localhost:5000/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"original_url": "https://stackoverflow.com"}'

# 4. Look up first URL
curl http://localhost:5000/api/lookup/gh

# 5. List all URLs
curl http://localhost:5000/api/all

# 6. Update first URL
curl -X PUT http://localhost:5000/api/update/gh \
  -H "Content-Type: application/json" \
  -d '{"original_url": "https://github.com/anthropics"}'

# 7. Look up updated URL
curl http://localhost:5000/api/lookup/gh

# 8. Delete first URL
curl -X DELETE http://localhost:5000/api/delete/gh

# 9. Verify deletion
curl http://localhost:5000/api/lookup/gh

# 10. List remaining URLs
curl http://localhost:5000/api/all
```

---

## Using Postman (Alternative to curl)

If you prefer a GUI, download [Postman](https://www.postman.com/downloads/) and:

1. Create a new request
2. Set method to POST
3. URL: `http://localhost:5000/api/shorten`
4. Body → raw → JSON
5. Paste:
   ```json
   {
     "original_url": "https://example.com",
     "custom_short_code": "ex"
   }
   ```
6. Click Send

---

## Understanding HTTP Status Codes

| Code | Meaning | When Used |
|------|---------|-----------|
| 200 | OK | Successful GET, PUT, DELETE |
| 201 | Created | Successful POST (resource created) |
| 400 | Bad Request | Missing/invalid parameters |
| 404 | Not Found | Short code doesn't exist |
| 405 | Method Not Allowed | Wrong HTTP verb (e.g. GET on POST endpoint) |
| 500 | Server Error | Unexpected error in the app |

---

## Debugging Tips

**See what the server is logging:**
Look at the terminal where you ran `python3 app.py`. You'll see entries like:
```
INFO:__main__:Created: py -> https://www.python.org
INFO:__main__:Lookup: py -> https://www.python.org
WARNING:__main__:Lookup failed: notexist not found
```

**Test a malformed request:**
```bash
curl -X POST http://localhost:5000/api/shorten \
  -H "Content-Type: application/json" \
  -d 'not valid json'
```

**Stop the server:**
Press `CTRL+C` in the terminal running `python3 app.py`

---

## Key Learning Points

This API demonstrates:

1. **REST design:** Each endpoint has a clear purpose (CRUD operation)
2. **HTTP verbs:** POST (create), GET (read), PUT (update), DELETE (delete)
3. **Status codes:** Returning correct codes helps clients know what happened
4. **JSON responses:** Standardized format with `success`, `data`, `error` keys
5. **Error handling:** Try/except blocks + meaningful error messages
6. **Logging:** Track what's happening in the server for debugging
7. **Modularity:** The Flask layer wraps the URLShortener class cleanly
