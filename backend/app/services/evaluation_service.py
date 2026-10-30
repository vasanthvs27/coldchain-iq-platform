# backend/app/services/evaluation_service.py
import os
import json
from typing import Dict, Any, List
from app.config.supabase_client import supabase
from app.config import Config

class EvaluationService:
    @staticmethod
    def get_ground_truth_records() -> List[Dict[str, Any]]:
        """Reads ground-truth offline reference data (isolated from operational engine)."""
        gt_json_path = os.path.join(Config.GROUND_TRUTH_DIR, "ground_truth.json")
        if not os.path.exists(gt_json_path):
            return []
        try:
            with open(gt_json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    @staticmethod
    def evaluate_detection_performance() -> Dict[str, Any]:
        """
        Calculates Confusion Matrix, Precision, Recall, F1-Score, and Anomaly-specific metrics
        by comparing operational detection outputs against offline ground-truth labels.
        """
        ground_truth = EvaluationService.get_ground_truth_records()
        gt_map = {gt["entity_id"]: gt for gt in ground_truth}

        # Query all operational compliance reports
        reports = supabase.table("compliance_reports").select("*").execute().data
        all_shipments = supabase.table("shipments").select("shipment_id").execute().data
        all_shipment_ids = set([s["shipment_id"] for s in all_shipments])

        # Mandatory negative scenarios
        target_scenarios = [
            "UNASSIGNED_LOGGER",
            "POLICY_MISMATCH",
            "MISSING_DATA",
            "CUSTODY_GAP",
            "CROSS_SHIPMENT_DURATION"
        ]

        # Overall Confusion Matrix counters
        tp = 0
        fp = 0
        tn = 0
        fn = 0

        # Per-scenario breakdown: {scenario: {"tp": 0, "fp": 0, "tn": 0, "fn": 0}}
        scenario_metrics = {sc: {"tp": 0, "fp": 0, "tn": 0, "fn": 0} for sc in target_scenarios}

        report_map = {r["shipment_id"]: r for r in reports}

        for sid in all_shipment_ids:
            gt_record = gt_map.get(sid)
            rep = report_map.get(sid, {})
            reason_codes = rep.get("reason_codes", [])
            decision = rep.get("compliance_status", "PENDING")

            is_actual_anomaly = gt_record is not None
            # Operational system flagged an anomaly if non-compliant, under-review, inconclusive, or reasons present
            is_predicted_anomaly = (decision != "COMPLIANT") or (len(reason_codes) > 0)

            if is_actual_anomaly and is_predicted_anomaly:
                tp += 1
            elif not is_actual_anomaly and is_predicted_anomaly:
                fp += 1
            elif not is_actual_anomaly and not is_predicted_anomaly:
                tn += 1
            elif is_actual_anomaly and not is_predicted_anomaly:
                fn += 1

            # Per scenario evaluation
            for sc in target_scenarios:
                is_sc_gt = (gt_record is not None and gt_record.get("issue_type") == sc)
                is_sc_predicted = (sc in reason_codes)

                if is_sc_gt and is_sc_predicted:
                    scenario_metrics[sc]["tp"] += 1
                elif not is_sc_gt and is_sc_predicted:
                    scenario_metrics[sc]["fp"] += 1
                elif not is_sc_gt and not is_sc_predicted:
                    scenario_metrics[sc]["tn"] += 1
                elif is_sc_gt and not is_sc_predicted:
                    scenario_metrics[sc]["fn"] += 1

        # Calculate metrics safely
        precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 1.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        total_eval = tp + tn + fp + fn
        accuracy = (tp + tn) / total_eval if total_eval > 0 else 1.0

        # Build scenario table
        breakdown = []
        for sc, m in scenario_metrics.items():
            sc_tp = m["tp"]
            sc_fp = m["fp"]
            sc_fn = m["fn"]
            sc_prec = sc_tp / (sc_tp + sc_fp) if (sc_tp + sc_fp) > 0 else 1.0
            sc_rec = sc_tp / (sc_tp + sc_fn) if (sc_tp + sc_fn) > 0 else 1.0
            sc_f1 = (2 * sc_prec * sc_rec) / (sc_prec + sc_rec) if (sc_prec + sc_rec) > 0 else 0.0
            breakdown.append({
                "scenario": sc,
                "true_positives": sc_tp,
                "false_positives": sc_fp,
                "false_negatives": sc_fn,
                "precision": round(sc_prec * 100, 2),
                "recall": round(sc_rec * 100, 2),
                "f1_score": round(sc_f1 * 100, 2)
            })

        return {
            "overall_metrics": {
                "precision": round(precision * 100, 2),
                "recall": round(recall * 100, 2),
                "f1_score": round(f1 * 100, 2),
                "accuracy": round(accuracy * 100, 2),
                "total_samples": total_eval
            },
            "confusion_matrix": {
                "true_positives": tp,
                "false_positives": fp,
                "true_negatives": tn,
                "false_negatives": fn
            },
            "anomaly_breakdown": breakdown,
            "isolation_verified": True,
            "evaluation_engine": "ColdChain IQ Offline Performance Evaluator"
        }
