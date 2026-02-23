from flask import Flask, render_template, request, flash, redirect, url_for
import redis
import time
import threading
import random

app = Flask(__name__)
app.secret_key = "super_secret_key"

# Connect to Redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# --- 1. CONFIGURING THE DATA FOR REALISTIC REVIEWS ---
food_items = [
    "Grilled Salmon", "Cheese Pizza", "Avocado Toast", "Truffle Pasta",
    "Caesar Salad", "Double Cheeseburger", "Sushi Platter", "Chocolate Lava Cake",
    "Spicy Ramen", "Iced Latte"
]

positive_phrases = [
    "absolutely delicious", "cooked to perfection", "bursting with flavor",
    "highly recommended", "worth every penny", "fresh and tasty"
]

negative_phrases = [
    "too salty", "served cold", "undercooked",
    "a bit bland", "overpriced for the portion", "disappointing"
]

# --- 2. THE BACKGROUND GENERATOR FUNCTION ---
def generate_auto_reviews():
    """
    Runs in a background thread. Generates a random review every 5 seconds
    and pushes it to Redis.
    """
    print(">>> Auto-Review Generator Started...")
    
    while True:
        try:
            # Randomly decide if the review is good (70% chance) or bad (30% chance)
            is_positive = random.random() > 0.3
            
            item = random.choice(food_items)
            
            if is_positive:
                opinion = random.choice(positive_phrases)
                rating = random.randint(4, 5)
                review_text = f"The {item} was {opinion}! I'd give it {rating} stars."
            else:
                opinion = random.choice(negative_phrases)
                rating = random.randint(1, 3)
                review_text = f"I didn't like the {item}, it was {opinion}. {rating} stars."

            # Add to Redis Stream
            entry_id = r.xadd("reviews_stream", {
                "review": review_text,
                "timestamp": time.time(),
                "type": "auto-generated"
            })

            print(f"[Auto-Gen] Sent: {review_text} (ID: {entry_id})")
            
            # Wait for 5 seconds
            time.sleep(5)
            
        except Exception as e:
            print(f"Error generating review: {e}")
            time.sleep(5) # Wait before retrying

@app.route("/", methods=["GET", "POST"])
def index():
    # You can still use the manual form if you want to!
    if request.method == "POST":
        review_text = request.form.get("review")
        if review_text:
            r.xadd("reviews_stream", {
                "review": review_text,
                "timestamp": time.time(),
                "type": "manual"
            })
            flash("Review submitted manually!", "success")
            return redirect(url_for("index"))
        else:
            flash("Please enter some text.", "danger")

    return render_template("form.html")

if __name__ == "__main__":
    # --- 3. START THE THREAD BEFORE THE APP ---
    # daemon=True means this thread will automatically die when the main program stops
    generator_thread = threading.Thread(target=generate_auto_reviews, daemon=True)
    generator_thread.start()

    # Run Flask (use_reloader=False prevents the script from running twice and doubling the reviews)
    print(">>> Starting Web Server on Port 5001...")
    app.run(debug=True, port=5001, use_reloader=False)