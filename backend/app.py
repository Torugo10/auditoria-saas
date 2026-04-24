"""Ponto de entrada oficial da aplicacao Streamlit."""

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.bootstrap import bootstrap_streamlit_app


bootstrap_streamlit_app()

