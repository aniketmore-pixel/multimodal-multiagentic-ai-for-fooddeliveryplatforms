from fastapi import FastAPI
import pandas as pd
import os

app = FastAPI()

BASE_DIR = os.getcwd()
LOG_FILE = os.path.join(BASE_DIR, "live_agent_log.csv")


def load_data():
    if not os.path.exists(LOG_FILE):
        return pd.DataFrame()

    df = pd.read_csv(LOG_FILE)

    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])

    if 'final_score' in df.columns:
        df['final_score'] = pd.to_numeric(df['final_score'], errors='coerce')

    return df


@app.get("/")
def dashboard_summary():
    df = load_data()

    if df.empty:
        return {"status": "no_data"}

    df = df.sort_values("timestamp", ascending=False)

    latest = df.iloc[0]

    overall_avg = df['final_score'].mean()

    critical_count = 0
    if 'action_taken' in df.columns:
        critical_count = df[
            df['action_taken'].astype(str).str.contains("CRITICAL", na=False)
        ].shape[0]

    # Holistic index (you can define logic however you want)
    holistic_index = round((overall_avg * 20) - (critical_count * 2), 2)

    # Trend data (last 50)
    trend_df = df.sort_values("timestamp").tail(50)
    trend_data = trend_df[['timestamp', 'final_score']].to_dict(orient="records")

    return {
        "kpis": {
            "orders_processed": len(df),
            "overall_avg_score": round(overall_avg, 2),
            "critical_alerts": critical_count,
            "holistic_index": holistic_index
        },
        "latest_order": latest.to_dict(),
        "trend_last_50": trend_data
    }
