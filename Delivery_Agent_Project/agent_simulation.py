import requests
import time
import random
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# --- Configuration ---
BACKEND_URL = "http://127.0.0.1:8239/get_order_analysis/"
IMAGE_BASE_DIR = "images"
BASE_DIR = os.getcwd()
LOG_FILE = os.path.join(BASE_DIR, "live_agent_log.csv")

# --- Helper to scan images ---
def get_available_images():
    ok_path = os.path.join(IMAGE_BASE_DIR, "ok")
    damaged_path = os.path.join(IMAGE_BASE_DIR, "damaged")
    
    if not os.path.exists(ok_path) or not os.path.exists(damaged_path):
        return [], []

    ok_images = [os.path.join("ok", f) for f in os.listdir(ok_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    damaged_images = [os.path.join("damaged", f) for f in os.listdir(damaged_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    return ok_images, damaged_images

# --- NEW: Helper to get the next Order ID ---
def get_next_order_id():
    """Checks the log file to find the highest previous ID and increments it."""
    start_id = 5000
    if os.path.exists(LOG_FILE):
        try:
            df = pd.read_csv(LOG_FILE)
            if not df.empty and 'order_id' in df.columns:
                last_id = df['order_id'].max()
                # Ensure it's a valid integer
                if pd.notna(last_id):
                    return int(last_id) + 1
        except Exception as e:
            print(f"⚠️ Could not read history: {e}. Starting fresh from {start_id}.")
    
    return start_id

# --- The Agent Logic ---
def run_autonomous_agent(interval_seconds=5):
    print("🚀 INITIALIZING AUTONOMOUS AGENT...")
    print(f"📡 Connecting to Brain at: {BACKEND_URL}")
    
    # 1. Determine Starting ID
    order_counter = get_next_order_id()
    print(f"🔢 Continuing sequence from Order ID: #{order_counter}")
    print("----------------------------------------------------------------")
    
    ok_images, damaged_images = get_available_images()
    
    if not ok_images or not damaged_images:
        print("❌ ERROR: Could not find images in 'images/ok' or 'images/damaged'.")
        return

    while True:
        try:
            # 2. GENERATE LIVE EVENT
            print(f"\n🔔 EVENT DETECTED: New Order #{order_counter}")
            
            # Generate random realistic features
            distance_km = round(random.uniform(1.0, 18.0), 2)
            estimated_time = datetime.now()
            
            # Simulate delays
            base_lateness = random.randint(-15, 35) 
            actual_time = estimated_time + timedelta(minutes=base_lateness)
            
            weather = random.choices(['Clear', 'Rain', 'Fog'], weights=[0.70, 0.25, 0.05])[0]
            restaurant_load = random.choices(['Low', 'Medium', 'High'], weights=[0.4, 0.4, 0.2])[0]
            
            # Pick an image
            if base_lateness > 20 and random.random() < 0.7:
                image_filename = random.choice(damaged_images)
            else:
                image_filename = random.choice(ok_images)

            # Create payload (Using pandas Series for easy JSON conversion like before)
            order_data = pd.Series({
                "order_id": order_counter,
                "estimated_delivery_time": estimated_time.isoformat(),
                "actual_delivery_time": actual_time.isoformat(),
                "distance_km": distance_km,
                "weather": weather,
                "restaurant_load": restaurant_load
            })
            
            # 3. SEND TO BRAIN
            payload = {
                'image_filename': image_filename,
                'order_data_json': order_data.to_json(date_format='iso')
            }
            
            response = requests.post(BACKEND_URL, data=payload)
            
            if response.status_code == 200:
                report = response.json()
                final_score = report['final_score']
                
                # 4. ACTION
                print(f"   🧠 ANALYZING... (Score: {final_score}/5.0)")
                
                if final_score >= 4.0:
                    action = "✅ ACTION: Standard protocol."
                elif final_score >= 2.5:
                    action = "⚠️ ACTION: Flagged for review."
                else:
                    action = "🚨 ACTION: CRITICAL ESCALATION."
                
                print(f"   👉 {action}")
                
            else:
                print(f"   ❌ BRAIN ERROR: {response.status_code} - {response.text}")

        except requests.exceptions.ConnectionError:
            print("   ❌ CONNECTION ERROR: Is 'backend.py' running?")
        except Exception as e:
            print(f"   ❌ UNEXPECTED ERROR: {e}")

        print("----------------------------------------------------------------")
        order_counter += 1
        time.sleep(interval_seconds)

if __name__ == "__main__":
    run_autonomous_agent()