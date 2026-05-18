import sys
import os

# Add root directory to path if needed
sys.path.insert(0, os.path.dirname(__file__))

from backend.api import app
