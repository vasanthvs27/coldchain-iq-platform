# backend/app/services/analytics_service.py
from datetime import datetime, timezone
from typing import Dict, Any, List
from app.config.supabase_client import supabase

class AnalyticsService:
    @staticmethod
    def get_dashboard_overview() -> Dict[str, Any]:
        """Calculates executive dashboard KPI metrics from operational database records."""
        shipments = supabase.table("shipments").select("*").execute().data
        reports = supabase.table("compliance_reports").select("*").execute().data
        excursions = supabase.table("excursion_reports").select("*").execute().data
        loggers = supabase.table("loggers").select("*").execute().data

        total_shipments = len(shipments)
        active_shipments = sum(1 for s in shipments if s.get("shipment_status") in ("IN_TRANSIT", "SCHEDULED"))
        delivered_shipments = sum(1 for s in shipments if s.get("shipment_status") == "DELIVERED")

        compliant_count = sum(1 for s in shipments if s.get("compliance_status") == "COMPLIANT")
        non_compliant_count = sum(1 for s in shipments if s.get("compliance_status") == "NON_COMPLIANT")
        inconclusive_count = sum(1 for s in shipments if s.get("compliance_status") == "INCONCLUSIVE")
        under_review_count = sum(1 for s in shipments if s.get("compliance_status") in ("UNDER_REVIEW", "PENDING"))

        total_excursions = len(excursions)
        critical_excursions = sum(1 for e in excursions if e.get("severity") in ("CRITICAL", "HIGH"))

        now_iso = datetime.now(timezone.utc).isoformat()
        cal_issues = sum(1 for l in loggers if l.get("calibration_expiry") and l.get("calibration_expiry") < now_iso)

        total_readings = sum(r.get("total_readings", 0) for r in reports)
        total_missing = sum(r.get("missing_readings", 0) for r in reports)

        return {
            "total_shipments": total_shipments,
            "active_shipments": active_shipments,
            "delivered_shipments": delivered_shipments,
            "compliant_shipments": compliant_count,
            "non_compliant_shipments": non_compliant_count,
            "inconclusive_shipments": inconclusive_count,
            "under_review_shipments": under_review_count,
            "compliance_rate": round((compliant_count / max(1, total_shipments)) * 100, 1),
            "temperature_excursions": total_excursions,
            "critical_excursions": critical_excursions,
            "logger_calibration_issues": cal_issues,
            "missing_telemetry_readings": total_missing,
            "total_telemetry_readings": total_readings
        }

    @staticmethod
    def get_compliance_distribution() -> List[Dict[str, Any]]:
        shipments = supabase.table("shipments").select("compliance_status").execute().data
        dist = {"COMPLIANT": 0, "NON_COMPLIANT": 0, "INCONCLUSIVE": 0, "UNDER_REVIEW": 0}
        for s in shipments:
            st = s.get("compliance_status", "UNDER_REVIEW")
            if st in dist:
                dist[st] += 1
            else:
                dist["UNDER_REVIEW"] += 1
        return [{"status": k, "count": v} for k, v in dist.items()]

    @staticmethod
    def get_excursions_by_product() -> List[Dict[str, Any]]:
        excursions = supabase.table("excursion_reports").select("product_id").execute().data
        counts = {}
        for e in excursions:
            pid = e.get("product_id", "UNKNOWN")
            counts[pid] = counts.get(pid, 0) + 1
        
        products = supabase.table("products").select("product_id,product_name").execute().data
        prod_map = {p["product_id"]: p["product_name"] for p in products}

        return [{"product_id": k, "product_name": prod_map.get(k, k), "excursion_count": v} for k, v in counts.items()]

    @staticmethod
    def get_carrier_risk_metrics() -> List[Dict[str, Any]]:
        shipments = supabase.table("shipments").select("carrier_name,compliance_status").execute().data
        carrier_stats = {}
        for s in shipments:
            carrier = s.get("carrier_name", "Unknown Carrier")
            stats = carrier_stats.setdefault(carrier, {"total": 0, "compliant": 0, "excursions": 0})
            stats["total"] += 1
            if s.get("compliance_status") == "COMPLIANT":
                stats["compliant"] += 1
            elif s.get("compliance_status") == "NON_COMPLIANT":
                stats["excursions"] += 1

        results = []
        for c, st in carrier_stats.items():
            comp_rate = round((st["compliant"] / max(1, st["total"])) * 100, 1)
            results.append({
                "carrier_name": c,
                "total_shipments": st["total"],
                "compliant_shipments": st["compliant"],
                "violations": st["excursions"],
                "compliance_score": comp_rate,
                "risk_rating": "LOW" if comp_rate >= 85 else ("MEDIUM" if comp_rate >= 70 else "HIGH")
            })
        return results

    @staticmethod
    def get_route_dwell_metrics() -> List[Dict[str, Any]]:
        stops = supabase.table("route_stops").select("stop_type,stop_name,dwell_duration").execute().data
        dwell_by_type = {}
        for st in stops:
            stype = st.get("stop_type", "OTHER")
            dwell = st.get("dwell_duration", 0)
            data = dwell_by_type.setdefault(stype, {"count": 0, "total_dwell": 0, "max_dwell": 0})
            data["count"] += 1
            data["total_dwell"] += dwell
            data["max_dwell"] = max(data["max_dwell"], dwell)

        return [
            {
                "stop_type": k,
                "total_stops": v["count"],
                "average_dwell_minutes": round(v["total_dwell"] / max(1, v["count"]), 1),
                "max_dwell_minutes": v["max_dwell"]
            }
            for k, v in dwell_by_type.items()
        ]
