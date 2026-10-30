# backend/app/services/custody_service.py
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from app.config.supabase_client import supabase

class CustodyService:
    @staticmethod
    def get_all(page: int = 1, page_size: int = 50) -> Dict[str, Any]:
        offset = (page - 1) * page_size
        res = supabase.table("custody_events").select("*").order("handoff_timestamp", desc=True).offset(offset).limit(page_size).execute()
        count_res = supabase.table("custody_events").select("custody_event_id").execute()
        total = count_res.count or len(count_res.data)
        return {
            "items": res.data,
            "total": total,
            "page": page,
            "page_size": page_size
        }

    @staticmethod
    def get_by_id(event_id: str) -> Optional[Dict[str, Any]]:
        res = supabase.table("custody_events").select("*").eq("custody_event_id", event_id).execute()
        return res.data[0] if res.data else None

    @staticmethod
    def create(data: Dict[str, Any]) -> Dict[str, Any]:
        if not data.get("created_at"):
            data["created_at"] = datetime.now(timezone.utc).isoformat()
        res = supabase.table("custody_events").insert(data).execute()
        return res.data[0] if res.data else data

    @staticmethod
    def get_shipment_timeline(shipment_id: str) -> List[Dict[str, Any]]:
        res = supabase.table("custody_events").select("*").eq("shipment_id", shipment_id).order("handoff_timestamp", desc=False).execute()
        return res.data

    @staticmethod
    def detect_custody_gaps(shipment_id: str) -> Dict[str, Any]:
        """
        Rule 8 & Negative Scenario 4: Custody Gap Detection
        Verifies:
        - Chronological order of handoffs
        - Custodian continuity: Event[i].new_custodian == Event[i+1].previous_custodian
        - Event verification statuses
        """
        events = CustodyService.get_shipment_timeline(shipment_id)
        if not events:
            return {
                "shipment_id": shipment_id,
                "has_gaps": True,
                "gap_count": 1,
                "completeness_score": 0.0,
                "gaps": [{
                    "gap_type": "NO_CUSTODY_RECORDS",
                    "description": "No custody transfer records found for shipment",
                    "severity": "CRITICAL"
                }]
            }

        gaps = []
        # Sort chronologically by handoff_timestamp
        sorted_events = sorted(events, key=lambda x: str(x.get("handoff_timestamp", "")))

        for i in range(len(sorted_events) - 1):
            curr_event = sorted_events[i]
            next_event = sorted_events[i + 1]

            curr_recipient = curr_event.get("new_custodian", "").strip()
            next_giver = next_event.get("previous_custodian", "").strip()

            if curr_recipient and next_giver and curr_recipient.lower() != next_giver.lower():
                # Discontinuity detected: Custody gap!
                gaps.append({
                    "gap_type": "CUSTODY_GAP",
                    "issue_code": "CUSTODY_GAP",
                    "previous_event_id": curr_event.get("custody_event_id"),
                    "next_event_id": next_event.get("custody_event_id"),
                    "expected_custodian": curr_recipient,
                    "actual_next_giver": next_giver,
                    "previous_timestamp": curr_event.get("handoff_timestamp"),
                    "next_timestamp": next_event.get("handoff_timestamp"),
                    "location_gap": f"Between {curr_event.get('location')} and {next_event.get('location')}",
                    "description": f"Custody handoff broken: {curr_recipient} was expected to transfer custody, but record shows {next_giver} handing off."
                })

            if next_event.get("verification_status") == "EXCEPTION":
                gaps.append({
                    "gap_type": "UNVERIFIED_HANDOFF",
                    "issue_code": "CUSTODY_EXCEPTION",
                    "event_id": next_event.get("custody_event_id"),
                    "description": f"Custody transfer verification flagged as EXCEPTION: {next_event.get('notes')}"
                })

        total_transitions = max(1, len(sorted_events) - 1)
        valid_transitions = total_transitions - len(gaps)
        completeness = max(0.0, min(100.0, round((valid_transitions / total_transitions) * 100, 2)))

        return {
            "shipment_id": shipment_id,
            "total_events": len(events),
            "has_gaps": len(gaps) > 0,
            "gap_count": len(gaps),
            "completeness_score": completeness,
            "gaps": gaps
        }
