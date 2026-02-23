import os
import csv
from datetime import datetime
from fastapi import FastAPI, HTTPException, Form
from fastapi.staticfiles import StaticFiles
import torch
from torchvision import models, transforms
from PIL import Image
import io
import pandas as pd

app = FastAPI(title="Satisfaction Insight AI Backend", version="2.2.0")

# --- Serve Images ---
os.makedirs("images", exist_ok=True)
app.mount("/images", StaticFiles(directory="images"), name="images")

# --- IMPROVED LOGGING ---
LOG_FILE = "live_agent_log.csv"

# Added 'lateness_min' to headers
CSV_HEADERS = [
    "timestamp", "order_id", "final_score", "status", "action_taken",
    "distance_km", "weather", "restaurant_load", "image_filename", 
    "analysis_text", "recommendation", "lateness_min"
]

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(CSV_HEADERS)

def log_full_details(order_series, final_score, summary, action, image_filename, analysis_text, recommendation, lateness):
    """Logs rich data including lateness."""
    with open(LOG_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            datetime.now().isoformat(),
            int(order_series['order_id']),
            round(final_score, 2),
            summary,
            action,
            order_series.get('distance_km'),
            order_series.get('weather'),
            order_series.get('restaurant_load'),
            image_filename,
            analysis_text,
            recommendation,
            round(lateness, 1) # Log the calculated lateness
        ])

# --- Model Loading ---
MODEL_PATH = 'packaging_classifier_model.pth'
CLASS_NAMES = ['damaged', 'ok']
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def load_packaging_model():
    if not os.path.exists(MODEL_PATH):
        model = models.resnet18(weights=None)
        model.fc = torch.nn.Linear(model.fc.in_features, 2)
        torch.save(model.state_dict(), MODEL_PATH)
    
    model = models.resnet18(weights=None)
    model.fc = torch.nn.Linear(model.fc.in_features, 2)
    model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
    model.to(device)
    model.eval()
    return model

packaging_model = load_packaging_model()
image_transforms = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# --- Core Logic ---
def calculate_lateness(order_data):
    estimated = pd.to_datetime(order_data['estimated_delivery_time'])
    actual = pd.to_datetime(order_data['actual_delivery_time'])
    lateness = (actual - estimated).total_seconds() / 60
    return lateness

def get_timeliness_status(lateness):
    if lateness <= 0: return 5.0, "Excellent"
    elif lateness <= 5: return 4.0, "Good"
    elif lateness <= 15: return 3.0, "Average"
    elif lateness <= 30: return 2.0, "Poor"
    else: return 1.0, "Very Poor"

def predict_packaging(image_path):
    try:
        img = Image.open(image_path).convert("RGB")
        img_t = image_transforms(img).unsqueeze(0).to(device)
        with torch.no_grad():
            out = packaging_model(img_t)
            _, pred = torch.max(out, 1)
            cls = CLASS_NAMES[pred.item()]
        return (5.0, "Excellent") if cls == 'ok' else (1.0, "Damaged")
    except:
        return 1.0, "Error"

def generate_insights(final_score, t_status, p_status, weather, load):
    reasons = []
    if p_status == "Damaged": reasons.append("packaging damage")
    if t_status in ["Poor", "Very Poor"]: reasons.append("significant delay")
    
    context = []
    if weather in ["Rain", "Fog"]: context.append(f"adverse weather ({weather})")
    if load == "High": context.append("high restaurant load")
        
    text = f"Score: {final_score:.1f}/5.0. "
    if reasons: text += f"Impacted by {', '.join(reasons)}. "
    if context: text += f"Context: {', '.join(context)}."
    
    rec = "Standard Protocol"
    if final_score < 4.0:
        if p_status == "Damaged": rec = "Check Handling"
        elif t_status in ["Poor", "Very Poor"]: rec = "Review Route / Adjust ETA"
        
    return text, rec

# --- Endpoint ---
@app.post("/get_order_analysis/")
async def get_order_analysis(image_filename: str = Form(...), order_data_json: str = Form(...)):
    try:
        order_series = pd.read_json(io.StringIO(order_data_json), typ='series')
        
        # 1. Analyze
        lateness = calculate_lateness(order_series)
        t_score, t_status = get_timeliness_status(lateness)
        
        img_path = os.path.join("images", image_filename)
        p_score, p_status = predict_packaging(img_path)
        
        # 2. Fuse
        final_score = (t_score * 0.7) + (p_score * 0.3)
        summary = f"Timeliness: {t_status}, Packaging: {p_status}"
        
        # 3. Action
        if final_score >= 4.0: action = "No Action"
        elif final_score >= 2.5: action = "Flagged for Review"
        else: action = "CRITICAL: Refund Issued"
        
        # 4. Insights
        analysis_text, recommendation = generate_insights(
            final_score, t_status, p_status, 
            order_series.get('weather'), order_series.get('restaurant_load')
        )
        
        # 5. Log
        log_full_details(
            order_series, final_score, summary, action, image_filename, 
            analysis_text, recommendation, lateness
        )
        
        return {
            "order_id": int(order_series['order_id']),
            "final_score": round(final_score, 2),
            "summary": summary,
            "analysis_text": analysis_text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))