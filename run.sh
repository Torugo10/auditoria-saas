#!/bin/bash
set -e
export PYTHONUNBUFFERED=1
echo "🚀 Starting Streamlit app..."
streamlit run backend/auditoria_fiscal.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    2>&1 || {
    echo "❌ App crashed with error code $?"
    exit 1
}
