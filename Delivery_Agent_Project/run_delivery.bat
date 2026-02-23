@echo off

echo Starting System...

:: TERMINAL 1 - FastAPI Backend (Port 8000 default)
start cmd /k "echo Running Backend... && uvicorn backend:app --reload --port 8239"

:: Small delay
timeout /t 2 >nul

:: TERMINAL 2 - Streamlit Frontend
start cmd /k "echo Running Frontend... && streamlit run frontend.py --server.port 8275"

timeout /t 2 >nul

:: TERMINAL 3 - Autonomous Agent
start cmd /k "echo Running Agent Simulation... && python agent_simulation.py"

timeout /t 2 >nul

:: TERMINAL 4 - Dashboard Analytics API (Port 9578)
start cmd /k "echo Running Dashboard API on Port 9578... && uvicorn dashboard_api:app --host 0.0.0.0 --port 9578"

echo All services started successfully!
pause
