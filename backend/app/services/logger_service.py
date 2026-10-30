# backend/app/services/logger_service.py
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from app.config.supabase_client import supabase

class LoggerService:
    @staticmethod
    def get_all(status: Optional[str] = None, page: int = 1, page_size: int = 50) -> Dict[str, Any]:
        query = supabase.table("loggers").select("*")
        if status:
            query = query.eq("logger_status", status)
        
        offset = (page - 1) * page_size
        response = query.order("logger_id").offset(offset).limit(page_size).execute()
        
        # total count
        count_res = supabase.table("loggers").select("logger_id").execute()
        total = count_res.count or len(count_res.data)
        
        return {
            "items": response.data,
            "total": total,
            "page": page,
            "page_size": page_size
        }

    @staticmethod
    def get_by_id(logger_id: str) -> Optional[Dict[str, Any]]:
        res = supabase.table("loggers").select("*").eq("logger_id", logger_id).execute()
        return res.data[0] if res.data else None

    @staticmethod
    def create(data: Dict[str, Any]) -> Dict[str, Any]:
        # Validate calibration
        cal_date = data.get("calibration_date")
        cal_expiry = data.get("calibration_expiry")
        if cal_date and cal_expiry and cal_date >= cal_expiry:
            raise ValueError("Calibration date must be earlier than calibration expiry date")
        
        res = supabase.table("loggers").insert(data).execute()
        return res.data[0] if res.data else data

    @staticmethod
    def update(logger_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        res = supabase.table("loggers").update(data).eq("logger_id", logger_id).execute()
        return res.data[0] if res.data else None

    @staticmethod
    def assign_to_shipment(logger_id: str, shipment_id: str, assigned_at: Optional[str] = None) -> Dict[str, Any]:
        assigned_time = assigned_at or datetime.now(timezone.utc).isoformat()
        assignment_id = f"ASG-{logger_id}-{shipment_id}"
        
        record = {
            "assignment_id": assignment_id,
            "shipment_id": shipment_id,
            "logger_id": logger_id,
            "assigned_at": assigned_time,
            "unassigned_at": None,
            "status": "ACTIVE",
            "assignment_notes": f"Assigned to shipment {shipment_id}"
        }
        
        supabase.table("shipment_logger_assignments").insert(record, upsert=True).execute()
        supabase.table("loggers").update({"logger_status": "IN_USE"}).eq("logger_id", logger_id).execute()
        return record

    @staticmethod
    def get_assignments(logger_id: str) -> List[Dict[str, Any]]:
        res = supabase.table("shipment_logger_assignments").select("*").eq("logger_id", logger_id).order("assigned_at", desc=True).execute()
        return res.data

    @staticmethod
    def validate_calibration(logger_id: str, check_timestamp: Optional[datetime] = None) -> Dict[str, Any]:
        logger = LoggerService.get_by_id(logger_id)
        if not logger:
            return {"valid": False, "reason": "LOGGER_NOT_FOUND", "status": "UNKNOWN"}
        
        now = check_timestamp or datetime.now(timezone.utc)
        cal_expiry_str = logger.get("calibration_expiry")
        if not cal_expiry_str:
            return {"valid": False, "reason": "MISSING_CALIBRATION_EXPIRY", "status": "SUSPECT"}
        
        cal_expiry = datetime.fromisoformat(cal_expiry_str.replace("Z", "+00:00"))
        if now > cal_expiry:
            return {
                "valid": False,
                "reason": "CALIBRATION_EXPIRED",
                "status": "EXPIRED",
                "calibration_expiry": cal_expiry_str,
                "uncertainty": logger.get("measurement_uncertainty", 0.2)
            }
        
        return {
            "valid": True,
            "status": "VALID",
            "calibration_date": logger.get("calibration_date"),
            "calibration_expiry": cal_expiry_str,
            "accuracy_tolerance": logger.get("accuracy_tolerance", 0.5),
            "measurement_uncertainty": logger.get("measurement_uncertainty", 0.2)
        }
