# dashboard.py
import streamlit as st
import redis
import numpy as np
from streamlit_autorefresh import st_autorefresh

# =========================
# Redis setup
# =========================
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# =========================
# Labeling function (8 levels)
# =========================
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

# =========================
# Streamlit UI
# =========================
st.set_page_config(page_title="Food Quality Dashboard", layout="wide")
st.title("🍽 Food Quality Real-Time Dashboard")
st.markdown("Latest 10 reviews & Holistic food quality index for the last 100 reviews.")

# =========================
# Auto-refresh every 3 seconds
# =========================
st_autorefresh(interval=3000, key="fqi_refresh")

# =========================
# Fetch latest 10 reviews
# =========================
def get_latest_10_reviews():
    scores = r.lrange("review_scores", -10, -1)  # last 10 scores
    reviews_entries = r.xrevrange("reviews_stream", max="+", min="-", count=10)
    reviews_entries.reverse()  # oldest first

    reviews_with_scores = []
    for (entry_id, data), score in zip(reviews_entries, scores):
        reviews_with_scores.append((data["review"], float(score)))
    return reviews_with_scores

# =========================
# Holistic score for last 100
# =========================
def get_holistic_score():
    scores = r.lrange("review_scores", -100, -1)
    scores = [float(s) for s in scores]
    if scores:
        score = np.mean(scores)
        label = get_quality_label(score)
        return round(score, 3), label, len(scores)
    return None, None, 0

# =========================
# Display
# =========================
# Latest 10 reviews
latest_reviews = get_latest_10_reviews()
if latest_reviews:
    st.subheader("Latest 10 Reviews")
    st.table([
        {"Review": review, "Score": round(score, 3), "Label": get_quality_label(score)}
        for review, score in latest_reviews
    ])
else:
    st.markdown("No reviews yet.")

# Holistic index
holistic_score, holistic_label, n_reviews = get_holistic_score()
if holistic_score is not None:
    st.subheader(f"Holistic Food Quality Index (last {n_reviews} reviews)")
    st.markdown(
        f"**Score (0-1):** {holistic_score}  \n"
        f"**Overall Quality:** {holistic_label}"
    )
else:
    st.markdown("No holistic score yet.")
