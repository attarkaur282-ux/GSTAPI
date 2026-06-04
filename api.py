from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "status": "ok",
        "message": "GST API by @notxsatvir",
        "endpoints": {
            "/health": "Health check",
            "/api/gst?gst=07AAACA1234A1Z": "Get GST info"
        }
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "owner": "@notxsatvir",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/gst')
def gst_info():
    gst = request.args.get('gst', '')
    
    if not gst:
        return jsonify({"error": "GST number required", "example": "/api/gst?gst=07AAACA1234A1Z"}), 400
    
    # Demo response
    return jsonify({
        "success": True,
        "owner": "@notxsatvir",
        "gst_number": gst,
        "data": {
            "business_name": "Demo Business",
            "status": "Active"
        }
    })

if __name__ == '__main__':
    app.run()
