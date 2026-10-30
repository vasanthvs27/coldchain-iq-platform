# backend/app/services/temperature_service.py
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from app.config.supabase_client import supabase

class TemperatureService:
    @staticmethod
    def get_readings(
        shipment_id: Optional[str] = None,
        logger_id: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 100
    ) -> Dict[str, Any]:
        query = supabase.table("temperature_readings").select("*")
        if shipment_id:
            query = query.eq("shipment_id", shipment_id)
        if logger_id:
            query = query.eq("logger_id", logger_id)
        if status:
            query = query.eq("reading_status", status)
        
        offset = (page - 1) * page_size
        res = query.order("recorded_at", desc=False).offset(offset).limit(page_size).execute()
        
        count_q = supabase.table("temperature_readings").select("reading_id")
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
    def get_by_id(reading_id: str) -> Optional[Dict[str, Any]]:
        res = supabase.table("temperature_readings").select("*").eq("reading_id", reading_id).execute()
        return res.data[0] if res.data else None

    @staticmethod
    def insert_reading(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ingests a temperature reading and validates logger assignment.
        Rule 3 & Negative Scenario 1 (UNASSIGNED_LOGGER).
        """
        shipment_id = data.get("shipment_id")
        logger_id = data.get("logger_id")
        recorded_at_str = data.get("recorded_at")
        
        if not data.get("created_at"):
            data["created_at"] = datetime.now(timezone.utc).isoformat()
        if not data.get("reading_status"):
            data["reading_status"] = "VALID"
            
        # Verify logger assignment
        validation = TemperatureService.verify_logger_assignment(shipment_id, logger_id, recorded_at_str)
        if not validation["is_valid_assignment"]:
            data["reading_status"] = "UNASSIGNED_LOGGER"
            data["calibration_uncertainty"] = 99.9 # Mark suspect
        
        res = supabase.table("temperature_readings").insert(data).execute()
        return res.data[0] if res.data else data

    @staticmethod
    def verify_logger_assignment(shipment_id: str, logger_id: str, timestamp_str: str) -> Dict[str, Any]:
        """
        Rule 3 & Negative Scenario 1:
        Checks whether logger is assigned to shipment at reading timestamp.
        """
        assignments = supabase.table("shipment_logger_assignments")\
            .select("*")\
            .eq("shipment_id", shipment_id)\
            .eq("logger_id", logger_id)\
            .execute().data
        
        if not assignments:
            return {
                "is_valid_assignment": False,
                "error_code": "UNASSIGNED_LOGGER",
                "message": f"Logger {logger_id} has no assignment record for shipment {shipment_id}."
            }
        
        rec_time = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        
        is_assigned_at_time = False
        for asg in assignments:
            asg_start = datetime.fromisoformat(asg["assigned_at"].replace("Z", "+00:00"))
            asg_end = None
            if asg.get("unassigned_at"):
                asg_end = datetime.fromisoformat(asg["unassigned_at"].replace("Z", "+00:00"))
            
            if asg_start <= rec_time and (asg_end is None or rec_time <= asg_end):
                is_assigned_at_time = True
                break
                
        if not is_assigned_at_time:
            return {
                "is_valid_assignment": False,
                "error_code": "UNASSIGNED_LOGGER",
                "message": f"Logger {logger_id} was not actively assigned to shipment {shipment_id} at timestamp {timestamp_str}."
            }
            
        return {
            "is_valid_assignment": True,
            "error_code": None,
            "message": "Valid logger assignment verified."
        }

    @staticmethod
    def detect_missing_gaps(shipment_id: str, expected_interval_minutes: int = 10) -> Dict[str, Any]:
        """
        Rule 7 & Negative Scenario 3: Missing Data Detection
        Calculates expected readings every 10 minutes between shipment departure and arrival.
        Identifies missing intervals and counts missing readings.
        """
        shipment_res = supabase.table("shipments").select("*").eq("shipment_id", shipment_id).execute()
        if not shipment_res.data:
            return {"error": "SHIPMENT_NOT_FOUND", "shipment_id": shipment_id}
        
        shipment = shipment_res.data[0]
        start_time_str = shipment.get("actual_departure") or shipment.get("planned_departure")
        end_time_str = shipment.get("actual_arrival") or shipment.get("expected_arrival")
        
        if not start_time_str or not end_time_str:
            return {"error": "INSUFFICIENT_TIMESTAMPS", "shipment_id": shipment_id}
            
        start_time = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
        end_time = datetime.fromisoformat(end_time_str.replace("Z", "+00:00"))
        
        # Query readings sorted by recorded_at
        readings = supabase.table("temperature_readings")\
            .select("*")\
            .eq("shipment_id", shipment_id)\
            .order("recorded_at", desc=False)\
            .execute().data
            
        # Calculate expected total intervals
        duration_minutes = (end_time - start_time).total_seconds() / 60.0
        expected_reading_count = max(1, int(round(duration_minutes / expected_interval_minutes)))
        
        if not readings:
            return {
                "shipment_id": shipment_id,
                "expected_reading_count": expected_reading_count,
                "actual_reading_count": 0,
                "missing_reading_count": expected_reading_count,
                "completeness_pct": 0.0,
                "has_gaps": True,
                "gaps": [{
                    "gap_start": start_time_str,
                    "gap_end": end_time_str,
                    "gap_duration_minutes": round(duration_minutes),
                    "missing_readings_in_gap": expected_reading_count,
                    "issue_code": "MISSING_DATA",
                    "severity": "CRITICAL"
                }]
            }
            
        # Detect gaps between consecutive readings
        gaps = []
        tolerance_multiplier = 1.8 # Anything greater than 18 minutes indicates a missing 10-minute ping
        gap_threshold_seconds = expected_interval_minutes * 60 * tolerance_multiplier
        
        missing_count = 0
        timestamps = [datetime.fromisoformat(r["recorded_at"].replace("Z", "+00:00")) for r in readings]
        
        # Check start gap
        first_dt = timestamps[0]
        if (first_dt - start_time).total_seconds() > gap_threshold_seconds:
            gap_dur = (first_dt - start_time).total_seconds() / 60.0
            missed = int(round(gap_dur / expected_interval_minutes)) - 1
            if missed > 0:
                missing_count += missed
                gaps.append({
                    "gap_start": start_time_str,
                    "gap_end": readings[0]["recorded_at"],
                    "gap_duration_minutes": round(gap_dur, 1),
                    "missing_readings_in_gap": missed,
                    "issue_code": "MISSING_DATA",
                    "severity": "HIGH" if missed > 3 else "MEDIUM"
                })
        
        for i in range(len(timestamps) - 1):
            curr_dt = timestamps[i]
            next_dt = timestamps[i + 1]
            diff_seconds = (next_dt - curr_dt).total_seconds()
            
            if diff_seconds > gap_threshold_seconds:
                gap_dur_min = diff_seconds / 60.0
                missed = int(round(gap_dur_min / expected_interval_minutes)) - 1
                if missed > 0:
                    missing_count += missed
                    gaps.append({
                        "gap_start": readings[i]["recorded_at"],
                        "gap_end": readings[i + 1]["recorded_at"],
                        "gap_duration_minutes": round(gap_dur_min, 1),
                        "missing_readings_in_gap": missed,
                        "issue_code": "MISSING_DATA",
                        "severity": "CRITICAL" if missed >= 6 else ("HIGH" if missed >= 3 else "MEDIUM")
                    })
        
        # Check end gap
        last_dt = timestamps[-1]
        if (end_time - last_dt).total_seconds() > gap_threshold_seconds:
            gap_dur = (end_time - last_dt).total_seconds() / 60.0
            missed = int(round(gap_dur / expected_interval_minutes)) - 1
            if missed > 0:
                missing_count += missed
                gaps.append({
                    "gap_start": readings[-1]["recorded_at"],
                    "gap_end": end_time_str,
                    "gap_duration_minutes": round(gap_dur, 1),
                    "missing_readings_in_gap": missed,
                    "issue_code": "MISSING_DATA",
                    "severity": "HIGH" if missed > 3 else "MEDIUM"
                })
                
        completeness = max(0.0, min(100.0, round(((expected_reading_count - missing_count) / max(1, expected_reading_count)) * 100, 2)))
        
        return {
            "shipment_id": shipment_id,
            "expected_reading_count": expected_reading_count,
            "actual_reading_count": len(readings),
            "missing_reading_count": missing_count,
            "completeness_pct": completeness,
            "has_gaps": len(gaps) > 0,
            "gaps": gaps
        }

    @staticmethod
    def get_shipment_trends(shipment_id: str) -> Dict[str, Any]:
        """Returns chronological readings with min, max, avg, and thresholds for charting."""
        readings_res = supabase.table("temperature_readings")\
            .select("*")\
            .eq("shipment_id", shipment_id)\
            .order("recorded_at", desc=False)\
            .execute()
            
        shipment_res = supabase.table("shipments").select("*").eq("shipment_id", shipment_id).execute()
        if not shipment_res.data:
            return {"readings": [], "stats": {}}
            
        shipment = shipment_res.data[0]
        prod_res = supabase.table("products").select("*").eq("product_id", shipment["product_id"]).execute()
        product = prod_res.data[0] if prod_res.data else {}
        
        readings = readings_res.data
        if not readings:
            return {
                "shipment": shipment,
                "product": product,
                "readings": [],
                "stats": {"count": 0}
            }
            
        temps = [float(r["corrected_temperature"]) for r in readings]
        stats = {
            "count": len(readings),
            "min_temp": round(min(temps), 2),
            "max_temp": round(max(temps), 2),
            "avg_temp": round(sum(temps) / len(temps), 2),
            "target_min": product.get("minimum_temperature"),
            "target_max": product.get("maximum_temperature")
        }
        
        return {
            "shipment": shipment,
            "product": product,
            "stats": stats,
            "readings": readings
        }
