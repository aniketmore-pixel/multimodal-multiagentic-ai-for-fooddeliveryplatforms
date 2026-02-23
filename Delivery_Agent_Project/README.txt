HOW TO RUN THE DELIVERY AGENT AI

1. Install Dependencies:
   Open a terminal in this folder and run:
   pip install -r requirements.txt

2. Run the System (You need 3 separate terminals):

   TERMINAL 1 (The Brain):
   uvicorn backend:app --reload

   TERMINAL 2 (The Dashboard):
   streamlit run frontend.py

   TERMINAL 3 (The Autonomous Agent):
   python agent_simulation.py

3. Usage:
   - Open the URL shown in Terminal 2 (usually http://localhost:8501).
   - Go to the "🔴 Live Monitor" tab.
   - Watch the agent automatically process orders in real-time!