# producer.py
import redis

# Connect to Redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def add_review(review_text: str):
    """
    Add a review to the Redis stream.
    """
    r.xadd("reviews_stream", {"review": review_text})
    print(f"Review added: {review_text}")

# Example usage
if __name__ == "__main__":
    while True:
        review = input("Enter a food review (or 'exit' to quit): ")
        if review.lower() == "exit":
            break
        add_review(review)
