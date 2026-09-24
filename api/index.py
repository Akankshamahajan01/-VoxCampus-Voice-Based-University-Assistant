"""
Vercel entry point for VoxCampus.
Vercel expects the ASGI app to be importable from api/index.py as `app`.
"""
import sys
import os

# Add project root to path so app.* imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app  # noqa: F401 — Vercel picks up `app`
