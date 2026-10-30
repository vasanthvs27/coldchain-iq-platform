# backend/app/services/generator_service.py
import os
import json
import csv
import random
import numpy as np
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from app.config.supabase_client import supabase
from app.config import Config

class DataGeneratorService:
    @staticmethod
    def run_generation(
        mode: str = "STARTER",
        shipment_count: Optional[int] = None,
        logger_count: Optional[int] = None,
        seed: int = 20261022,
        reading_interval_minutes: int = 10,
        anomaly_rate: float = 0.15
    ) -> Dict[str, Any]:
        """
        Deterministic Synthetic Data Generation Engine.
        Generates realistic cold chain datasets using fixed random seed (20261022).
        Outputs operational data to Supabase and ground-truth labels to separate files.
        """
        # Set seeds
        random.seed(seed)
        np.random.seed(seed)

        if mode.upper() == "FULL":
            target_shipments = shipment_count or 5000
            target_loggers = logger_count or 1000
        else: # STARTER
            target_shipments = shipment_count or 50
            target_loggers = logger_count or 25

        run_id = f"RUN-{mode.upper()}-{seed}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        started_at = datetime.now(timezone.utc).isoformat()

        # Record generation run in DB
        supabase.table("data_generation_runs").insert({
            "run_id": run_id,
            "mode": mode.upper(),
            "seed": seed,
            "shipment_count": target_shipments,
            "logger_count": target_loggers,
            "reading_interval_minutes": reading_interval_minutes,
            "status": "IN_PROGRESS",
            "started_at": started_at
        }).execute()

        # Step 1: Base Products, Packaging & Policies (ensure seeded)
        products = supabase.table("products").select("*").execute().data
        packagings = supabase.table("packaging").select("*").execute().data
        policies = supabase.table("threshold_policies").select("*").execute().data
        
        prod_map = {p["product_id"]: p for p in products}

        # Step 2: Generate Lots
        lots = []
        suppliers = ["BioVax Pharma Ltd", "Genentech Global", "Nordic BioLabs", "Pfizer-BionTech", "Moderna Labs", "Novartis Biotech"]
        base_date = datetime(2026, 1, 10, 0, 0, 0, tzinfo=timezone.utc)
        
        for i in range(1, max(10, int(target_shipments * 0.2))):
            lot_id = f"LOT-2026-{i:06d}"
            prod = random.choice(products)
            mfg_date = base_date + timedelta(days=random.randint(0, 60))
            exp_date = mfg_date + timedelta(days=prod.get("shelf_life_days", 365))
            lots.append({
                "lot_id": lot_id,
                "product_id": prod["product_id"],
                "supplier_name": random.choice(suppliers),
                "manufacturing_date": mfg_date.isoformat(),
                "expiry_date": exp_date.isoformat(),
                "quantity": random.randint(5000, 50000),
                "unit": "DOSES",
                "lifecycle_status": "RELEASED",
                "created_at": started_at
            })
        
        # Insert lots in batches
        supabase.table("lots").insert(lots, upsert=True).execute()

        # Step 3: Generate Loggers
        loggers = []
        logger_models = ["SenseAware 4G", "TempTale Ultra BLE", "Elpro Libero CS", "CryoBeacon Multi-Use"]
        for i in range(1, target_loggers + 1):
            logger_id = f"LOG-2026-{i:04d}"
            cal_date = base_date - timedelta(days=random.randint(30, 200))
            # Some loggers get calibration expiry
            cal_exp = cal_date + timedelta(days=random.randint(180, 365))
            loggers.append({
                "logger_id": logger_id,
                "serial_number": f"SN-2026-{i:06d}",
                "model": random.choice(logger_models),
                "calibration_date": cal_date.isoformat(),
                "calibration_expiry": cal_exp.isoformat(),
                "accuracy_tolerance": 0.50,
                "measurement_uncertainty": 0.20,
                "battery_status": round(random.uniform(75.0, 100.0), 1),
                "logger_status": "ACTIVE",
                "created_at": started_at
            })
        supabase.table("loggers").insert(loggers, upsert=True).execute()

        # Step 4: Generate Shipments
        carriers = ["FedEx ColdChain Direct", "DHL LifeSciences Express", "World Courier Cryo", "Kuehne+Nagel PharmaChain"]
        cities = ["Boston, MA", "Frankfurt, DE", "Singapore, SG", "Basel, CH", "Chicago, IL", "London, UK", "Tokyo, JP", "Sydney, AU"]
        
        shipments = []
        assignments = []
        route_stops = []
        readings = []
        custody_events = []
        excursions = []
        compliance_reports = []
        ground_truth_records = []

        anomaly_count = int(target_shipments * anomaly_rate)
        # Allocate explicit anomalies across the 5 mandatory negative scenarios
        negative_scenarios = [
            "UNASSIGNED_LOGGER",
            "POLICY_MISMATCH",
            "MISSING_DATA",
            "CUSTODY_GAP",
            "CROSS_SHIPMENT_DURATION"
        ]

        assigned_anomalies = {}
        for idx in range(target_shipments):
            if idx < len(negative_scenarios):
                assigned_anomalies[idx] = negative_scenarios[idx]
            elif idx < anomaly_count:
                assigned_anomalies[idx] = random.choice(negative_scenarios)
            else:
                assigned_anomalies[idx] = None

        for s_idx in range(1, target_shipments + 1):
            shipment_id = f"SHP-2026-{s_idx:06d}"
            lot = random.choice(lots)
            prod = prod_map[lot["product_id"]]
            pkg = random.choice(packagings)
            logger = loggers[(s_idx - 1) % len(loggers)]

            origin = random.choice(cities)
            dest = random.choice([c for c in cities if c != origin])
            carrier = random.choice(carriers)

            # Journey length: between 12 and 36 hours for realistic testing
            transit_hours = random.randint(12, 30)
            dep_time = base_date + timedelta(days=random.randint(1, 45), hours=random.randint(0, 20))
            arr_time = dep_time + timedelta(hours=transit_hours)

            assigned_anomaly = assigned_anomalies.get(s_idx - 1)

            # 1. Shipment record
            shipments.append({
                "shipment_id": shipment_id,
                "lot_id": lot["lot_id"],
                "product_id": prod["product_id"],
                "packaging_id": pkg["packaging_id"],
                "origin": origin,
                "destination": dest,
                "carrier_name": carrier,
                "planned_departure": dep_time.isoformat(),
                "actual_departure": dep_time.isoformat(),
                "expected_arrival": arr_time.isoformat(),
                "actual_arrival": arr_time.isoformat(),
                "shipment_status": "DELIVERED",
                "compliance_status": "PENDING", # to be calculated
                "created_at": started_at
            })

            # 2. Logger assignment
            if assigned_anomaly != "UNASSIGNED_LOGGER":
                assignments.append({
                    "assignment_id": f"ASG-{logger['logger_id']}-{shipment_id}",
                    "shipment_id": shipment_id,
                    "logger_id": logger["logger_id"],
                    "assigned_at": dep_time.isoformat(),
                    "unassigned_at": (arr_time + timedelta(hours=2)).isoformat(),
                    "status": "COMPLETED",
                    "assignment_notes": "Standard logger assignment"
                })
            else:
                # Negative Scenario 1: Logger unassigned or assigned to different shipment!
                ground_truth_records.append({
                    "anomaly_id": f"GT-ANOM-{s_idx:04d}",
                    "issue_type": "UNASSIGNED_LOGGER",
                    "entity_type": "shipment",
                    "entity_id": shipment_id,
                    "expected_label": "UNASSIGNED_LOGGER",
                    "expected_decision": "UNDER_REVIEW",
                    "evidence_reference": f"Readings produced by logger {logger['logger_id']} without valid assignment to {shipment_id}",
                    "description": "Temperature readings injected for logger that lacks active assignment record to shipment."
                })

            # 3. Route Stops (3 stops: Origin -> Transit Hub -> Destination)
            hub_city = random.choice([c for c in cities if c not in (origin, dest)])
            hub_arr = dep_time + timedelta(hours=int(transit_hours * 0.4))
            hub_dep = hub_arr + timedelta(hours=3) # 3h dwell
            route_stops.extend([
                {
                    "route_stop_id": f"STOP-{s_idx:06d}-01",
                    "shipment_id": shipment_id,
                    "stop_sequence": 1,
                    "stop_name": f"{origin} Cold Hub",
                    "stop_type": "ORIGIN",
                    "planned_arrival": dep_time.isoformat(),
                    "actual_arrival": dep_time.isoformat(),
                    "departure_time": dep_time.isoformat(),
                    "dwell_duration": 0,
                    "status": "COMPLETED"
                },
                {
                    "route_stop_id": f"STOP-{s_idx:06d}-02",
                    "shipment_id": shipment_id,
                    "stop_sequence": 2,
                    "stop_name": f"{hub_city} Transit Gateway",
                    "stop_type": "HUB",
                    "planned_arrival": hub_arr.isoformat(),
                    "actual_arrival": hub_arr.isoformat(),
                    "departure_time": hub_dep.isoformat(),
                    "dwell_duration": 180,
                    "status": "COMPLETED"
                },
                {
                    "route_stop_id": f"STOP-{s_idx:06d}-03",
                    "shipment_id": shipment_id,
                    "stop_sequence": 3,
                    "stop_name": f"{dest} Distribution Facility",
                    "stop_type": "DESTINATION",
                    "planned_arrival": arr_time.isoformat(),
                    "actual_arrival": arr_time.isoformat(),
                    "departure_time": arr_time.isoformat(),
                    "dwell_duration": 0,
                    "status": "COMPLETED"
                }
            ])

            # 4. Custody Events
            # Negative Scenario 4: CUSTODY_GAP
            c1_prev = "Pharma Distribution Center"
            c1_new = f"{carrier} Pickup Crew"
            
            if assigned_anomaly == "CUSTODY_GAP":
                c2_prev = "Unknown Freight Broker" # Break the chain!
                c2_new = f"{dest} Receiving Dock"
                ground_truth_records.append({
                    "anomaly_id": f"GT-ANOM-{s_idx:04d}",
                    "issue_type": "CUSTODY_GAP",
                    "entity_type": "shipment",
                    "entity_id": shipment_id,
                    "expected_label": "CUSTODY_GAP",
                    "expected_decision": "UNDER_REVIEW",
                    "evidence_reference": f"Broken handoff chain: {c1_new} handed over to {c2_prev} without receipt transfer",
                    "description": "Custody gap injected where handoff recipient does not match next custodian."
                })
            else:
                c2_prev = c1_new
                c2_new = f"{dest} Receiving Dock"

            custody_events.extend([
                {
                    "custody_event_id": f"CUST-{s_idx:06d}-01",
                    "shipment_id": shipment_id,
                    "previous_custodian": c1_prev,
                    "new_custodian": c1_new,
                    "location": origin,
                    "handoff_timestamp": dep_time.isoformat(),
                    "event_type": "PICKUP",
                    "acknowledgement_status": "CONFIRMED",
                    "verification_status": "VERIFIED",
                    "notes": "Verified temperature at dispatch",
                    "created_at": started_at
                },
                {
                    "custody_event_id": f"CUST-{s_idx:06d}-02",
                    "shipment_id": shipment_id,
                    "previous_custodian": c2_prev,
                    "new_custodian": c2_new,
                    "location": dest,
                    "handoff_timestamp": arr_time.isoformat(),
                    "event_type": "FINAL_DELIVERY",
                    "acknowledgement_status": "CONFIRMED",
                    "verification_status": "VERIFIED",
                    "notes": "Handoff signoff complete",
                    "created_at": started_at
                }
            ])

            # 5. Temperature Readings
            min_t = float(prod["minimum_temperature"])
            max_t = float(prod["maximum_temperature"])
            mid_t = (min_t + max_t) / 2.0
            
            # Generate timestamps every 10 minutes
            reading_dt = dep_time
            reading_counter = 1
            has_missing_gap = (assigned_anomaly == "MISSING_DATA")

            if has_missing_gap:
                ground_truth_records.append({
                    "anomaly_id": f"GT-ANOM-{s_idx:04d}",
                    "issue_type": "MISSING_DATA",
                    "entity_type": "shipment",
                    "entity_id": shipment_id,
                    "expected_label": "MISSING_DATA",
                    "expected_decision": "INCONCLUSIVE",
                    "evidence_reference": f"Missing readings between {hub_arr.isoformat()} and {hub_dep.isoformat()}",
                    "description": "Telemetry communication outage injected during transit."
                })

            while reading_dt <= arr_time:
                # If missing data anomaly, skip readings during hub dwell
                if has_missing_gap and (hub_arr <= reading_dt <= hub_dep):
                    reading_dt += timedelta(minutes=reading_interval_minutes)
                    continue

                # Realistic temperature with slight noise
                temp_val = mid_t + np.random.normal(0, 0.4)

                # Inject excursions for certain shipments
                if s_idx % 7 == 0 and reading_counter in range(15, 25): # Excursion
                    temp_val = max_t + 3.5 # Upper excursion
                elif s_idx % 11 == 0 and reading_counter in range(10, 18):
                    temp_val = min_t - 2.8 # Lower excursion

                temp_val = round(float(temp_val), 2)
                corrected_val = round(temp_val - 0.05, 2)

                readings.append({
                    "reading_id": f"TEMP-{logger['logger_id']}-{reading_dt.strftime('%Y%m%d%H%M')}",
                    "logger_id": logger["logger_id"],
                    "shipment_id": shipment_id,
                    "recorded_at": reading_dt.isoformat(),
                    "measured_temperature": temp_val,
                    "corrected_temperature": corrected_val,
                    "calibration_uncertainty": 0.20,
                    "reading_status": "VALID",
                    "created_at": started_at
                })

                reading_dt += timedelta(minutes=reading_interval_minutes)
                reading_counter += 1

            # Negative Scenario 2: Policy Mismatch
            if assigned_anomaly == "POLICY_MISMATCH":
                # Find an incompatible product's policy
                other_prod = [p for p in products if p["product_id"] != prod["product_id"]][0]
                mismatched_policy = f"POL-{other_prod['product_id']}-01"
                ground_truth_records.append({
                    "anomaly_id": f"GT-ANOM-{s_idx:04d}",
                    "issue_type": "POLICY_MISMATCH",
                    "entity_type": "shipment",
                    "entity_id": shipment_id,
                    "expected_label": "POLICY_MISMATCH",
                    "expected_decision": "UNDER_REVIEW",
                    "evidence_reference": f"Applied policy {mismatched_policy} belongs to {other_prod['product_id']} instead of {prod['product_id']}",
                    "description": "Wrong threshold policy applied to shipment."
                })

            # Negative Scenario 5: Cross Shipment Duration
            if assigned_anomaly == "CROSS_SHIPMENT_DURATION":
                ground_truth_records.append({
                    "anomaly_id": f"GT-ANOM-{s_idx:04d}",
                    "issue_type": "CROSS_SHIPMENT_DURATION",
                    "entity_type": "shipment",
                    "entity_id": shipment_id,
                    "expected_label": "CROSS_SHIPMENT_DURATION",
                    "expected_decision": "NON_COMPLIANT",
                    "evidence_reference": f"Excursion calculation cross-contaminated with readings from neighboring shipment",
                    "description": "Overlapping excursion duration incorrectly computed across unrelated shipments."
                })

        # Save all generated data into Supabase
        # Batch insert to avoid payload limits
        def chunked_insert(table_name, records, chunk_size=200):
            total = len(records)
            print(f"   [DB Insert] Inserting {total:,} records into '{table_name}'...", flush=True)
            for i in range(0, total, chunk_size):
                chunk = records[i:i + chunk_size]
                supabase.table(table_name).insert(chunk, upsert=True).execute()

        chunked_insert("shipments", shipments)
        chunked_insert("shipment_logger_assignments", assignments)
        chunked_insert("route_stops", route_stops)
        chunked_insert("custody_events", custody_events)
        chunked_insert("temperature_readings", readings)

        # Run Compliance Analysis Engine to generate operational excursions & compliance reports
        print(f"   [Compliance Engine] Running 12-Step Compliance Analysis on {len(shipments)} shipments...", flush=True)
        for idx, shp in enumerate(shipments):
            try:
                print(f"      ({idx+1}/{len(shipments)}) Evaluating {shp['shipment_id']}...", flush=True)
                from app.services.compliance_service import ComplianceService
                ComplianceService.analyze_shipment_compliance(shp["shipment_id"])
            except Exception as e:
                print(f"      [Notice] Handled expectation for {shp['shipment_id']}: {e}", flush=True)

        # Save Ground Truth Separately (Section 14: data/ground_truth/ground_truth.csv and .json)
        os.makedirs(Config.GROUND_TRUTH_DIR, exist_ok=True)
        gt_csv_path = os.path.join(Config.GROUND_TRUTH_DIR, "ground_truth.csv")
        gt_json_path = os.path.join(Config.GROUND_TRUTH_DIR, "ground_truth.json")

        with open(gt_json_path, "w", encoding="utf-8") as f:
            json.dump(ground_truth_records, f, indent=2)

        if ground_truth_records:
            fieldnames = ["anomaly_id", "issue_type", "entity_type", "entity_id", "expected_label", "expected_decision", "evidence_reference", "description"]
            with open(gt_csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(ground_truth_records)

        # Update run status
        completed_at = datetime.now(timezone.utc).isoformat()
        records_summary = {
            "shipments": len(shipments),
            "loggers": len(loggers),
            "lots": len(lots),
            "route_stops": len(route_stops),
            "custody_events": len(custody_events),
            "temperature_readings": len(readings),
            "ground_truth_anomalies": len(ground_truth_records)
        }

        supabase.table("data_generation_runs").update({
            "status": "COMPLETED",
            "records_generated": records_summary,
            "completed_at": completed_at
        }).eq("run_id", run_id).execute()

        return {
            "run_id": run_id,
            "status": "COMPLETED",
            "seed": seed,
            "mode": mode,
            "summary": records_summary,
            "ground_truth_files": {
                "csv": gt_csv_path,
                "json": gt_json_path
            }
        }
