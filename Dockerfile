FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "backend/auditoria_fiscal.py", "--server.port=8501", "--server.address=0.0.0.0"]
