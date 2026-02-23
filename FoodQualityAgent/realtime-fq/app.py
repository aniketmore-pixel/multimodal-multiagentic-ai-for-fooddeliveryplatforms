# from flask import Flask, render_template
# import redis
# import json

# app = Flask(__name__)

# # Connect to the same Redis instance as consumer.py
# r = redis.Redis(host="localhost", port=6379, decode_responses=True)

# @app.route("/")
# def dashboard():
#     # 1. Fetch Holistic Data
#     # Redis returns strings (or None if keys don't exist yet)
#     holistic_score = r.get("holistic_score")
#     holistic_label = r.get("holistic_label")

#     # Format score for display (handle None case)
#     if holistic_score:
#         holistic_score = round(float(holistic_score), 3)
#     else:
#         holistic_score = 0.0
#         holistic_label = "Waiting for data..."

#     # 2. Fetch Latest Reviews
#     # lrange(0, -1) gets all items. Your consumer stores them via rpush (newest at the end).
#     raw_reviews = r.lrange("latest_reviews", 0, -1)
    
#     parsed_reviews = []
#     for item in raw_reviews:
#         try:
#             parsed_reviews.append(json.loads(item))
#         except json.JSONDecodeError:
#             continue
    
#     # Reverse the list so the newest reviews appear at the top of the table
#     parsed_reviews.reverse()

#     return render_template(
#         "dashboard.html",
#         score=holistic_score,
#         label=holistic_label,
#         reviews=parsed_reviews
#     )

# if __name__ == "__main__":
#     app.run(debug=True, port=5000)

from flask import Flask, render_template, jsonify
import redis
import json

app = Flask(__name__)

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

def fetch_dashboard_data():
    # ---- Holistic Data ----
    holistic_score = r.get("holistic_score")
    holistic_label = r.get("holistic_label")

    if holistic_score:
        holistic_score = round(float(holistic_score), 3)
    else:
        holistic_score = 0.0
        holistic_label = "Waiting for data..."

    # ---- Latest Reviews ----
    raw_reviews = r.lrange("latest_reviews", 0, -1)

    parsed_reviews = []
    for item in raw_reviews:
        try:
            parsed_reviews.append(json.loads(item))
        except json.JSONDecodeError:
            continue

    parsed_reviews.reverse()

    return {
        "holisticScore": holistic_score,
        "holisticLabel": holistic_label,
        "totalReviews": len(parsed_reviews),
        "reviews": parsed_reviews
    }


# ----------------------------
# FRONTEND ROUTE (HTML)
# ----------------------------
@app.route("/")
def dashboard():
    data = fetch_dashboard_data()

    return render_template(
        "dashboard.html",
        score=data["holisticScore"],
        label=data["holisticLabel"],
        reviews=data["reviews"]
    )


# ----------------------------
# NEW API ROUTE
# ----------------------------
@app.route("/api/dashboard")
def dashboard_api():
    data = fetch_dashboard_data()
    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True, port=4782)
