@echo off

start "" cmd /k "cd /d D:\coding-files\FoodQualityAgent && run_all.bat"

start "" cmd /k "cd /d C:\Users\Admin\BE-MPR && run_ux_agent.bat"
start "" cmd /k "cd /d C:\Users\Admin\Documents\Delivery_Agent_Project && run_delivery.bat"

REM Start churn-agent-agentic
start "" cmd /k "cd /d C:\Users\Admin\Documents\churn-agent-agentic && python app.py"

REM Start HTML server (same folder as this BAT file)
start "" cmd /k "cd /d %~dp0 && python app.py"

exit
