# backend/app/services/excursion_service.py
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from app.config.supabase_client import supabase

class ExcursionService:
    @staticmethod
    def get_all(shipment_id: Optional[str] = None, severity: Optional[str] = None, page: int = 1, page_size: int = 50) -> Dict[str, Any]:
        query = supabase.table("excursion_reports").select("*")
        if shipment_id:
            query = query.eq("shipment_id", shipment_id)
        if severity:
            query = query.eq("severity", severity)
            
        offset = (page - 1) * page_size
        res = query.order("start_timestamp", desc=True).offset(offset).limit(page_size).execute()
        
        count_q = supabase.table("excursion_reports").select("excursion_id")
        if shipment_id:
            count_q = count_q.eq("shipment_id", shipment_id)
        count_res = count_q.execute()
        total = count_res.count or len(count_res.data)
        
        return {
            "items": res.data,
            "total": total,
            "page": page,
            "page_size": page_size
        }

    @staticmethod
    def get_by_id(excursion_id: str) -> Optional[Dict[str, Any]]:
        res = supabase.table("excursion_reports").select("*").eq("excursion_id", excursion_id).execute()
        return res.data[0] if res.data else None

    @staticmethod
    def update_investigation(excursion_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        res = supabase.table("excursion_reports").update(data).eq("excursion_id", excursion_id).execute()
        return res.data[0] if res.data else None

    @staticmethod
    def analyze_shipment_excursions(shipment_id: str, custom_policy: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Rules 5 & 6 & Negative Scenario 5 (Isolation):
        Calculates excursions strictly from readings belonging to the same shipment_id.
        Prevents combining readings from unrelated shipments.
        """
        # Fetch shipment
        shipment_res = supabase.table("shipments").select("*").eq("shipment_id", shipment_id).execute()
        if not shipment_res.data:
            return []
        shipment = shipment_res.data[0]
        product_id = shipment["product_id"]
        lot_id = shipment["lot_id"]

        # Determine policy
        policy = custom_policy
        if not policy:
            pol_res = supabase.table("threshold_policies")\
                .select("*")\
                .eq("product_id", product_id)\
                .eq("policy_status", "ACTIVE")\
                .execute()
            policy = pol_res.data[0] if pol_res.data else {
                "minimum_temperature": 2.0,
                "maximum_temperature": 8.0,
                "allowed_excursion_duration": 60
            }

        min_temp = float(policy["minimum_temperature"])
        max_temp = float(policy["maximum_temperature"])
        allowed_dur = int(policy.get("allowed_excursion_duration", 60))

        # Query readings STRICTLY filtered by shipment_id to isolate from other shipments
        readings_res = supabase.table("temperature_readings")\
            .select("*")\
            .eq("shipment_id", shipment_id)\
            .order("recorded_at", desc=False)\
            .execute()

        readings = readings_res.data
        if not readings:
            return []

        excursions = []
        current_streak = []
        streak_type = None # UPPER_EXCURSION or LOWER_EXCURSION

        def evaluate_and_record_streak(streak, stype):
            if not streak:
                return
            start_time = datetime.fromisoformat(streak[0]["recorded_at"].replace("Z", "+00:00"))
            end_time = datetime.fromisoformat(streak[-1]["recorded_at"].replace("Z", "+00:00"))
            # duration between start and end reading (plus reading interval duration of 10 min for single reading or interval)
            raw_diff_minutes = (end_time - start_time).total_seconds() / 60.0
            calc_duration = max(10, int(round(raw_diff_minutes + 10)))

            streak_temps = [float(r["corrected_temperature"]) for r in streak]
            min_obs = min(streak_temps)
            max_obs = max(streak_temps)

            # Determine severity
            if calc_duration > allowed_dur * 2:
                severity = "CRITICAL"
            elif calc_duration > allowed_dur:
                severity = "HIGH"
            elif calc_duration > allowed_dur * 0.5:
                severity = "MEDIUM"
            else:
                severity = "LOW"

            decision = "NON_COMPLIANT" if calc_duration > allowed_dur else "COMPLIANT"

            excr_id = f"EXCR-{shipment_id[:12]}-{len(excursions)+1:02d}"
            excursion_record = {
                "excursion_id": excr_id,
                "shipment_id": shipment_id,
                "product_id": product_id,
                "lot_id": lot_id,
                "logger_id": streak[0]["logger_id"],
                "start_timestamp": streak[0]["recorded_at"],
                "end_timestamp": streak[-1]["recorded_at"],
                "calculated_duration": calc_duration,
                "minimum_observed_temperature": round(min_obs, 2),
                "maximum_observed_temperature": round(max_obs, 2),
                "severity": severity,
                "issue_type": stype,
                "investigation_status": "OPEN",
                "compliance_decision": decision,
                "evidence_reference": f"Readings: {streak[0]['reading_id']} to {streak[-1]['reading_id']} ({len(streak)} samples)",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            excursions.append(excursion_record)

        for r in readings:
            temp = float(r["corrected_temperature"])
            if temp > max_temp:
                if streak_type == "UPPER_EXCURSION":
                    current_streak.append(r)
                else:
                    evaluate_and_record_streak(current_streak, streak_type)
                    current_streak = [r]
                    streak_type = "UPPER_EXCURSION"
            elif temp < min_temp:
                if streak_type == "LOWER_EXCURSION":
                    current_streak.append(r)
                else:
                    evaluate_and_record_streak(current_streak, streak_type)
                    current_streak = [r]
                    streak_type = "LOWER_EXCURSION"
            else:
                evaluate_and_record_streak(current_streak, streak_type)
                current_streak = []
                streak_type = None

        evaluate_and_record_streak(current_streak, streak_type)
        return excursions

    @staticmethod
    def detect_cross_shipment_anomaly(proposed_excursions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Negative Scenario 5:
        Detects if an excursion calculation incorrectly pooled readings from multiple different shipments.
        Recalculates independently for each shipment.
        """
        shipment_ids = list(set([e.get("shipment_id") for e in proposed_excursions if e.get("shipment_id")]))
        if len(shipment_ids) > 1:
            # Cross shipment contamination detected!
            isolated_results = {}
            for sid in shipment_ids:
                isolated_results[sid] = ExcursionService.analyze_shipment_excursions(sid)
            return {
                "detected": True,
                "error_code": "CROSS_SHIPMENT_DURATION",
                "message": f"Cross-shipment duration contamination detected across shipments {shipment_ids}. Recalculated independently.",
                "isolated_excursions": isolated_results
            }
        return {"detected": False, "error_code": None}
