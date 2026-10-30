# backend/tests/conftest.py
import pytest
import os
import sys

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.config.supabase_client import supabase

@pytest.fixture(scope="session")
def app():
    app_instance = create_app()
    app_instance.config.update({
        "TESTING": True
    })
    return app_instance

@pytest.fixture(scope="session")
def client(app):
    return app.test_client()
