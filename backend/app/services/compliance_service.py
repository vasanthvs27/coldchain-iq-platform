# backend/app/services/compliance_service.py
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from app.config.supabase_client import supabase
from app.services.logger_service import LoggerService
from app.services.custody_service import CustodyService
from app.services.temperature_service import TemperatureService
from app.services.excursion_service import ExcursionService

class ComplianceService:
    @staticmethod
    def get_all_reports(page: int = 1, page_size: int = 50, status: Optional[str] = None) -> Dict[str, Any]:
        query = supabase.table("compliance_reports").select("*")
        if status:
            query = query.eq("compliance_status", status)
            
        offset = (page - 1) * page_size
        res = query.order("generated_at", desc=True).offset(offset).limit(page_size).execute()
        
        count_q = supabase.table("compliance_reports").select("report_id")
        if status:
            count_q = count_q.eq("compliance_status", status)
        count_res = count_q.execute()
        total = count_res.count or len(count_res.data)
        
        return {
            "items": res.data,
            "total": total,
            "page": page,
            "page_size": page_size
        }

    @staticmethod
    def get_report_by_id(report_id: str) -> Optional[Dict[str, Any]]:
        res = supabase.table("compliance_reports").select("*").eq("report_id", report_id).execute()
        return res.data[0] if res.data else None

    @staticmethod
    def get_report_for_shipment(shipment_id: str) -> Optional[Dict[str, Any]]:
        res = supabase.table("compliance_reports")\
            .select("*")\
            .eq("shipment_id", shipment_id)\
            .order("generated_at", desc=True)\
            .execute()
        return res.data[0] if res.data else None

    @staticmethod
    def analyze_shipment_compliance(shipment_id: str, applied_policy_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Comprehensive 12-Step Compliance Determination Engine.
        Enforces Business Rules 1-10 and Negative Scenarios 1-5.
        """
        reason_codes = []
        evidence_references = []
        
        # 1. Validate Shipment
        shipment_res = supabase.table("shipments").select("*").eq("shipment_id", shipment_id).execute()
        if not shipment_res.data:
            raise ValueError(f"Shipment '{shipment_id}' not found.")
        shipment = shipment_res.data[0]
        product_id = shipment["product_id"]
        lot_id = shipment["lot_id"]

        # 2. Validate Product & Lot
        prod_res = supabase.table("products").select("*").eq("product_id", product_id).execute()
        if not prod_res.data:
            raise ValueError(f"Associated Product '{product_id}' not found.")
        product = prod_res.data[0]

        lot_res = supabase.table("lots").select("*").eq("lot_id", lot_id).execute()
        if not lot_res.data:
            reason_codes.append("INVALID_LOT_REFERENCE")
        else:
            lot = lot_res.data[0]
            if lot.get("product_id") != product_id:
                reason_codes.append("LOT_PRODUCT_MISMATCH")

        # 3. Policy Selection & Validation (Rule 2 & Negative Scenario 2: POLICY_MISMATCH)
        applied_policy = None
        if applied_policy_id:
            pol_fetch = supabase.table("threshold_policies").select("*").eq("policy_id", applied_policy_id).execute()
            if pol_fetch.data:
                applied_policy = pol_fetch.data[0]

        if not applied_policy:
            # Query active policy for this product
            pol_fetch = supabase.table("threshold_policies")\
                .select("*")\
                .eq("product_id", product_id)\
                .eq("policy_status", "ACTIVE")\
                .execute()
            if pol_fetch.data:
                applied_policy = pol_fetch.data[0]

        if not applied_policy:
            # Fallback to product parameters
            applied_policy = {
                "policy_id": f"POL-DEFAULT-{product_id}",
                "product_id": product_id,
                "minimum_temperature": product.get("minimum_temperature", 2.0),
                "maximum_temperature": product.get("maximum_temperature", 8.0),
                "allowed_excursion_duration": product.get("allowed_excursion_duration", 60),
                "policy_version": "v1.0"
            }

        # Check for Rule 2 / Negative Scenario 2: Policy Mismatch
        policy_product_mismatch = False
        if applied_policy.get("product_id") != product_id:
            policy_product_mismatch = True
            reason_codes.append("POLICY_MISMATCH")
            evidence_references.append(
                f"Policy Mismatch: Applied policy '{applied_policy.get('policy_id')}' belongs to product '{applied_policy.get('product_id')}', but shipment is for product '{product_id}'."
            )

        # 4. Logger Assignment Validation (Rule 3 & Negative Scenario 1: UNASSIGNED_LOGGER)
        assignments = supabase.table("shipment_logger_assignments")\
            .select("*")\
            .eq("shipment_id", shipment_id)\
            .execute().data
            
        unassigned_logger_detected = False
        assigned_logger_ids = [a["logger_id"] for a in assignments]
        
        # 5. Calibration Validation (Rule 4)
        calibration_valid = True
        cal_status_str = "VALID"
        for lid in assigned_logger_ids:
            cal_check = LoggerService.validate_calibration(lid)
            if not cal_check.get("valid"):
                calibration_valid = False
                cal_status_str = cal_check.get("status", "EXPIRED")
                reason_codes.append("LOGGER_CALIBRATION_EXPIRED")
                evidence_references.append(f"Logger {lid} calibration expired on {cal_check.get('calibration_expiry')}")

        # 6. Temperature Readings & Missing Data (Rule 7 & Negative Scenario 3: MISSING_DATA)
        readings = supabase.table("temperature_readings")\
            .select("*")\
            .eq("shipment_id", shipment_id)\
            .order("recorded_at", desc=False)\
            .execute().data

        total_readings = len(readings)
        valid_readings = 0
        untrusted_readings = 0

        for r in readings:
            r_logger = r.get("logger_id")
            if r_logger not in assigned_logger_ids or r.get("reading_status") == "UNASSIGNED_LOGGER":
                unassigned_logger_detected = True
                untrusted_readings += 1
            else:
                valid_readings += 1

        if unassigned_logger_detected:
            reason_codes.append("UNASSIGNED_LOGGER")
            evidence_references.append(f"{untrusted_readings} temperature readings were recorded by unassigned data loggers.")

        # Detect Missing Data Gaps
        gap_analysis = TemperatureService.detect_missing_gaps(shipment_id)
        missing_count = gap_analysis.get("missing_reading_count", 0)
        if gap_analysis.get("has_gaps"):
            reason_codes.append("MISSING_DATA")
            evidence_references.append(
                f"Missing Telemetry Gaps: Expected reading completeness is {gap_analysis.get('completeness_pct')}%. Detected {len(gap_analysis.get('gaps', []))} gaps totaling {missing_count} missing intervals."
            )

        # 7. Excursion Duration Calculation (Rules 5, 6 & Negative Scenario 5)
        excursions = ExcursionService.analyze_shipment_excursions(shipment_id, applied_policy)
        max_deviation = 0.0
        max_duration = 0
        has_violating_excursion = False

        min_allowed = float(applied_policy["minimum_temperature"])
        max_allowed = float(applied_policy["maximum_temperature"])
        allowed_dur = int(applied_policy.get("allowed_excursion_duration", 60))

        for excr in excursions:
            dur = excr["calculated_duration"]
            if dur > max_duration:
                max_duration = dur

            obs_max = float(excr["maximum_observed_temperature"])
            obs_min = float(excr["minimum_observed_temperature"])
            dev_upper = max(0.0, obs_max - max_allowed)
            dev_lower = max(0.0, min_allowed - obs_min)
            max_dev_candidate = max(dev_upper, dev_lower)
            if max_dev_candidate > max_deviation:
                max_deviation = max_dev_candidate

            if dur > allowed_dur:
                has_violating_excursion = True
                reason_codes.append("TEMPERATURE_EXCURSION_EXCEEDED")
                evidence_references.append(
                    f"Excursion {excr['excursion_id']} duration ({dur} mins) exceeded allowable limit ({allowed_dur} mins). Observed: [{obs_min}°C, {obs_max}°C]."
                )

        # 8. Route Dwell Analysis (Rule 9)
        route_stops = supabase.table("route_stops")\
            .select("*")\
            .eq("shipment_id", shipment_id)\
            .order("stop_sequence", desc=False)\
            .execute().data
            
        for stop in route_stops:
            dwell = stop.get("dwell_duration", 0)
            if dwell > 240: # > 4 hours
                reason_codes.append("EXCESSIVE_ROUTE_DWELL")
                evidence_references.append(f"Excessive dwell of {dwell} minutes at stop '{stop.get('stop_name')}'.")

        # 9. Custody Chain Validation (Rule 8 & Negative Scenario 4: CUSTODY_GAP)
        custody_analysis = CustodyService.detect_custody_gaps(shipment_id)
        custody_completeness = custody_analysis.get("completeness_score", 100.0)
        if custody_analysis.get("has_gaps"):
            reason_codes.append("CUSTODY_GAP")
            for g in custody_analysis.get("gaps", []):
                evidence_references.append(g.get("description"))

        # 10. Final Compliance Decision Synthesis (Rule 10)
        # Decision precedence:
        # 1. Policy Mismatch blocks standard compliant release -> UNDER_REVIEW
        # 2. Confirmed Excursion Exceeding Limit -> NON_COMPLIANT
        # 3. Missing Data without enough evidence -> INCONCLUSIVE
        # 4. Unassigned Logger with suspect evidence -> UNDER_REVIEW
        # 5. Broken Custody Gap without confirmed excursion -> UNDER_REVIEW
        # 6. Expired Calibration without other failure -> INCONCLUSIVE
        # 7. Otherwise -> COMPLIANT

        final_decision = "COMPLIANT"
        if policy_product_mismatch:
            final_decision = "UNDER_REVIEW"
        elif has_violating_excursion:
            final_decision = "NON_COMPLIANT"
        elif gap_analysis.get("has_gaps") and (missing_count > 6 or gap_analysis.get("completeness_pct", 100) < 80):
            final_decision = "INCONCLUSIVE"
        elif unassigned_logger_detected and valid_readings == 0:
            final_decision = "INCONCLUSIVE"
        elif unassigned_logger_detected or custody_analysis.get("has_gaps"):
            final_decision = "UNDER_REVIEW"
        elif not calibration_valid:
            final_decision = "INCONCLUSIVE"

        # Calculate Compliance Score (0-100)
        score = 100.0
        if final_decision == "NON_COMPLIANT":
            score = max(10.0, 60.0 - (max_duration * 0.2) - (max_deviation * 2.0))
        elif final_decision == "INCONCLUSIVE":
            score = max(30.0, gap_analysis.get("completeness_pct", 50.0) * 0.7)
        elif final_decision == "UNDER_REVIEW":
            score = 65.0
        else:
            score = 98.5

        score = round(max(0.0, min(100.0, score)), 2)

        # 11. Create & Save Formal Compliance Report
        report_id = f"COMP-{shipment_id}"
        report_record = {
            "report_id": report_id,
            "shipment_id": shipment_id,
            "product_id": product_id,
            "lot_id": lot_id,
            "compliance_status": final_decision,
            "compliance_score": score,
            "total_readings": total_readings,
            "valid_readings": valid_readings,
            "missing_readings": missing_count,
            "excursion_count": len(excursions),
            "maximum_deviation": round(max_deviation, 2),
            "maximum_excursion_duration": max_duration,
            "calibration_status": cal_status_str,
            "custody_completeness": custody_completeness,
            "policy_version": applied_policy.get("policy_version", "v1.0"),
            "reason_codes": list(set(reason_codes)),
            "evidence_references": evidence_references,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

        supabase.table("compliance_reports").insert(report_record, upsert=True).execute()

        # Update shipment table compliance status
        supabase.table("shipments").update({
            "compliance_status": final_decision
        }).eq("shipment_id", shipment_id).execute()

        return report_record
