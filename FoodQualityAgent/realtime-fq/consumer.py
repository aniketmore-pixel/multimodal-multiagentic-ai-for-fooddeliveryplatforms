# consumer.py
import redis
import requests
import numpy as np
import time
import json

REDIS_HOST = "localhost"
REDIS_PORT = 6379
API_URL = "http://127.0.0.1:9850/predict"

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
last_id = "0-0"

def get_quality_label(score):
    if score < 0.125:
        return "Extremely Bad"
    elif score < 0.25:
        return "Very Bad"
    elif score < 0.375:
        return "Bad"
    elif score < 0.5:
        return "Slightly Bad"
    elif score < 0.625:
        return "Slightly Good"
    elif score < 0.75:
        return "Good"
    elif score < 0.875:
        return "Very Good"
    else:
        return "Excellent"

def process_new_reviews():
    global last_id

    entries = r.xread({"reviews_stream": last_id}, block=5000, count=10)
    if not entries:
        return None

    stream_name, new_entries = entries[0]
    latest_reviews_with_scores = []

    for entry_id, data in new_entries:
        last_id = entry_id
        review_text = data["review"]

        # Call ML API
        try:
            response = requests.post(API_URL, json={"review": review_text})
            if response.status_code == 200:
                score = response.json()["score"]
            else:
                print(f"API error for review: {review_text}")
                continue
        except Exception as e:
            print(f"Error calling API: {e}")
            continue

        # Store as JSON in Redis list for latest 100 reviews
        review_entry = json.dumps({"review": review_text, "score": score})
        r.rpush("latest_reviews", review_entry)
        r.ltrim("latest_reviews", -100, -1)  # keep latest 100 reviews

        latest_reviews_with_scores.append((review_text, score))

    # Compute holistic score & label
    all_entries = r.lrange("latest_reviews", 0, -1)
    all_scores = [json.loads(e)["score"] for e in all_entries]
    holistic_score = np.mean(all_scores) if all_scores else None
    holistic_label = get_quality_label(holistic_score) if all_scores else None

    # Store for dashboard
    if holistic_score is not None:
        # CONVERT TO PYTHON FLOAT HERE
        r.set("holistic_score", float(holistic_score)) 
        r.set("holistic_label", holistic_label)

    return {
        "latest_reviews": latest_reviews_with_scores,
        "holistic_score": holistic_score,
        "holistic_label": holistic_label
    }

if __name__ == "__main__":
    print("Consumer started. Waiting for new reviews...")
    while True:
        result = process_new_reviews()
        if result and result["latest_reviews"]:
            print("Processed new reviews:")
            for review, score in result["latest_reviews"]:
                print(f"- {review[:50]}... | Score: {round(score,3)}")
            print(f"Holistic Score: {round(result['holistic_score'],3)} | Label: {result['holistic_label']}")
        time.sleep(1)
