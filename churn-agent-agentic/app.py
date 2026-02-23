from flask import Flask, jsonify, render_template
import requests
import threading
import time
import os
import random
import pandas as pd
import joblib
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

churn_history = []
MAX_HISTORY = 100 

# Load the trained Machine Learning Model
try:
    ml_model = joblib.load('churn_prediction_model.pkl')
    print("Successfully loaded Churn Prediction ML Model.")
except Exception as e:
    print(f"Error loading model: {e}. Please ensure the .pkl file is present.")
    ml_model = None

UX_API = "http://localhost:9000/ux-agent-latest"
DELIVERY_API = "http://localhost:9578"
FOOD_API = "http://localhost:4782/api/dashboard"

def calculate_churn_metrics():
    """Background thread function with ML-powered evaluation."""
    while True:
        try:
            # 1. Fetch Real Data from APIs
            try:
                ux_resp = requests.get(UX_API, timeout=2).json()
                del_resp = requests.get(DELIVERY_API, timeout=2).json()
                food_resp = requests.get(FOOD_API, timeout=2).json()
                
                # Parse JSON according to your specific API schemas
                ux_avg = ux_resp.get("overview", {}).get("rolling_average", 10.0)
                del_avg = del_resp.get("kpis", {}).get("overall_avg_score", 5.0)
                food_score = food_resp.get("holisticScore", 1.0)
            except Exception as e:
                print(f"API Fetch Error (Using Fallbacks): {e}")
                # Fallbacks just in case the APIs are down
                ux_avg = random.uniform(5.0, 9.5)
                del_avg = random.uniform(2.0, 4.8)
                food_score = random.uniform(0.5, 0.95)

            # Convert API scores into friction/risk percentages
            ux_friction_pct = max(0, (10.0 - ux_avg) / 10.0 * 100)
            delivery_delay_pct = max(0, (5.0 - del_avg) / 5.0 * 100)
            food_quality_pct = food_score * 100 

            # 2. Generate Mock Data for remaining ML features
            active_inactive_ratio = random.uniform(0.1, 5.0)
            avg_orders_per_user = random.uniform(1.0, 20.0)
            cancellation_rate = random.uniform(0.0, 0.3)
            avg_order_value = random.uniform(15.0, 100.0)
            discount_usage_pct = random.uniform(0.0, 100.0)
            complaints_resolved_ratio = random.uniform(0.0, 1.0)

            # 3. Predict Churn using the ML Model
            predicted_churn = 0.0
            if ml_model:
                input_data = pd.DataFrame([{
                    'active_inactive_ratio': active_inactive_ratio,
                    'avg_orders_per_user': avg_orders_per_user,
                    'cancellation_rate': cancellation_rate,
                    'avg_order_value': avg_order_value,
                    'discount_usage_pct': discount_usage_pct,
                    'ux_friction_pct': ux_friction_pct,
                    'delivery_delay_pct': delivery_delay_pct,
                    'food_quality_pct': food_quality_pct,
                    'complaints_resolved_ratio': complaints_resolved_ratio
                }])
                
                raw_prediction = float(ml_model.predict(input_data)[0])
                predicted_churn = max(0.0, min(100.0, raw_prediction))

            # 4. Save the Record with ALL parameters
            record = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "overall_churn_risk_percent": round(predicted_churn, 2),
                "factors": {
                    "ux_friction_pct": round(ux_friction_pct, 2),
                    "delivery_delay_pct": round(delivery_delay_pct, 2),
                    "food_quality_pct": round(food_quality_pct, 2),
                    "active_inactive_ratio": round(active_inactive_ratio, 2),
                    "avg_orders_per_user": round(avg_orders_per_user, 2),
                    "cancellation_rate": round(cancellation_rate, 3), # 3 decimals for lower numbers
                    "avg_order_value": round(avg_order_value, 2),
                    "discount_usage_pct": round(discount_usage_pct, 2),
                    "complaints_resolved_ratio": round(complaints_resolved_ratio, 3)
                }
            }

            churn_history.insert(0, record)
            if len(churn_history) > MAX_HISTORY:
                churn_history.pop()

        except Exception as e:
            print(f"[{datetime.now()}] Background Task Error: {e}")
        
        # New churn generated every 5 seconds
        time.sleep(5) 

polling_thread = threading.Thread(target=calculate_churn_metrics, daemon=True)
polling_thread.start()

# --- ROUTES ---

@app.route('/api/churn/latest', methods=['GET'])
def get_latest_churn():
    if not churn_history:
        return jsonify({"status": "pending", "message": "Waiting for data"}), 202
    
    recent_20 = churn_history[:20]
    avg_last_20 = sum(r['overall_churn_risk_percent'] for r in recent_20) / len(recent_20)

    return jsonify({
        "status": "success", 
        "data": churn_history[0],
        "rolling_average_20": round(avg_last_20, 2)
    })

@app.route('/api/churn/history', methods=['GET'])
def get_churn_history():
    return jsonify({"status": "success", "data": churn_history})

@app.route('/', methods=['GET'])
def dashboard():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=4996, use_reloader=False)