#!/bin/bash

# Script para iniciar Streamlit y FastAPI juntos en Linux
echo "Iniciando servicios..."

# Activar el entorno virtual
source .venv/bin/activate

# Iniciar FastAPI en segundo plano
echo "Iniciando API FastAPI en http://localhost:8000"
uvicorn api.main:app --reload &

# Iniciar Streamlit en segundo plano
echo "Iniciando Dashboard Streamlit en http://localhost:8501"
streamlit run dashboard.py &

echo "Servicios iniciados! Puedes acceder a:"
echo "- Dashboard: http://localhost:8501"
echo "- API Docs: http://localhost:8000/docs"

# Esperar a que el usuario presione Ctrl+C
echo "Presiona Ctrl+C para detener los servicios"
wait