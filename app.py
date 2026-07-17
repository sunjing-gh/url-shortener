"""
Flask REST API for URL Shortener.

Endpoints:
  POST   /api/shorten           - Create a short URL
  GET    /api/lookup/<code>     - Retrieve original URL
  PUT    /api/update/<code>     - Update a short URL
  DELETE /api/delete/<code>     - Delete a short URL
  GET    /api/all               - List all mappings
  GET    /health                - Health check

Run with: python3 app.py
Then test with curl or access http://localhost:5000 in browser.
"""

from flask import Flask, request, jsonify
from url_shortener import URLShortener
import logging

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Initialize URL shortener
shortener = URLShortener()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def success_response(data, status_code=200):
    """Return a standardized success response."""
    return jsonify({
        "success": True,
        "data": data
    }), status_code


def error_response(message, status_code=400):
    """Return a standardized error response."""
    return jsonify({
        "success": False,
        "error": message
    }), status_code


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint. Always returns 200 OK.
    
    Response:
        {
            "status": "ok",
            "total_urls": <count>
        }
    """
    return jsonify({
        "status": "ok",
        "total_urls": len(shortener)
    }), 200


@app.route('/api/shorten', methods=['POST'])
def shorten():
    """
    Create a short URL mapping.
    
    Request body:
        {
            "original_url": "https://example.com/very/long/path",
            "custom_short_code": "ex" (optional)
        }
    
    Response (201 Created):
        {
            "success": true,
            "data": {
                "short_code": "ex",
                "original_url": "https://example.com/very/long/path"
            }
        }
    """
    data = request.get_json() or {}
    original_url = data.get('original_url', '').strip()
    custom_short_code = data.get('custom_short_code', '').strip() or None

    if not original_url:
        return error_response("original_url is required", 400)

    try:
        short_code = shortener.create(original_url, custom_short_code)
        logger.info(f"Created: {short_code} -> {original_url}")
        
        return success_response({
            "short_code": short_code,
            "original_url": original_url
        }, 201)
    
    except ValueError as e:
        logger.warning(f"Validation error in shorten: {e}")
        return error_response(str(e), 400)
    except Exception as e:
        logger.error(f"Unexpected error in shorten: {e}")
        return error_response("Internal server error", 500)


@app.route('/api/lookup/<short_code>', methods=['GET'])
def lookup(short_code):
    """
    Retrieve the original URL for a short code.
    
    Path parameter:
        short_code: The short code to look up (e.g., "/api/lookup/ex")
    
    Response (200 OK):
        {
            "success": true,
            "data": {
                "short_code": "ex",
                "original_url": "https://example.com/very/long/path"
            }
        }
    
    Response (404 Not Found):
        {
            "success": false,
            "error": "Short code 'xyz' not found"
        }
    """
    if not short_code:
        return error_response("short_code is required", 400)

    original_url = shortener.read(short_code)
    
    if original_url is None:
        logger.info(f"Lookup failed: {short_code} not found")
        return error_response(f"Short code '{short_code}' not found", 404)
    
    logger.info(f"Lookup: {short_code} -> {original_url}")
    return success_response({
        "short_code": short_code,
        "original_url": original_url
    }, 200)


@app.route('/api/update/<short_code>', methods=['PUT'])
def update(short_code):
    """
    Update the original URL for an existing short code.
    
    Path parameter:
        short_code: The short code to update (e.g., "/api/update/ex")
    
    Request body:
        {
            "original_url": "https://new-url.com"
        }
    
    Response (200 OK):
        {
            "success": true,
            "data": {
                "short_code": "ex",
                "original_url": "https://new-url.com"
            }
        }
    """
    if not short_code:
        return error_response("short_code is required", 400)

    data = request.get_json() or {}
    new_url = data.get('original_url', '').strip()

    if not new_url:
        return error_response("original_url is required", 400)

    try:
        shortener.update(short_code, new_url)
        logger.info(f"Updated: {short_code} -> {new_url}")
        
        return success_response({
            "short_code": short_code,
            "original_url": new_url
        }, 200)
    
    except ValueError as e:
        logger.warning(f"Validation error in update: {e}")
        return error_response(str(e), 404)
    except Exception as e:
        logger.error(f"Unexpected error in update: {e}")
        return error_response("Internal server error", 500)


@app.route('/api/delete/<short_code>', methods=['DELETE'])
def delete(short_code):
    """
    Delete a short code mapping.
    
    Path parameter:
        short_code: The short code to delete (e.g., "/api/delete/ex")
    
    Response (200 OK):
        {
            "success": true,
            "data": {
                "message": "Short code 'ex' deleted"
            }
        }
    """
    if not short_code:
        return error_response("short_code is required", 400)

    try:
        shortener.delete(short_code)
        logger.info(f"Deleted: {short_code}")
        
        return success_response({
            "message": f"Short code '{short_code}' deleted"
        }, 200)
    
    except ValueError as e:
        logger.warning(f"Validation error in delete: {e}")
        return error_response(str(e), 404)
    except Exception as e:
        logger.error(f"Unexpected error in delete: {e}")
        return error_response("Internal server error", 500)


@app.route('/api/all', methods=['GET'])
def list_all():
    """
    Retrieve all short code mappings.
    
    Response (200 OK):
        {
            "success": true,
            "data": {
                "count": 3,
                "urls": {
                    "ex": "https://example.com",
                    "py": "https://python.org",
                    "gh": "https://github.com"
                }
            }
        }
    """
    all_urls = shortener.list_all()
    
    return success_response({
        "count": len(all_urls),
        "urls": all_urls
    }, 200)


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(e):
    """Handle 404 Not Found errors."""
    return error_response("Endpoint not found", 404)


@app.errorhandler(405)
def method_not_allowed(e):
    """Handle 405 Method Not Allowed errors."""
    return error_response("HTTP method not allowed", 405)


@app.errorhandler(500)
def internal_error(e):
    """Handle 500 Internal Server Error."""
    logger.error(f"Internal server error: {e}")
    return error_response("Internal server error", 500)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║  URL SHORTENER - Flask REST API                            ║
    ║                                                              ║
    ║  Starting server at http://localhost:8080                   ║
    ║                                                              ║
    ║  Endpoints:                                                  ║
    ║    POST   /api/shorten         - Create short URL           ║
    ║    GET    /api/lookup/<code>   - Lookup original URL        ║
    ║    PUT    /api/update/<code>   - Update mapping             ║
    ║    DELETE /api/delete/<code>   - Delete mapping             ║
    ║    GET    /api/all             - List all URLs              ║
    ║    GET    /health              - Health check               ║
    ║                                                              ║
    ║  Press CTRL+C to stop                                        ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    app.run(debug=True, host='127.0.0.1', port=8080)
