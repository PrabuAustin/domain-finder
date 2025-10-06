import os
import sys

# Ensure the project root is on sys.path so `domain_finder` can be imported
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# Expose the FastAPI ASGI app for Vercel
from domain_finder.api import app  # noqa: E402


