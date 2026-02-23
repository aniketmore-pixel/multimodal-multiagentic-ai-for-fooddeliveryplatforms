import torch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification

# =========================
# APP INIT
# =========================
app = FastAPI(title="Food Quality Regression API")

device = "cuda" if torch.cuda.is_available() else "cpu"

# =========================
# LOAD MODEL
# =========================
MODEL_PATH = "./food_quality_model"

tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_PATH)
model = DistilBertForSequenceClassification.from_pretrained(MODEL_PATH)
model.to(device)
model.eval()

# =========================
# OBSERVED RAW RANGE
# (from your tests)
# =========================
RAW_MIN = 0.4629
RAW_MAX = 0.6905

# =========================
# REQUEST SCHEMA
# =========================
class ReviewInput(BaseModel):
    review: str

# =========================
# SCALING FUNCTION
# =========================
def scale_to_0_1(value: float) -> float:
    scaled = (value - RAW_MIN) / (RAW_MAX - RAW_MIN)
    return max(0.0, min(1.0, scaled))  # clamp safely

# =========================
# PREDICTION FUNCTION
# =========================
def predict_food_quality(review: str):
    try:
        inputs = tokenizer(
            review,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=128
        ).to(device)

        with torch.no_grad():
            logits = model(**inputs).logits  # shape: [1, 1]

        # Raw sigmoid score
        raw_score = torch.sigmoid(logits).item()

        # Rescaled score [0, 1]
        final_score = scale_to_0_1(raw_score)

        return {
            "score": round(final_score, 4)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =========================
# API ROUTE
# =========================
@app.post("/predict")
def predict_quality(data: ReviewInput):
    return predict_food_quality(data.review)

# =========================
# HEALTH CHECK
# =========================
@app.get("/")
def root():
    return {"message": "Food Quality Regression API is running"}
