# backend/app/services/shipment_service.py
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from app.config.supabase_client import supabase

class ShipmentService:
    @staticmethod
    def get_all(
        status: Optional[str] = None,
        compliance: Optional[str] = None,
        product_id: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 25
    ) -> Dict[str, Any]:
        query = supabase.table("shipments").select("*")
        if status:
            query = query.eq("shipment_status", status)
        if compliance:
            query = query.eq("compliance_status", compliance)
        if product_id:
            query = query.eq("product_id", product_id)
            
        offset = (page - 1) * page_size
        res = query.order("planned_departure", desc=True).offset(offset).limit(page_size).execute()
        
        count_q = supabase.table("shipments").select("shipment_id")
        if status:
            count_q = count_q.eq("shipment_status", status)
        if compliance:
            count_q = count_q.eq("compliance_status", compliance)
        count_res = count_q.execute()
        total = count_res.count or len(count_res.data)
        
        # Enrich items with product_name and carrier info if available
        items = res.data
        if items:
            prod_ids = list(set([item["product_id"] for item in items if item.get("product_id")]))
            prods = supabase.table("products").select("product_id,product_name,minimum_temperature,maximum_temperature").in_("product_id", prod_ids).execute().data
            prod_map = {p["product_id"]: p for p in prods}
            for it in items:
                p_info = prod_map.get(it["product_id"], {})
                it["product_name"] = p_info.get("product_name", it["product_id"])
                it["min_temp"] = p_info.get("minimum_temperature")
                it["max_temp"] = p_info.get("maximum_temperature")

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size
        }

    @staticmethod
    def get_by_id(shipment_id: str) -> Optional[Dict[str, Any]]:
        res = supabase.table("shipments").select("*").eq("shipment_id", shipment_id).execute()
        if not res.data:
            return None
        shipment = res.data[0]
        
        # Enrich with product details
        prod_res = supabase.table("products").select("*").eq("product_id", shipment["product_id"]).execute()
        shipment["product"] = prod_res.data[0] if prod_res.data else {}

        # Enrich with lot details
        lot_res = supabase.table("lots").select("*").eq("lot_id", shipment["lot_id"]).execute()
        shipment["lot"] = lot_res.data[0] if lot_res.data else {}

        # Enrich with packaging details
        pkg_res = supabase.table("packaging").select("*").eq("packaging_id", shipment["packaging_id"]).execute()
        shipment["packaging"] = pkg_res.data[0] if pkg_res.data else {}

        return shipment

    @staticmethod
    def create(data: Dict[str, Any]) -> Dict[str, Any]:
        if not data.get("created_at"):
            data["created_at"] = datetime.now(timezone.utc).isoformat()
        if not data.get("compliance_status"):
            data["compliance_status"] = "PENDING"
            
        res = supabase.table("shipments").insert(data).execute()
        return res.data[0] if res.data else data

    @staticmethod
    def update(shipment_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        res = supabase.table("shipments").update(data).eq("shipment_id", shipment_id).execute()
        return res.data[0] if res.data else None

    @staticmethod
    def get_shipment_details_bundle(shipment_id: str) -> Dict[str, Any]:
        """Provides complete aggregated data bundle for Shipment Details tabs."""
        shipment = ShipmentService.get_by_id(shipment_id)
        if not shipment:
            return {}

        readings = supabase.table("temperature_readings")\
            .select("*")\
            .eq("shipment_id", shipment_id)\
            .order("recorded_at", desc=False)\
            .limit(500)\
            .execute().data

        route_stops = supabase.table("route_stops")\
            .select("*")\
            .eq("shipment_id", shipment_id)\
            .order("stop_sequence", desc=False)\
            .execute().data

        custody_events = supabase.table("custody_events")\
            .select("*")\
            .eq("shipment_id", shipment_id)\
            .order("handoff_timestamp", desc=False)\
            .execute().data

        assignments = supabase.table("shipment_logger_assignments")\
            .select("*")\
            .eq("shipment_id", shipment_id)\
            .execute().data

        excursions = supabase.table("excursion_reports")\
            .select("*")\
            .eq("shipment_id", shipment_id)\
            .execute().data

        compliance_report = supabase.table("compliance_reports")\
            .select("*")\
            .eq("shipment_id", shipment_id)\
            .order("generated_at", desc=True)\
            .execute().data

        audit_history = supabase.table("audit_events")\
            .select("*")\
            .eq("entity_type", "shipment")\
            .eq("entity_id", shipment_id)\
            .order("created_at", desc=True)\
            .execute().data

        return {
            "overview": shipment,
            "readings": readings,
            "route_stops": route_stops,
            "custody_events": custody_events,
            "loggers": assignments,
            "excursions": excursions,
            "compliance_report": compliance_report[0] if compliance_report else None,
            "audit_history": audit_history
        }
