from flask import Flask, jsonify, request
import os
import requests

app = Flask(__name__)

# ==========================
# Environment Variables
# ==========================

RAKUTEN_APP_ID = os.getenv("RAKUTEN_APP_ID")
RAKUTEN_ACCESS_KEY = os.getenv("RAKUTEN_ACCESS_KEY")
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

    url = "https://openapi.rakuten.co.jp/ichibaranking/api/IchibaItem/Ranking/20220601"
    params = {
        "applicationId": RAKUTEN_APP_ID,
        "accessKey": RAKUTEN_ACCESS_KEY,
        "affiliateId": RAKUTEN_AFFILIATE_ID,
        "format": "json"
    }

    try:

        headers = {
            "Origin": "https://aishoppingstudioblogapi-production.up.railway.app",
            "Referer": "https://aishoppingstudioblogapi-production.up.railway.app",
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=20
        )

        print("URL =", response.request.url)
        print("STATUS =", response.status_code)
        print("BODY =", response.text)

        data = response.json()

        items = []

        for item in data["Items"]:
            product = item["Item"]

            items.append({
                "title": product["itemName"],
                "price": product["itemPrice"],
                "url": product["itemUrl"],
                "image": product["mediumImageUrls"][0]["imageUrl"],
                "shop": product["shopName"],
                "reviewAverage": product["reviewAverage"],
                "reviewCount": product["reviewCount"]
            })

        return jsonify({
            "success": True,
            "count": len(items),
            "items": items
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

# ==========================
# Rakuten Search API
# ==========================

@app.route("/search")
def search():

    print("APP_ID =", RAKUTEN_APP_ID)
    print("ACCESS_KEY =", RAKUTEN_ACCESS_KEY)
    print("AFFILIATE_ID =", RAKUTEN_AFFILIATE_ID)
    
    keyword = request.args.get("keyword")

    if not keyword:
        return jsonify({
            "success": False,
            "message": "keyword is required"
        }), 400

    url = "https://openapi.rakuten.co.jp/ichibams/api/IchibaItem/Search/20260701"

    params = {
        "applicationId": RAKUTEN_APP_ID,
        "accessKey": RAKUTEN_ACCESS_KEY,
        "affiliateId": RAKUTEN_AFFILIATE_ID,
        "keyword": keyword,
        "genreId": 0,
        "hits": 10,
        "format": "json"
    }

    try:

        headers = {
            "Origin": "https://aishoppingstudioblogapi-production.up.railway.app",
            "Referer": "https://aishoppingstudioblogapi-production.up.railway.app",
            "User-Agent": "Mozilla/5.0"
        }
     
        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=20
        )

        print("URL =", response.request.url)
        print("STATUS =", response.status_code)
        print("BODY =", response.text)

        return jsonify({
            "url": response.request.url,
            "status": response.status_code,
            "body": response.text
        })

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
