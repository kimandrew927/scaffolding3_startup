"""
app.py
Flask application template for the warm-up assignment

Students need to implement the API endpoints as specified in the assignment.
"""

from flask import Flask, request, jsonify, render_template
from starter_preprocess import TextPreprocessor
import traceback

app = Flask(__name__)
preprocessor = TextPreprocessor()

@app.route('/')
def home():
    """Render a simple HTML form for URL input"""
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Simple health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Text preprocessing service is running"
    })

@app.route('/api/clean', methods=['POST'])
def clean_text():
    """
    TODO: Implement this endpoint for Part 3
    
    API endpoint that accepts a URL and returns cleaned text
    
    Expected JSON input:
        {"url": "https://www.gutenberg.org/files/1342/1342-0.txt"}
    
    Returns JSON:
        {
            "success": true/false,
            "cleaned_text": "...",
            "statistics": {...},
            "summary": "...",
            "error": "..." (if applicable)
        }
    """
    try:
        data = request.get_json(silent=True) or {}
        url = (data.get("url") or "").strip()
        num_sentences = int(data.get("num_sentences", 3))

        if not url:
            return jsonify({"success": False, "error": "Missing 'url' in request JSON"}), 400
        lo = url.lower()
        if not lo.startswith(("http://", "https://")):
            return jsonify({"success": False, "error": "URL must start with http:// or https://"}), 400
        if not lo.endswith(".txt"):
            return jsonify({"success": False, "error": "URL must point to a .txt file"}), 400
        
        raw_text = preprocessor.fetch_from_url(url)                          # fetch
        trimmed = preprocessor.clean_gutenberg_text(raw_text)                # trim headers/footers
        cleaned = preprocessor.normalize_text(trimmed, preserve_sentences=True)  # normalize
        stats = preprocessor.get_text_statistics(cleaned)                    # stats
        summary = preprocessor.create_summary(cleaned, num_sentences)        # summary

        return jsonify({
            "success": True,
            "cleaned_text": cleaned,
            "statistics": stats,
            "summary": summary
        }), 200

    except ValueError as e:
        # Input or validator errors (from our checks or fetch_from_url)
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        # Network / decoding / unexpected errors
        return jsonify({"success": False, "error": str(e)}), 502
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_text():
    """
    TODO: Implement this endpoint for Part 3
    
    API endpoint that accepts raw text and returns statistics only
    
    Expected JSON input:
        {"text": "Your raw text here..."}
    
    Returns JSON:
        {
            "success": true/false,
            "statistics": {...},
            "error": "..." (if applicable)
        }
    """
    try:
     
        data = request.get_json(silent=True) or {}
        raw_text = data.get("text", "")

        if not isinstance(raw_text, str) or not raw_text.strip():
            return jsonify({"success": False, "error": "Missing or empty 'text'"}), 400

        normalized = preprocessor.normalize_text(raw_text, preserve_sentences=True)

        stats = preprocessor.get_text_statistics(normalized)

        return jsonify({"success": True, "statistics": stats}), 200

    except Exception as e:
        return jsonify({"success": False, "error": f"Server error: {str(e)}"}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "Internal server error"
    }), 500

if __name__ == '__main__':
    print("🚀 Starting Text Preprocessing Web Service...")
    print("📖 Available endpoints:")
    print("   GET  /           - Web interface")
    print("   GET  /health     - Health check")
    print("   POST /api/clean  - Clean text from URL")
    print("   POST /api/analyze - Analyze raw text")
    print()
    print("🌐 Open your browser to: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop the server")
    
    app.run(debug=True, port=5000, host='0.0.0.0')