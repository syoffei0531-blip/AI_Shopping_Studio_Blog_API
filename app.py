from flask import Flask, jsonify
import os
import requests

app = Flask(__name__)

# ==========================
# Environment Variables
# ==========================

RAKUTEN_APP_ID = os.getenv("RAKUTEN_APP_ID")
RAKUTEN_AFFILIATE_ID = os.getenv("RAKUTEN_AFFILIATE_ID")

# ==========================
# Home
# ==========================

@app.route("/")
def home():
    return jsonify({
        "service": "AI Shopping Studio Blog API",
        "status": "running",
        "version": "1.0"
    })

# ==========================
# Health Check
# ==========================

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy"
    })

# ==========================
# Rakuten Ranking API
# ==========================

@app.route("/ranking")
def ranking():

    if not RAKUTEN_APP_ID:
        return jsonify({
            "error": "RAKUTEN_APP_ID not configured"
        }), 500

    url = "https://app.rakuten.co.jp/services/api/IchibaItem/Ranking/20220601"

    params = {
        "applicationId": RAKUTEN_APP_ID,
        "affiliateId": RAKUTEN_AFFILIATE_ID,
        "format": "json"
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

        return jsonify(data)

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


# ==========================
# Start
# ==========================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8080
    )
