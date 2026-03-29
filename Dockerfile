FROM python:3.11-slim

WORKDIR /app

# Copiar requirements
COPY backend/requirements.txt .

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Expor porta
EXPOSE 8501

# Comando para rodar
CMD ["streamlit", "run", "backend/auditoria_fiscal.py", "--server.port=8501", "--server.address=0.0.0.0"]