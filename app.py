from flask import Flask, jsonify, request, send_file
import os
import requests
import tempfile
import base64

from playwright.sync_api import sync_playwright

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

        response.raise_for_status()

        data = response.json()

        items = []

        for item in data.get("Items", []):
            product = item.get("Item", {})

            items.append({
                "title": product.get("itemName"),
                "price": product.get("itemPrice"),
                "url": product.get("itemUrl"),
                "image": product.get("mediumImageUrls", [{}])[0].get("imageUrl", ""),
                "shop": product.get("shopName"),
                "reviewAverage": product.get("reviewAverage"),
                "reviewCount": product.get("reviewCount"),

                "description": product.get("itemCaption"),
                "availability": product.get("availability"),
                "pointRate": product.get("pointRate"),
                "genreId": product.get("genreId"),
                "shopUrl": product.get("shopUrl"),
                "affiliateUrl": product.get("affiliateUrl"),
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

        response.raise_for_status()

        data = response.json()

        items = []

        for item in data.get("Items", []):
            product = item.get("Item", {})

            items.append({
                "title": product.get("itemName"),
                "price": product.get("itemPrice"),
                "url": product.get("itemUrl"),
                "image": product.get("mediumImageUrls", [{}])[0].get("imageUrl", ""),
                "shop": product.get("shopName"),
                "shopUrl": product.get("shopUrl"),

                "reviewAverage": product.get("reviewAverage"),
                "reviewCount": product.get("reviewCount"),

                "description": product.get("itemCaption"),
                "availability": product.get("availability"),
                "pointRate": product.get("pointRate"),
                "genreId": product.get("genreId"),

                "affiliateUrl": product.get("affiliateUrl")
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
# NOTE Draft API
# ==========================

@app.route("/render", methods=["POST"])
def render_blog():

    data = request.json

    if not data:
        return jsonify({
            "success": False,
            "message": "No JSON received"
        }), 400
    
    title = data.get("title", "")
    html = data.get("html", "")

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".html",
        mode="w",
        encoding="utf-8"
    ) as f:

        f.write(html)
        html_file = f.name

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)

        page = browser.new_page(
            viewport={
                "width":720,
                "height":1280
            }
        )

        page.goto("file://" + html_file)

        page.screenshot(
            path="blog.jpg",
            type="jpeg",
            quality=85,
            full_page=True
        )

        browser.close()

    with open("blog.jpg","rb") as f:
        image_base64 = base64.b64encode(f.read()).decode("utf-8")

    html = html.replace(
        "__QUESTION_IMAGE__",
        f"data:image/jpeg;base64,{image_base64}"
    )
    
    return jsonify({
        "success": True,
        "title": title,
        "description": data.get("description", ""),
        "tags": data.get("tags", []),
        "html": html,
        "image": image_base64
    })

# ==========================
# Publish API
# ==========================

@app.route("/publish", methods=["POST"])
def publish():

    data = request.json

    if not data:
        return jsonify({
            "success": False,
            "message": "No JSON received"
        }), 400

    platform = data.get("platform", "")
    title = data.get("title", "")
    description = data.get("description", "")
    tags = data.get("tags", [])
    html = data.get("html", "")
    image = data.get("image", "")

    return jsonify({
        "success": True,
        "platform": platform,
        "title": title,
        "description": description,
        "tags": tags,
        "html": html,
        "image": image
    })

# ==========================
# Start
# ==========================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8080
    )
