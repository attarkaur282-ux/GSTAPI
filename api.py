import os
import re
import json
import requests
from flask import Flask, request, Response, jsonify
from datetime import datetime

app = Flask(__name__)

# ========== CONFIG ==========
OWNER_NAME = "@notxsatvir"
CHANNEL = "https://t.me/notxsatvir"

# ========== HELPERS ==========
def is_valid_gst(gst_number: str) -> bool:
    """Basic GST validation (15 characters)"""
    gst = gst_number.strip().upper()
    pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[0-9]{1}[A-Z]{1}[0-9A-Z]{1}$'
    return bool(re.match(pattern, gst))

def fetch_gst_info(gst_number: str):
    """Fetch GST information from public API"""
    
    # Try public GST API
    try:
        url = f"https://publigst.in/api/v1/gstin/{gst_number}"
        headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            return {"success": True, "source": "publigst.in", "data": response.json()}
    except:
        pass
    
    # Return demo data for educational purpose
    return {
        "success": False,
        "error": "GST API temporarily unavailable",
        "demo_data": {
            "gstin": gst_number,
            "trade_name": "Demo Business Name",
            "legal_name": "Demo Legal Name Pvt Ltd",
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

# ========== ROUTES ==========
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "GST API is running",
        "owner": OWNER_NAME,
        "channel": CHANNEL,
        "endpoints": {
            "/api/gst?gst=GST_NUMBER": "GET - Get GST info",
            "/api/gst/GST_NUMBER": "GET - Get GST info by path",
            "/health": "GET - Health check"
        },
        "example": "/api/gst?gst=07AAACA1234A1Z"
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "ok",
        "owner": OWNER_NAME,
        "channel": CHANNEL,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/gst', methods=['GET'])
def gst_lookup():
    gst = request.args.get('gst') or request.args.get('gstin') or request.args.get('query')
    
    if not gst:
        return jsonify(make_response(False, error="Missing GST number! Use ?gst=07AAACA1234A1Z")), 400
    
    gst = gst.strip().upper()
    
    if not is_valid_gst(gst):
        return jsonify(make_response(False, error=f"Invalid GST number! Expected 15 characters. Got: {gst}", query=gst)), 400
    
    result = fetch_gst_info(gst)
    
    if result.get("success"):
        return jsonify(make_response(True, data=result.get("data"), query=gst))
    else:
        return jsonify(make_response(False, data=result.get("demo_data"), error=result.get("error", "Using demo data"), query=gst))

@app.route('/api/gst/<gst>', methods=['GET'])
def gst_lookup_path(gst):
    gst = gst.strip().upper()
    
    if not is_valid_gst(gst):
        return jsonify(make_response(False, error=f"Invalid GST number! Expected 15 characters. Got: {gst}", query=gst)), 400
    
    result = fetch_gst_info(gst)
    
    if result.get("success"):
        return jsonify(make_response(True, data=result.get("data"), query=gst))
    else:
        return jsonify(make_response(False, data=result.get("demo_data"), error=result.get("error", "Using demo data"), query=gst))

@app.route('/api/gst', methods=['POST'])
def gst_lookup_post():
    data = request.get_json(force=True, silent=True) or {}
    gst = data.get('gst') or data.get('gstin') or data.get('query')
    
    if not gst:
        return jsonify(make_response(False, error="Missing GST number! Send JSON {\"gst\": \"07AAACA1234A1Z\"}")), 400
    
    gst = gst.strip().upper()
    
    if not is_valid_gst(gst):
        return jsonify(make_response(False, error=f"Invalid GST number! Expected 15 characters. Got: {gst}", query=gst)), 400
    
    result = fetch_gst_info(gst)
    
    if result.get("success"):
        return jsonify(make_response(True, data=result.get("data"), query=gst))
    else:
        return jsonify(make_response(False, data=result.get("demo_data"), error=result.get("error", "Using demo data"), query=gst))

# ========== RUN ==========
if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    print(f"🔐 GST API Started | Owner: {OWNER_NAME}")
    print(f"📖 http://localhost:{port}/api/gst?gst=07AAACA1234A1Z")
    app.run(host="0.0.0.0", port=port, debug=True)

# Vercel needs this
app = app
