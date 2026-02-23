@echo off
echo Starting Food Quality Agent System...

:: Start FastAPI (Model API)
start cmd /k "cd food-quality-agent && uvicorn app:app --reload --port 9850"

:: Start Producer Interface (Flask)
start cmd /k "cd review submission && python producer_interface.py"

:: Start Realtime Dashboard (Flask)
start cmd /k "cd realtime-fq && python app.py"

:: Start Consumer
start cmd /k "cd realtime-fq && python consumer.py"

echo All services started!
