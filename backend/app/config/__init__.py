# backend/app/config/__init__.py
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "coldchain-iq-super-secret-key-2026")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "coldchain-iq-jwt-secret-key-2026")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    
    # Supabase Configuration
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    
    # Synthetic Data Parameters
    DEFAULT_RANDOM_SEED = 20261022
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    GENERATED_DIR = os.path.join(DATA_DIR, "generated")
    GROUND_TRUTH_DIR = os.path.join(DATA_DIR, "ground_truth")
    EXPORTS_DIR = os.path.join(DATA_DIR, "exports")
    MANIFESTS_DIR = os.path.join(DATA_DIR, "manifests")
    
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
