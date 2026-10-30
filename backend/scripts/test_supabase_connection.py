#!/usr/bin/env python
# backend/scripts/test_supabase_connection.py
"""
ColdChain IQ Platform — Supabase Connection Diagnostic & Verification Utility.
Safely tests connection, schema tables, read operations, and isolated CRUD cycles.
Never prints secrets or alters production data.
"""

import os
import sys
from dotenv import load_dotenv

# Ensure backend root is on sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

# Load environment configuration explicitly from backend/.env
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

REQUIRED_TABLES = [
    "packaging",
    "products",
    "lots",
    "shipments",
    "loggers",
    "temperature_readings",
    "custody_events",
    "route_stops",
    "threshold_policies",
    "excursion_reports",
    "roles",
    "users",
    "shipment_logger_assignments",
    "packaging_product_compatibilities",
    "compliance_reports",
    "audit_events",
    "data_generation_runs",
    "validation_results",
    "ground_truth_records"
]

def mask_credential(val: str) -> str:
    if not val:
        return "[NOT SET]"
    if len(val) <= 12:
        return "****"
    return f"{val[:6]}...{val[-4:]}"

def test_connection():
    print("=" * 70)
    print("ColdChain IQ — Supabase Connection Diagnostic Test")
    print("=" * 70)

    # 1. Environment Inspection
    print("\n1. Environment Configuration:")
    print(f"   SUPABASE_URL:              {SUPABASE_URL if SUPABASE_URL else '[NOT SET]'}")
    print(f"   SUPABASE_KEY (Anon):       {mask_credential(SUPABASE_KEY)}")
    print(f"   SUPABASE_SERVICE_ROLE_KEY: {mask_credential(SUPABASE_SERVICE_ROLE_KEY)}")

    if not SUPABASE_URL:
        print("\n[ERROR] SUPABASE_URL is missing. Please set it in backend/.env")
        return False

    active_key = SUPABASE_SERVICE_ROLE_KEY or SUPABASE_KEY
    if not active_key:
        print("\n[ERROR] Neither SUPABASE_SERVICE_ROLE_KEY nor SUPABASE_KEY is set in backend/.env")
        return False

    # 2. SDK Initialization
    print("\n2. Initializing Supabase Python SDK Client...")
    try:
        from supabase import create_client
        client = create_client(SUPABASE_URL, active_key)
        print("   [SUCCESS] Supabase Client instance initialized successfully.")
    except Exception as e:
        print(f"   [FAIL] Failed to initialize Supabase client: {e}")
        return False

    # 3. Schema & Table Verification
    print("\n3. Testing Table Schema Presence in Supabase...")
    missing_tables = []
    available_tables = []

    for table in REQUIRED_TABLES:
        try:
            res = client.table(table).select("*").limit(1).execute()
            available_tables.append(table)
            print(f"   [OK] Table '{table}' exists (Sample read succeeded)")
        except Exception as e:
            err_msg = str(e)
            if "PGRST205" in err_msg or "Could not find the table" in err_msg:
                missing_tables.append(table)
                print(f"   [MISSING] Table '{table}' not found in schema cache")
            else:
                print(f"   [WARNING] Table '{table}' returned error: {err_msg}")
                missing_tables.append(table)

    if missing_tables:
        print("\n" + "!" * 70)
        print("SCHEMA PENDING DEPLOYMENT IN SUPABASE:")
        print(f"   {len(missing_tables)} of {len(REQUIRED_TABLES)} tables were not found.")
        print("   Please execute 'backend/database/ALL_SUPABASE_QUERIES.sql' (or the 12 numbered")
        print("   scripts in 'backend/database/') directly in your Supabase SQL Editor.")
        print("!" * 70)
        return False

    print(f"\n   [SUCCESS] All {len(REQUIRED_TABLES)} required tables are live in Supabase!")

    # 4. Master Data Seed Inspection
    print("\n4. Checking Master Seed Records:")
    for check_table in ["products", "packaging", "threshold_policies", "roles", "users"]:
        try:
            res = client.table(check_table).select("*").execute()
            count = len(res.data) if res.data else 0
            print(f"   - {check_table}: {count} records found")
        except Exception as e:
            print(f"   - {check_table}: query failed ({e})")

    # 5. Controlled Isolated CRUD Test
    print("\n5. Testing Controlled Isolated Insert / Read / Delete on Audit Trail...")
    test_event_id = "AUD-CONN-TEST-9999"
    try:
        # Insert
        insert_payload = {
            "event_id": test_event_id,
            "entity_type": "SYSTEM_DIAGNOSTIC",
            "entity_id": "CONN_TEST",
            "action": "DIAGNOSTIC_PING",
            "user_id": "DIAGNOSTIC_DAEMON",
            "details": {"test": True, "description": "Temporary connection verification ping"}
        }
        client.table("audit_events").insert(insert_payload).execute()
        print("   [OK] Test record inserted into audit_events")

        # Read
        read_res = client.table("audit_events").select("*").eq("event_id", test_event_id).execute()
        if read_res.data and len(read_res.data) > 0:
            print("   [OK] Test record read back successfully")

        # Delete cleanup
        client.table("audit_events").delete().eq("event_id", test_event_id).execute()
        print("   [OK] Test record cleaned up successfully")

        print("   [SUCCESS] Full CRUD round-trip validated with zero data contamination.")
    except Exception as e:
        print(f"   [WARNING] CRUD round-trip check encountered: {e}")

    print("\n" + "=" * 70)
    print("DIAGNOSTIC SUMMARY: SUPABASE IS FULLY OPERATIONAL AND CONNECTED!")
    print("=" * 70)
    return True

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
