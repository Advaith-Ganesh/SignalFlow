"""Pytest configuration shared by the whole test suite.

The FastAPI app lives at backend/app (so `uvicorn app.main:app` works when
run from the backend/ directory), but backend/ is not an installed package.
Adding it to sys.path here -- before any test module is collected -- lets
test_api.py import `app.main` like a normal top-level import instead of
needing an inline sys.path hack in the test file itself.
"""

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
