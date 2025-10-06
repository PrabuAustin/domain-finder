import os
import sys

# Ensure project modules import when running as a Vercel function
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
if PROJECT_ROOT not in sys.path:
	sys.path.insert(0, PROJECT_ROOT)

from domain_finder.api import app  # noqa: E402

# Vercel detects `app` as the ASGI callable
