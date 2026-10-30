# backend/app/services/product_service.py
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from app.config.supabase_client import supabase

class ProductService:
    @staticmethod
    def get_all(category: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        query = supabase.table("products").select("*")
        if category:
            query = query.eq("product_category", category)
        if status:
            query = query.eq("status", status)
        res = query.order("product_id").execute()
        return res.data

    @staticmethod
    def get_by_id(product_id: str) -> Optional[Dict[str, Any]]:
        res = supabase.table("products").select("*").eq("product_id", product_id).execute()
        return res.data[0] if res.data else None

    @staticmethod
    def create(data: Dict[str, Any]) -> Dict[str, Any]:
        # Rule 1: Product Temperature Requirements: min must be strictly less than max
        min_temp = float(data.get("minimum_temperature", 0))
        max_temp = float(data.get("maximum_temperature", 0))
        if min_temp >= max_temp:
            raise ValueError(f"Invalid temperature range: minimum temperature ({min_temp}°C) must be less than maximum temperature ({max_temp}°C)")
        
        if not data.get("created_at"):
            data["created_at"] = datetime.now(timezone.utc).isoformat()
        if not data.get("updated_at"):
            data["updated_at"] = datetime.now(timezone.utc).isoformat()
        if not data.get("status"):
            data["status"] = "ACTIVE"
            
        res = supabase.table("products").insert(data).execute()
        
        # Also auto-create a default active threshold policy for the product
        policy_id = f"POL-{data['product_id']}-01"
        policy_record = {
            "policy_id": policy_id,
            "product_id": data["product_id"],
            "minimum_temperature": min_temp,
            "maximum_temperature": max_temp,
            "allowed_excursion_duration": data.get("allowed_excursion_duration", 60),
            "effective_from": data.get("effective_from", datetime.now(timezone.utc).isoformat()),
            "effective_until": None,
            "policy_version": "v1.0",
            "policy_status": "ACTIVE"
        }
        supabase.table("threshold_policies").insert(policy_record, upsert=True).execute()
        
        return res.data[0] if res.data else data

    @staticmethod
    def update(product_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if "minimum_temperature" in data and "maximum_temperature" in data:
            if float(data["minimum_temperature"]) >= float(data["maximum_temperature"]):
                raise ValueError("Minimum temperature must be less than maximum temperature")
        data["updated_at"] = datetime.now(timezone.utc).isoformat()
        res = supabase.table("products").update(data).eq("product_id", product_id).execute()
        return res.data[0] if res.data else None

    @staticmethod
    def delete(product_id: str) -> bool:
        res = supabase.table("products").delete().eq("product_id", product_id).execute()
        return bool(res.data)

    @staticmethod
    def get_lots(product_id: str) -> List[Dict[str, Any]]:
        res = supabase.table("lots").select("*").eq("product_id", product_id).order("manufacturing_date", desc=True).execute()
        return res.data

    @staticmethod
    def get_policies(product_id: str) -> List[Dict[str, Any]]:
        res = supabase.table("threshold_policies").select("*").eq("product_id", product_id).order("policy_version", desc=True).execute()
        return res.data
