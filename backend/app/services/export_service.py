# backend/app/services/export_service.py
import os
import csv
import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List
from app.config.supabase_client import supabase
from app.config import Config

class ExportService:
    @staticmethod
    def export_all_datasets() -> Dict[str, Any]:
        """
        Exports all core entities and evaluations to CSV, JSON, and SQL seed formats.
        Generates manifest.json with SHA-256 checksums.
        """
        export_dir = Config.EXPORTS_DIR
        os.makedirs(export_dir, exist_ok=True)
        timestamp_str = datetime.now(timezone.utc).isoformat()

        tables_to_export = [
            "products",
            "lots",
            "shipments",
            "packaging",
            "loggers",
            "temperature_readings",
            "custody_events",
            "route_stops",
            "threshold_policies",
            "excursion_reports",
            "compliance_reports"
        ]

        file_manifest = {}

        for table in tables_to_export:
            records = supabase.table(table).select("*").execute().data
            
            # 1. Export CSV
            csv_filename = f"{table}.csv"
            csv_path = os.path.join(export_dir, csv_filename)
            if records:
                all_fields = set()
                for r in records:
                    all_fields.update(r.keys())
                fieldnames = sorted(list(all_fields))
                with open(csv_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
                    writer.writeheader()
                    for r in records:
                        clean_row = {}
                        for k, v in r.items():
                            clean_row[k] = json.dumps(v) if isinstance(v, (list, dict)) else v
                        writer.writerow(clean_row)
            else:
                with open(csv_path, "w", newline="", encoding="utf-8") as f:
                    pass

            # 2. Export JSON
            json_filename = f"{table}.json"
            json_path = os.path.join(export_dir, json_filename)
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=2)

            # Compute Checksums
            with open(csv_path, "rb") as f:
                csv_hash = hashlib.sha256(f.read()).hexdigest()

            file_manifest[table] = {
                "record_count": len(records),
                "csv_file": csv_filename,
                "csv_sha256": csv_hash,
                "json_file": json_filename
            }

        # 3. Export SQL Seed Data
        sql_filename = "seed_operational_dataset.sql"
        sql_path = os.path.join(export_dir, sql_filename)
        with open(sql_path, "w", encoding="utf-8") as f:
            f.write(f"-- ColdChain IQ Exported SQL Dataset\n-- Generated: {timestamp_str}\n\n")
            for table in ["products", "packaging", "lots", "shipments", "loggers"]:
                records = supabase.table(table).select("*").limit(200).execute().data
                for r in records:
                    cols = ", ".join(r.keys())
                    val_list = []
                    for v in r.values():
                        if v is not None:
                            escaped = str(v).replace("'", "''")
                            val_list.append(f"'{escaped}'")
                        else:
                            val_list.append("NULL")
                    vals = ", ".join(val_list)
                    f.write(f"INSERT INTO {table} ({cols}) VALUES ({vals}) ON CONFLICT DO NOTHING;\n")

        # 4. Manifest.json
        manifest_filename = "manifest.json"
        manifest_path = os.path.join(export_dir, manifest_filename)
        manifest_data = {
            "platform": "ColdChain IQ",
            "version": "1.0.0",
            "exported_at": timestamp_str,
            "export_directory": export_dir,
            "tables": file_manifest,
            "sql_seed": sql_filename
        }
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest_data, f, indent=2)

        return {
            "status": "SUCCESS",
            "export_path": export_dir,
            "manifest": manifest_data
        }
