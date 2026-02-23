import streamlit as st
import pandas as pd
import time
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="Satisfaction Mission Control", page_icon="🚀", layout="wide")

# --- PATH SETUP ---
BASE_DIR = os.getcwd() 
LOG_FILE = os.path.join(BASE_DIR, "live_agent_log.csv")
BACKEND_BASE_URL = "http://127.0.0.1:8239"

# --- DATA LOADER ---
def load_live_data():
    if not os.path.exists(LOG_FILE):
        return pd.DataFrame()
    try:
        df = pd.read_csv(LOG_FILE)
        
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        if 'final_score' in df.columns:
            df['final_score'] = pd.to_numeric(df['final_score'], errors='coerce')
        if 'image_filename' in df.columns:
            df['image_filename'] = df['image_filename'].astype(str).str.replace("\\", "/", regex=False)
        if 'lateness_min' in df.columns:
            df['lateness_min'] = pd.to_numeric(df['lateness_min'], errors='coerce')

        if not df.empty and 'timestamp' in df.columns:
            df = df.sort_values(by="timestamp", ascending=False)
        return df
    except Exception:
        return pd.DataFrame()

def get_status_color(score):
    if score >= 4.0: return "green"
    elif score >= 2.5: return "orange"
    return "red"

# --- SIDEBAR ---
st.sidebar.title("⚙️ Settings")
auto_refresh = st.sidebar.toggle("Enable Live Auto-Refresh", value=True)
st.sidebar.caption("Pause updates to inspect orders.")

# --- MAIN APP ---
st.title("🚀 Delivery Agent Mission Control")
df = load_live_data()

# TABS
live_tab, deep_dive_tab, analysis_tab, explorer_tab = st.tabs([
    "🔴 Live Monitor", "🕵️ Order Deep Dive", "🔬 Performance Analysis", "🗂️ Data Explorer"
])

# ==========================================
# TAB 1: LIVE MONITOR
# ==========================================
with live_tab:
    st.markdown("### 📡 Autonomous Agent Feed")
    if df.empty:
        st.info(f"Waiting for Agent... (Log: {LOG_FILE})")
    else:
        # KPIs
        curr_avg = df['final_score'].mean()
        delta = 0.0
        if len(df) > 10:
            delta = curr_avg - df['final_score'].iloc[10:].mean()

        k1, k2, k3, k4 = st.columns(4)
        latest = df.iloc[0]
        
        k1.metric("Orders Processed", len(df))
        k2.metric("Latest Order ID", f"#{latest['order_id']}")
        k3.metric("Overall Avg Score", f"{curr_avg:.2f}", delta=f"{delta:.2f}")
        
        crit_count = 0
        if 'action_taken' in df.columns:
            crit_count = df[df['action_taken'].astype(str).str.contains("CRITICAL", na=False)].shape[0]
        k4.metric("Critical Alerts", crit_count, delta_color="inverse")

        # Live Pulse Graph
        st.divider()
        st.markdown("#### ⚡ Live Pulse (Last 50 Orders)")
        chart_data = df.sort_values("timestamp").tail(50).copy()
        chart_data['Trend'] = chart_data['final_score'].rolling(window=5).mean()
        st.line_chart(chart_data.set_index("timestamp")[['final_score', 'Trend']])

        # Details
        st.divider()
        c1, c2 = st.columns([1, 2])
        with c1:
            st.subheader("📦 Latest Arrival")
            if 'image_filename' in latest:
                img_url = f"{BACKEND_BASE_URL}/images/{latest['image_filename']}"
                st.image(img_url, caption=f"Order #{latest['order_id']}", use_container_width=True)
                score = latest['final_score']
                st.markdown(f"**Score:** :{get_status_color(score)}[{score}]")
        with c2:
            st.subheader("📜 Decision Log")
            st.dataframe(df[['timestamp', 'order_id', 'final_score', 'action_taken']].head(8), hide_index=True, use_container_width=True)

# ==========================================
# TAB 2: DEEP DIVE (With ALL Conditions)
# ==========================================
with deep_dive_tab:
    st.header("🕵️ Forensic Analysis")
    if df.empty:
        st.warning("No data.")
    else:
        problematic = df[df['final_score'] < 3.0]
        options = problematic['order_id'].unique() if not problematic.empty else df['order_id'].unique()
        
        idx_arg = 0
        if 'deep_dive_selector' in st.session_state:
             if st.session_state.deep_dive_selector in options:
                 idx_arg = list(options).index(st.session_state.deep_dive_selector)

        selected_id = st.selectbox("Select Order:", options, index=idx_arg, key="deep_dive_selector")
        
        record_list = df[df['order_id'] == selected_id]
        if not record_list.empty:
            record = record_list.iloc[0]
            
            # --- DERIVED METRICS ---
            # Calculate metrics that aren't explicitly in CSV but are useful context
            ts = record['timestamp']
            day_name = ts.strftime("%A") # e.g., 'Monday'
            time_str = ts.strftime("%H:%M") # e.g., '14:30'
            is_weekend = "Yes" if ts.weekday() >= 5 else "No"
            lateness = record.get('lateness_min', 0)
            
            c1, c2 = st.columns([1, 2])
            with c1:
                st.markdown("#### 📸 Evidence")
                img_url = f"{BACKEND_BASE_URL}/images/{record['image_filename']}"
                st.image(img_url, use_container_width=True)
            
            with c2:
                st.markdown(f"### Order #{selected_id}")
                s_color = get_status_color(record['final_score'])
                st.markdown(f"## Score: :{s_color}[{record['final_score']} / 5.0]")
                
                # --- NEW: FULL CONDITIONS GRID ---
                st.markdown("#### 🌍 Environmental Conditions")
                g1, g2, g3 = st.columns(3)
                g1.metric("⏱️ Lateness", f"{lateness} min", delta_color="inverse")
                g2.metric("📏 Distance", f"{record.get('distance_km')} km")
                g3.metric("☁️ Weather", f"{record.get('weather')}")
                
                g4, g5, g6 = st.columns(3)
                g4.metric("🍳 Load", f"{record.get('restaurant_load')}")
                g5.metric("🕒 Time", f"{time_str}")
                g6.metric("📅 Weekend?", f"{is_weekend}")
                
                st.divider()
                st.markdown("#### 🤖 Diagnosis")
                st.info(f"**Insight:** {record.get('analysis_text', 'N/A')}")
                
                st.markdown("#### 🔧 Recommendation")
                rec = record.get('recommendation', 'N/A')
                if "Refund" in rec or "Check" in rec:
                    st.error(f"**Action:** {rec}")
                else:
                    st.success(f"**Action:** {rec}")

# ==========================================
# TAB 3: ANALYSIS
# ==========================================
with analysis_tab:
    st.header("🔬 Trends")
    if df.empty:
        st.info("No data.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Weather Impact")
            if 'weather' in df.columns:
                st.bar_chart(df.groupby('weather')['final_score'].mean(), color="#FF4B4B")
        with c2:
            st.subheader("Restaurant Load Impact")
            if 'restaurant_load' in df.columns:
                st.bar_chart(df.groupby('restaurant_load')['final_score'].mean(), color="#0068C9")
        
        st.subheader("Full History")
        if 'timestamp' in df.columns:
            st.line_chart(df.sort_values("timestamp"), x="timestamp", y="final_score")

# ==========================================
# TAB 4: EXPLORER
# ==========================================
with explorer_tab:
    st.header("🗂️ Full Mission Log")
    if not df.empty:
        st.dataframe(df, use_container_width=True)

if auto_refresh:
    time.sleep(2)
    st.rerun()