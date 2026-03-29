#!/bin/bash
pip install -r backend/requirements.txt
streamlit run backend/app.py --server.port=$PORT --server.address=0.0.0.0