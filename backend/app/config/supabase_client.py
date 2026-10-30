# backend/app/config/supabase_client.py
"""
Centralized Supabase Client for ColdChain IQ Platform.
Provides direct integration with Supabase Python SDK.
Includes in-memory resilient fallback for local tests and offline execution
when live Supabase cloud credentials are not provided or unreachable.
"""

import os
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

class MockQueryResponse:
    def __init__(self, data: Any, count: Optional[int] = None):
        self.data = data
        self.count = count if count is not None else (len(data) if isinstance(data, list) else 1)
        self.error = None

STORAGE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "generated", "storage.json"))

class MockTableQuery:
    def __init__(self, table_name: str, storage: Dict[str, List[Dict[str, Any]]], on_change=None):
        self.table_name = table_name
        self.storage = storage
        self._on_change = on_change
        self._action = "select"
        self._payload = None
        self._filters = []
        self._limit = None
        self._offset = None
        self._order_col = None
        self._order_desc = False
        self._upsert = False

    def select(self, columns: str = "*", count: Optional[str] = None):
        self._action = "select"
        self._columns = columns
        return self

    def insert(self, values: Any, upsert: bool = False):
        self._action = "insert"
        self._payload = values
        self._upsert = upsert
        return self

    def update(self, values: Dict[str, Any]):
        self._action = "update"
        self._payload = values
        return self

    def delete(self):
        self._action = "delete"
        return self

    def eq(self, column: str, value: Any):
        self._filters.append(lambda r: str(r.get(column)) == str(value))
        return self

    def neq(self, column: str, value: Any):
        self._filters.append(lambda r: str(r.get(column)) != str(value))
        return self

    def gt(self, column: str, value: Any):
        self._filters.append(lambda r: r.get(column) is not None and r.get(column) > value)
        return self

    def gte(self, column: str, value: Any):
        self._filters.append(lambda r: r.get(column) is not None and r.get(column) >= value)
        return self

    def lt(self, column: str, value: Any):
        self._filters.append(lambda r: r.get(column) is not None and r.get(column) < value)
        return self

    def lte(self, column: str, value: Any):
        self._filters.append(lambda r: r.get(column) is not None and r.get(column) <= value)
        return self

    def in_(self, column: str, values: List[Any]):
        self._filters.append(lambda r: r.get(column) in values)
        return self

    def limit(self, count: int):
        self._limit = count
        return self

    def offset(self, start: int):
        self._offset = start
        return self

    def order(self, column: str, desc: bool = False):
        self._order_col = column
        self._order_desc = desc
        return self

    def execute(self) -> MockQueryResponse:
        records = self.storage.setdefault(self.table_name, [])

        if self._action == "insert":
            items = self._payload if isinstance(self._payload, list) else [self._payload]
            inserted = []
            pk_name = self._get_pk(self.table_name)
            for item in items:
                dict_copy = dict(item)
                if pk_name in dict_copy:
                    existing_idx = next((i for i, r in enumerate(records) if r.get(pk_name) == dict_copy[pk_name]), -1)
                    if existing_idx >= 0:
                        records[existing_idx].update(dict_copy)
                        inserted.append(records[existing_idx])
                        continue
                records.append(dict_copy)
                inserted.append(dict_copy)
            if self._on_change:
                self._on_change()
            return MockQueryResponse(inserted)

        # Apply filters
        matched = records
        for f in self._filters:
            matched = [r for r in matched if f(r)]

        if self._action == "update":
            updated = []
            for r in matched:
                r.update(self._payload)
                updated.append(dict(r))
            if self._on_change:
                self._on_change()
            return MockQueryResponse(updated)

        if self._action == "delete":
            deleted = list(matched)
            self.storage[self.table_name] = [r for r in records if r not in matched]
            if self._on_change:
                self._on_change()
            return MockQueryResponse(deleted)

        # SELECT action
        result = [dict(r) for r in matched]
        if self._order_col:
            result.sort(key=lambda x: str(x.get(self._order_col, "")), reverse=self._order_desc)
        if self._offset is not None:
            result = result[self._offset:]
        if self._limit is not None:
            result = result[:self._limit]

        return MockQueryResponse(result, count=len(matched))

    def _get_pk(self, table_name: str) -> str:
        pk_map = {
            "products": "product_id",
            "lots": "lot_id",
            "shipments": "shipment_id",
            "packaging": "packaging_id",
            "loggers": "logger_id",
            "temperature_readings": "reading_id",
            "custody_events": "custody_event_id",
            "route_stops": "route_stop_id",
            "threshold_policies": "policy_id",
            "excursion_reports": "excursion_id",
            "compliance_reports": "report_id",
            "users": "user_id",
            "roles": "role_id",
            "shipment_logger_assignments": "assignment_id",
            "packaging_product_compatibilities": "id",
            "audit_events": "event_id",
            "data_generation_runs": "run_id",
            "validation_results": "validation_id"
        }
        return pk_map.get(table_name, "id")

class MockSupabaseClient:
    """In-memory resilient client matching Supabase Python SDK API."""
    def __init__(self):
        self._storage: Dict[str, List[Dict[str, Any]]] = {}
        self._load_from_disk()
        if not self._storage.get("products"):
            self._seed_default_master_data()
            self._save_to_disk()

    def _save_to_disk(self):
        try:
            import json
            os.makedirs(os.path.dirname(STORAGE_PATH), exist_ok=True)
            with open(STORAGE_PATH, "w", encoding="utf-8") as f:
                json.dump(self._storage, f)
        except Exception:
            pass

    def _load_from_disk(self):
        try:
            import json
            if os.path.exists(STORAGE_PATH):
                with open(STORAGE_PATH, "r", encoding="utf-8") as f:
                    self._storage = json.load(f)
        except Exception:
            self._storage = {}

    def table(self, table_name: str) -> MockTableQuery:
        return MockTableQuery(table_name, self._storage, on_change=self._save_to_disk)

    def _seed_default_master_data(self):
        # 1. Packaging
        self._storage["packaging"] = [
            {
                "packaging_id": "PKG-001",
                "packaging_name": "AeroChill VIP Ultra 2-8C",
                "packaging_type": "VIP_CONTAINER",
                "minimum_temperature": 2.0,
                "maximum_temperature": 8.0,
                "validated_duration": 96,
                "insulation_type": "VACUUM_INSULATED_PANEL",
                "status": "QUALIFIED"
            },
            {
                "packaging_id": "PKG-002",
                "packaging_name": "CryoShipper DeepFreeze -80C",
                "packaging_type": "DRY_ICE_SHIPPER",
                "minimum_temperature": -90.0,
                "maximum_temperature": -60.0,
                "validated_duration": 120,
                "insulation_type": "DRY_ICE_VACUUM",
                "status": "QUALIFIED"
            },
            {
                "packaging_id": "PKG-003",
                "packaging_name": "BioShield Controlled Room 15-25C",
                "packaging_type": "GEL_PACK_BOX",
                "minimum_temperature": 15.0,
                "maximum_temperature": 25.0,
                "validated_duration": 72,
                "insulation_type": "POLYURETHANE",
                "status": "QUALIFIED"
            },
            {
                "packaging_id": "PKG-004",
                "packaging_name": "PolarGuard Active Reefer Unit",
                "packaging_type": "ACTIVE_REEFER",
                "minimum_temperature": 2.0,
                "maximum_temperature": 8.0,
                "validated_duration": 168,
                "insulation_type": "EXPANDED_POLYSTYRENE",
                "status": "QUALIFIED"
            },
            {
                "packaging_id": "PKG-005",
                "packaging_name": "CryoSafe Liquid Nitrogen Vapor",
                "packaging_type": "CRYOGENIC_DEWAR",
                "minimum_temperature": -196.0,
                "maximum_temperature": -150.0,
                "validated_duration": 240,
                "insulation_type": "SUPER_INSULATION_JACKET",
                "status": "QUALIFIED"
            }
        ]

        # 2. Products
        self._storage["products"] = [
            {
                "product_id": "PROD-001",
                "product_name": "VaxiGuard mRNA Covid Booster",
                "product_category": "VACCINE_ULTRA_COLD",
                "minimum_temperature": -80.0,
                "maximum_temperature": -60.0,
                "allowed_excursion_duration": 30,
                "default_packaging_id": "PKG-002",
                "shelf_life_days": 180,
                "description": "Lipid nanoparticle encapsulated mRNA vaccine requiring deep ultra-cold storage",
                "status": "ACTIVE",
                "effective_from": "2026-01-01T00:00:00Z"
            },
            {
                "product_id": "PROD-002",
                "product_name": "InsuliPure Rapid Recombinant",
                "product_category": "INSULIN_BIOLOGIC",
                "minimum_temperature": 2.0,
                "maximum_temperature": 8.0,
                "allowed_excursion_duration": 60,
                "default_packaging_id": "PKG-001",
                "shelf_life_days": 730,
                "description": "High-purity human insulin analog for diabetes management",
                "status": "ACTIVE",
                "effective_from": "2026-01-01T00:00:00Z"
            },
            {
                "product_id": "PROD-003",
                "product_name": "OncoMab Monoclonal Antibody",
                "product_category": "MONOCLONAL_ANTIBODY",
                "minimum_temperature": 2.0,
                "maximum_temperature": 8.0,
                "allowed_excursion_duration": 45,
                "default_packaging_id": "PKG-001",
                "shelf_life_days": 365,
                "description": "Targeted oncology immunotherapy biologic solution",
                "status": "ACTIVE",
                "effective_from": "2026-01-01T00:00:00Z"
            },
            {
                "product_id": "PROD-004",
                "product_name": "ImmunoGlobulin IV High-Purity",
                "product_category": "BLOOD_DERIVED_PLASMA",
                "minimum_temperature": 2.0,
                "maximum_temperature": 8.0,
                "allowed_excursion_duration": 90,
                "default_packaging_id": "PKG-001",
                "shelf_life_days": 540,
                "description": "Sterile intravenous immune globulin liquid formulation",
                "status": "ACTIVE",
                "effective_from": "2026-01-01T00:00:00Z"
            },
            {
                "product_id": "PROD-005",
                "product_name": "RegenStem Autologous Cell Therapy",
                "product_category": "CELL_AND_GENE_THERAPY",
                "minimum_temperature": -196.0,
                "maximum_temperature": -150.0,
                "allowed_excursion_duration": 15,
                "default_packaging_id": "PKG-005",
                "shelf_life_days": 90,
                "description": "Cryopreserved living cellular therapy for regenerative oncology",
                "status": "ACTIVE",
                "effective_from": "2026-01-01T00:00:00Z"
            },
            {
                "product_id": "PROD-006",
                "product_name": "CardioPlatelet Platelet Rich Plasma",
                "product_category": "ROOM_TEMP_BLOOD_PRODUCT",
                "minimum_temperature": 20.0,
                "maximum_temperature": 24.0,
                "allowed_excursion_duration": 120,
                "default_packaging_id": "PKG-003",
                "shelf_life_days": 7,
                "description": "Platelet suspension requiring gentle agitation and room temperature control",
                "status": "ACTIVE",
                "effective_from": "2026-01-01T00:00:00Z"
            }
        ]

        # 3. Packaging Compatibility
        self._storage["packaging_product_compatibilities"] = [
            {"id": "COMPAT-001", "product_id": "PROD-001", "packaging_id": "PKG-002", "qualified_status": "QUALIFIED", "max_transit_hours": 120},
            {"id": "COMPAT-002", "product_id": "PROD-002", "packaging_id": "PKG-001", "qualified_status": "QUALIFIED", "max_transit_hours": 96},
            {"id": "COMPAT-003", "product_id": "PROD-002", "packaging_id": "PKG-004", "qualified_status": "QUALIFIED", "max_transit_hours": 168},
            {"id": "COMPAT-004", "product_id": "PROD-003", "packaging_id": "PKG-001", "qualified_status": "QUALIFIED", "max_transit_hours": 96},
            {"id": "COMPAT-005", "product_id": "PROD-004", "packaging_id": "PKG-001", "qualified_status": "QUALIFIED", "max_transit_hours": 96},
            {"id": "COMPAT-006", "product_id": "PROD-005", "packaging_id": "PKG-005", "qualified_status": "QUALIFIED", "max_transit_hours": 240},
            {"id": "COMPAT-007", "product_id": "PROD-006", "packaging_id": "PKG-003", "qualified_status": "QUALIFIED", "max_transit_hours": 72}
        ]

        # 4. Threshold Policies
        self._storage["threshold_policies"] = [
            {"policy_id": "POL-2026-000001", "product_id": "PROD-001", "minimum_temperature": -80.0, "maximum_temperature": -60.0, "allowed_excursion_duration": 30, "policy_version": "v1.0", "policy_status": "ACTIVE"},
            {"policy_id": "POL-2026-000002", "product_id": "PROD-002", "minimum_temperature": 2.0, "maximum_temperature": 8.0, "allowed_excursion_duration": 60, "policy_version": "v1.0", "policy_status": "ACTIVE"},
            {"policy_id": "POL-2026-000003", "product_id": "PROD-003", "minimum_temperature": 2.0, "maximum_temperature": 8.0, "allowed_excursion_duration": 45, "policy_version": "v1.0", "policy_status": "ACTIVE"},
            {"policy_id": "POL-2026-000004", "product_id": "PROD-004", "minimum_temperature": 2.0, "maximum_temperature": 8.0, "allowed_excursion_duration": 90, "policy_version": "v1.0", "policy_status": "ACTIVE"},
            {"policy_id": "POL-2026-000005", "product_id": "PROD-005", "minimum_temperature": -196.0, "maximum_temperature": -150.0, "allowed_excursion_duration": 15, "policy_version": "v1.0", "policy_status": "ACTIVE"},
            {"policy_id": "POL-2026-000006", "product_id": "PROD-006", "minimum_temperature": 20.0, "maximum_temperature": 24.0, "allowed_excursion_duration": 120, "policy_version": "v1.0", "policy_status": "ACTIVE"}
        ]

        # 5. Roles & Users
        self._storage["roles"] = [
            {"role_id": "ROLE-01", "role_name": "Supplier", "description": "Biopharmaceutical supplier"},
            {"role_id": "ROLE-02", "role_name": "Planner", "description": "Supply chain planner"},
            {"role_id": "ROLE-03", "role_name": "Carrier/Warehouse Operator", "description": "Freight & cold storage operator"},
            {"role_id": "ROLE-04", "role_name": "Logistics Analyst", "description": "Quality and telemetry analyst"},
            {"role_id": "ROLE-05", "role_name": "Operations Manager", "description": "Operations and release authority"},
            {"role_id": "ROLE-06", "role_name": "Administrator", "description": "Full system administrator"}
        ]

        self._storage["users"] = [
            {
                "user_id": "USR-001",
                "email": "admin@coldchainiq.io",
                "password_hash": "scrypt:32768:8:1$uH34i0yW8$a4bb56133be46b0a996f8c5b59ddb96ee31ee9db94aa0f00f07fa14d9b3a32f65a1ea03eb08e6ba2629b009e6c2cb9842f1cf8ba6e8ec9842a225da1ca12536b",
                "full_name": "System Administrator",
                "role": "Administrator",
                "organization": "ColdChain IQ Global",
                "is_active": True
            },
            {
                "user_id": "USR-002",
                "email": "analyst@coldchainiq.io",
                "password_hash": "scrypt:32768:8:1$uH34i0yW8$a4bb56133be46b0a996f8c5b59ddb96ee31ee9db94aa0f00f07fa14d9b3a32f65a1ea03eb08e6ba2629b009e6c2cb9842f1cf8ba6e8ec9842a225da1ca12536b",
                "full_name": "Sarah Jenkins",
                "role": "Logistics Analyst",
                "organization": "PharmaLogistics Inc",
                "is_active": True
            }
        ]

def get_supabase_client():
    """
    Returns the initialized Supabase client.
    Connects to live Supabase using SUPABASE_SERVICE_ROLE_KEY or SUPABASE_KEY.
    If the remote database is unreachable or tables have not yet been provisioned via SQL Editor,
    provides a high-fidelity local resilient client so tests and operations never crash.
    """
    active_key = SUPABASE_SERVICE_ROLE_KEY or SUPABASE_KEY
    if SUPABASE_URL and active_key and not SUPABASE_URL.startswith("https://placeholder"):
        try:
            from supabase import create_client
            client = create_client(SUPABASE_URL, active_key)
            # Test if schema has been deployed
            client.table("products").select("product_id").limit(1).execute()
            print(f"[SupabaseClient] Successfully connected to live Supabase database at {SUPABASE_URL}")
            return client
        except Exception as e:
            # Table not found (PGRST205) or network offline: use local resilient client
            print(f"[SupabaseClient] Live Supabase initialized. Note: Remote tables not yet populated or offline ({type(e).__name__}). Using local store until SQL scripts are run in Supabase SQL Editor.")
            return MockSupabaseClient()
    return MockSupabaseClient()

# Central singleton instance used across all backend services
supabase = get_supabase_client()
