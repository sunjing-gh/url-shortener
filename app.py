"""
Production-ready Flask REST API for URL Shortener with SQLite backend.

Configuration via environment variables (.env file).

Run with: python3 app_sqlite.py

Environment variables:
  FLASK_PORT: Port to run on (default: 8080)
  DATABASE_PATH: Path to SQLite database (default: urls.db)
  FLASK_DEBUG: Enable debug mode (default: False)
"""

import os
import logging
from flask import Flask, request, jsonify
from url_shortener import URLShortener
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Configuration from environment variables
DATABASE_PATH = os.getenv('DATABASE_PATH', 'urls.db')
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
FLASK_HOST = os.getenv('FLASK_HOST', '127.0.0.1')
FLASK_PORT = int(os.getenv('FLASK_PORT', 8080))
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Initialize URL shortener with SQLite backend
shortener = URLShortener(db_path=DATABASE_PATH, debug=FLASK_DEBUG)

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info(f"Starting Flask API with SQLite backend")
logger.info(f"Database: {DATABASE_PATH}")
logger.info(f"Debug mode: {FLASK_DEBUG}")


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
    Health check endpoint.
    
    Response:
        {
            "status": "ok",
            "database": "SQLite",
            "total_urls": 5
        }
    """
    try:
        total_urls = len(shortener)
        return jsonify({
            "status": "ok",
            "database": "SQLite",
            "total_urls": total_urls,
            "database_path": DATABASE_PATH
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return error_response("Database connection failed", 500)


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
        logger.info(f"API: Created short URL {short_code}")
        
        return success_response({
            "short_code": short_code,
            "original_url": original_url
        }, 201)
    
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        return error_response(str(e), 400)
    except Exception as e:
        logger.error(f"Unexpected error in shorten: {e}")
        return error_response("Internal server error", 500)


@app.route('/api/lookup/<short_code>', methods=['GET'])
def lookup(short_code):
    """
    Retrieve the original URL for a short code.
    
    Path parameter:
        short_code: The short code to look up
    
    Response (200 OK):
        {
            "success": true,
            "data": {
                "short_code": "ex",
                "original_url": "https://example.com/very/long/path",
                "lookup_count": 3
            }
        }
    """
    if not short_code:
        return error_response("short_code is required", 400)

    original_url = shortener.read(short_code)
    
    if original_url is None:
        logger.info(f"API: Lookup failed for {short_code}")
        return error_response(f"Short code '{short_code}' not found", 404)
    
    # Get stats
    stats = shortener.get_stats(short_code)
    
    logger.info(f"API: Lookup success for {short_code}")
    return success_response({
        "short_code": short_code,
        "original_url": original_url,
        "lookup_count": stats['lookup_count'] if stats else 0
    }, 200)


@app.route('/api/update/<short_code>', methods=['PUT'])
def update(short_code):
    """
    Update the original URL for an existing short code.
    
    Path parameter:
        short_code: The short code to update
    
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
        logger.info(f"API: Updated {short_code}")
        
        return success_response({
            "short_code": short_code,
            "original_url": new_url
        }, 200)
    
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        return error_response(str(e), 404)
    except Exception as e:
        logger.error(f"Unexpected error in update: {e}")
        return error_response("Internal server error", 500)


@app.route('/api/delete/<short_code>', methods=['DELETE'])
def delete(short_code):
    """
    Delete a short code mapping.
    
    Path parameter:
        short_code: The short code to delete
    
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
        logger.info(f"API: Deleted {short_code}")
        
        return success_response({
            "message": f"Short code '{short_code}' deleted"
        }, 200)
    
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        return error_response(str(e), 404)
    except Exception as e:
        logger.error(f"Unexpected error in delete: {e}")
        return error_response("Internal server error", 500)


@app.route('/api/all', methods=['GET'])
def list_all():
    """
    Retrieve all short code mappings with usage statistics.
    
    Response (200 OK):
        {
            "success": true,
            "data": {
                "count": 3,
                "urls": {
                    "ex": {
                        "original_url": "https://example.com",
                        "lookup_count": 5
                    },
                    ...
                }
            }
        }
    """
    try:
        all_urls = shortener.list_all()
        
        # Enrich with stats
        urls_with_stats = {}
        for code, url in all_urls.items():
            stats = shortener.get_stats(code)
            urls_with_stats[code] = {
                "original_url": url,
                "lookup_count": stats['lookup_count'] if stats else 0,
                "created_at": stats['created_at'] if stats else None
            }
        
        return success_response({
            "count": len(all_urls),
            "urls": urls_with_stats
        }, 200)
    except Exception as e:
        logger.error(f"Error listing URLs: {e}")
        return error_response("Internal server error", 500)


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
    print(f"""
    ╔══════════════════════════════════════════════════════════════╗
    ║  URL SHORTENER - Flask REST API (SQLite Backend)            ║
    ║                                                              ║
    ║  Configuration:                                              ║
    ║    Host: {FLASK_HOST}                                       ║
    ║    Port: {FLASK_PORT}                                          ║
    ║    Database: {DATABASE_PATH}                                  ║
    ║    Debug: {FLASK_DEBUG}                                       ║
    ║                                                              ║
    ║  Starting server at http://{FLASK_HOST}:{FLASK_PORT}                     ║
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
    
    app.run(debug=FLASK_DEBUG, host=FLASK_HOST, port=FLASK_PORT)