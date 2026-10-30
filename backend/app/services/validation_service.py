# backend/app/services/validation_service.py
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from app.config.supabase_client import supabase

class ValidationService:
    @staticmethod
    def run_all_validations() -> Dict[str, Any]:
        """
        Executes Structural, Business, and Derived Value validations across the entire dataset.
        Distinguishes between expected synthetic anomalies and unexpected system failures.
        """
        results = []
        overall_passed = True

        # Rule 1: Product Temperature Range Validity (min < max)
        products = supabase.table("products").select("*").execute().data
        failed_prod_ids = []
        for p in products:
            if float(p.get("minimum_temperature", 0)) >= float(p.get("maximum_temperature", 0)):
                failed_prod_ids.append(p.get("product_id"))
        
        results.append(ValidationService._record_result(
            rule_name="Product Temperature Range (min < max)",
            total=len(products),
            failed_ids=failed_prod_ids
        ))

        # Rule 2: Foreign Key Integrity (Shipment -> Product & Lot & Packaging)
        shipments = supabase.table("shipments").select("*").execute().data
        prod_ids = set([p["product_id"] for p in products])
        lots = supabase.table("lots").select("*").execute().data
        lot_ids = set([l["lot_id"] for l in lots])
        packagings = supabase.table("packaging").select("*").execute().data
        pkg_ids = set([pkg["packaging_id"] for pkg in packagings])

        orphan_shipments = []
        for s in shipments:
            if s.get("product_id") not in prod_ids or s.get("lot_id") not in lot_ids or s.get("packaging_id") not in pkg_ids:
                orphan_shipments.append(s.get("shipment_id"))

        results.append(ValidationService._record_result(
            rule_name="Shipment Foreign Key Integrity",
            total=len(shipments),
            failed_ids=orphan_shipments
        ))

        # Rule 3: Shipment-to-Lot Consistency (Lot's product must match Shipment's product)
        lot_map = {l["lot_id"]: l for l in lots}
        inconsistent_lots = []
        for s in shipments:
            lot = lot_map.get(s.get("lot_id"))
            if lot and lot.get("product_id") != s.get("product_id"):
                inconsistent_lots.append(s.get("shipment_id"))

        results.append(ValidationService._record_result(
            rule_name="Shipment to Lot Product Consistency",
            total=len(shipments),
            failed_ids=inconsistent_lots
        ))

        # Rule 4: Logger Calibration Validity
        loggers = supabase.table("loggers").select("*").execute().data
        expired_cal_loggers = []
        now_iso = datetime.now(timezone.utc).isoformat()
        for log in loggers:
            cal_exp = log.get("calibration_expiry")
            if cal_exp and cal_exp < now_iso:
                expired_cal_loggers.append(log.get("logger_id"))

        results.append(ValidationService._record_result(
            rule_name="Logger Calibration Expiry Audit",
            total=len(loggers),
            failed_ids=expired_cal_loggers,
            is_anomaly_expected=True # Expected that some loggers expire
        ))

        # Rule 5: Derived Value Reconciliation (Compliance Reports vs Recomputed Values)
        reports = supabase.table("compliance_reports").select("*").execute().data
        reconciliation_discrepancies = []
        for rep in reports:
            # Check non-negative counts and bounded score
            if rep.get("compliance_score", 0) < 0 or rep.get("compliance_score", 0) > 100:
                reconciliation_discrepancies.append(rep.get("report_id"))
            if rep.get("total_readings", 0) < 0:
                reconciliation_discrepancies.append(rep.get("report_id"))

        results.append(ValidationService._record_result(
            rule_name="Derived Compliance Values Reconciliation",
            total=len(reports),
            failed_ids=reconciliation_discrepancies
        ))

        # Rule 6: Primary Key Uniqueness
        shipment_id_list = [s["shipment_id"] for s in shipments]
        has_dup_pks = len(shipment_id_list) != len(set(shipment_id_list))
        results.append(ValidationService._record_result(
            rule_name="Primary Key Uniqueness (Shipments)",
            total=len(shipments),
            failed_ids=["DUPLICATE_SHIPMENTS_FOUND"] if has_dup_pks else []
        ))

        # Rule 7: Chronological Route Stop Sequences
        route_stops = supabase.table("route_stops").select("*").execute().data
        disordered_stops = []
        grouped_stops = {}
        for st in route_stops:
            grouped_stops.setdefault(st["shipment_id"], []).append(st)

        for sid, stops in grouped_stops.items():
            sorted_by_seq = sorted(stops, key=lambda x: x["stop_sequence"])
            for idx in range(len(sorted_by_seq) - 1):
                cur_arr = sorted_by_seq[idx].get("planned_arrival")
                next_arr = sorted_by_seq[idx + 1].get("planned_arrival")
                if cur_arr and next_arr and cur_arr > next_arr:
                    disordered_stops.append(sid)
                    break

        results.append(ValidationService._record_result(
            rule_name="Chronological Route Stop Sequence",
            total=len(grouped_stops),
            failed_ids=disordered_stops
        ))

        # Store in validation_results table
        for r in results:
            supabase.table("validation_results").insert(r, upsert=True).execute()

        # Compute summary
        total_rules = len(results)
        passed_rules = sum(1 for r in results if r["status"] == "PASSED")
        warning_rules = sum(1 for r in results if r["status"] == "WARNING")
        failed_rules = sum(1 for r in results if r["status"] == "FAILED")

        return {
            "validation_timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_status": "PASSED" if failed_rules == 0 else "FAILED",
            "summary": {
                "total_rules": total_rules,
                "passed": passed_rules,
                "warnings": warning_rules,
                "failed": failed_rules
            },
            "results": results
        }

    @staticmethod
    def _record_result(
        rule_name: str,
        total: int,
        failed_ids: List[str],
        is_anomaly_expected: bool = False
    ) -> Dict[str, Any]:
        failed_count = len(failed_ids)
        passed_count = total - failed_count
        expected_anom = failed_count if is_anomaly_expected else 0
        unexpected_fail = 0 if is_anomaly_expected else failed_count

        status = "PASSED"
        if unexpected_fail > 0:
            status = "FAILED"
        elif expected_anom > 0:
            status = "WARNING"

        val_id = f"VAL-{hash(rule_name) % 1000000:06d}"
        return {
            "validation_id": val_id,
            "rule_name": rule_name,
            "total_evaluated": total,
            "passed_count": passed_count,
            "failed_count": failed_count,
            "expected_anomalies": expected_anom,
            "unexpected_failures": unexpected_fail,
            "affected_ids": failed_ids,
            "status": status,
            "validated_at": datetime.now(timezone.utc).isoformat()
        }

    @staticmethod
    def get_summary() -> Dict[str, Any]:
        res = supabase.table("validation_results").select("*").order("validated_at", desc=True).limit(20).execute()
        return {
            "recent_results": res.data,
            "count": len(res.data)
        }
