# Script para iniciar Streamlit y FastAPI juntos en Windows (PowerShell)
Start-Process -NoNewWindow -FilePath "streamlit" -ArgumentList "run dashboard.py"
Start-Process -NoNewWindow -FilePath "uvicorn" -ArgumentList "api.main:app --reload"
