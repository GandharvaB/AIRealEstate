import sys
import os

# Add root directory to path so we can import from backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.api import app
