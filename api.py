import os
import re
import json
import requests
from flask import Flask, request, Response, url_for
from datetime import datetime

app = Flask(__name__)

# ========== CONFIG ==========
OWNER_NAME = "@notxsatvir"
CHANNEL = "https://t.me/notxsatvir"

# ========== HELPERS ==========
def is_valid_gst(gst_number: str) -> bool:
    """Basic GST validation (15 characters, format check)"""
    gst = gst_number.strip().upper()
    # GST format: 15 characters (2 state code + 10 PAN + 1 entity code + 2 checksum)
    pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[0-9]{1}[A-Z]{1}[0-9A-Z]{1}$'
    return bool(re.match(pattern, gst))

def fetch_gst_info(gst_number: str):
    """Fetch GST information from public API"""
    
    # Using public GST API (free, no key required)
    try:
        # Method 1: Public GST Search API
        url = f"https://publigst.in/api/v1/gstin/{gst_number}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "source": "publigst.in",
                "data": data
            }
    except:
        pass
    
    # Method 2: MasterGST API (free tier)
    try:
        url = f"https://api.mastergst.com/v1/search/gstin/{gst_number}"
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            return {
                "success": True,
                "source": "mastergst.com",
                "data": response.json()
            }
    except:
        pass
    
    # Method 3: Return demo data if API fails (for educational purpose)
    return {
        "success": False,
        "error": "GST API temporarily unavailable. Try again later.",
        "demo_data": {
            "gstin": gst_number,
            "trade_name": "Demo Business Name",
            "legal_name": "Demo Legal Name",
            "status": "Active",
            "state": "Delhi",
            "state_code": gst_number[:2] if len(gst_number) >= 2 else "07"
        }
    }

# ========== RESPONSE FORMATTER ==========
def make_response(success, data=None, error=None, query=None):
    return {
        "success": success,
        "owner": OWNER_NAME,
        "channel": CHANNEL,
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "data": data,
        "error": error
    }

def respond_json(obj, pretty=False):
    if pretty:
        text = json.dumps(obj, indent=2, ensure_ascii=False)
        return Response(text, mimetype="application/json; charset=utf-8")
    return Response(json.dumps(obj, ensure_ascii=False), mimetype="application/json; charset=utf-8")

# ========== ROUTES ==========
@app.route("/")
def home():
    return Response(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>GST API - @notxsatvir</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; background: #0a0a2a; color: white; }}
            pre {{ background: #1a1a3a; padding: 15px; border-radius: 10px; overflow-x: auto; }}
            a {{ color: #ff9800; }}
        </style>
    </head>
    <body>
        <h1>🔐 GST API by @notxsatvir</h1>
        <p>GST Information API - Get GST details using GST number</p>
        
        <h2>📖 Usage:</h2>
        <pre>
GET /api/gst?gst=07AAACA1234A1Z
GET /api/gst/07AAACA1234A1Z
POST /api/gst {{"gst": "07AAACA1234A1Z"}}
        </pre>
        
        <h2>📝 Example:</h2>
        <a href="/api/gst?gst=07AAACA1234A1Z&pretty=1">/api/gst?gst=07AAACA1234A1Z&pretty=1</a>
        
        <h2>👤 Owner:</h2>
        <p>{OWNER_NAME} | <a href="{CHANNEL}">{CHANNEL}</a></p>
        
        <h2>📋 Response Format:</h2>
        <pre>{{
  "success": true,
  "owner": "@notxsatvir",
  "channel": "https://t.me/notxsatvir",
  "timestamp": "2024-01-01T12:00:00",
  "query": "07AAACA1234A1Z",
  "data": {{ ... }}
}}</pre>
    </body>
    </html>
    """, mimetype="text/html")

@app.route("/api/gst", methods=["GET"])
def gst_lookup_get():
    gst = request.args.get("gst") or request.args.get("gstin") or request.args.get("query")
    pretty = request.args.get("pretty") in ("1", "true", "True")
    
    if not gst:
        return respond_json(make_response(False, error="Missing GST number! Use ?gst=07AAACA1234A1Z"), pretty=pretty), 400
    
    gst = gst.strip().upper()
    
    if not is_valid_gst(gst):
        return respond_json(make_response(False, error=f"Invalid GST number format! Expected 15 characters. Got: {gst}", query=gst), pretty=pretty), 400
    
    result = fetch_gst_info(gst)
    
    if result.get("success"):
        return respond_json(make_response(True, data=result.get("data"), query=gst), pretty=pretty)
    else:
        return respond_json(make_response(False, error=result.get("error", "Failed to fetch GST info"), query=gst), pretty=pretty), 404

@app.route("/api/gst/<path:gst>", methods=["GET"])
def gst_lookup_path(gst):
    pretty = request.args.get("pretty") in ("1", "true", "True")
    gst = gst.strip().upper()
    
    if not is_valid_gst(gst):
        return respond_json(make_response(False, error=f"Invalid GST number format! Expected 15 characters. Got: {gst}", query=gst), pretty=pretty), 400
    
    result = fetch_gst_info(gst)
    
    if result.get("success"):
        return respond_json(make_response(True, data=result.get("data"), query=gst), pretty=pretty)
    else:
        return respond_json(make_response(False, error=result.get("error", "Failed to fetch GST info"), query=gst), pretty=pretty), 404

@app.route("/api/gst", methods=["POST"])
def gst_lookup_post():
    pretty = request.args.get("pretty") in ("1", "true", "True")
    data = request.get_json(force=True, silent=True) or {}
    gst = data.get("gst") or data.get("gstin") or data.get("query")
    
    if not gst:
        return respond_json(make_response(False, error="Missing GST number! Send JSON {\"gst\": \"07AAACA1234A1Z\"}"), pretty=pretty), 400
    
    gst = gst.strip().upper()
    
    if not is_valid_gst(gst):
        return respond_json(make_response(False, error=f"Invalid GST number format! Expected 15 characters. Got: {gst}", query=gst), pretty=pretty), 400
    
    result = fetch_gst_info(gst)
    
    if result.get("success"):
        return respond_json(make_response(True, data=result.get("data"), query=gst), pretty=pretty)
    else:
        return respond_json(make_response(False, error=result.get("error", "Failed to fetch GST info"), query=gst), pretty=pretty), 404

@app.route("/health", methods=["GET"])
def health():
    return respond_json({
        "status": "ok",
        "owner": OWNER_NAME,
        "channel": CHANNEL,
        "timestamp": datetime.now().isoformat()
    })

# ========== RUN ==========
if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    print(f"🔐 GST API Started | Owner: {OWNER_NAME}")
    print(f"📖 Usage: http://localhost:{port}/api/gst?gst=07AAACA1234A1Z")
    app.run(host="0.0.0.0", port=port, debug=True)