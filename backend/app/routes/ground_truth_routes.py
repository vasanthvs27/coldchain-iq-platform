# backend/app/routes/ground_truth_routes.py
from flask import Blueprint
from app.services.evaluation_service import EvaluationService
from app.utils.response import success_response, error_response

ground_truth_bp = Blueprint("evaluation", __name__)

@ground_truth_bp.route("/ground-truth", methods=["GET"])
def get_ground_truth():
    records = EvaluationService.get_ground_truth_records()
    return success_response(data=records, meta={"total": len(records)}, message="Ground truth dataset retrieved (isolated offline storage)")

@ground_truth_bp.route("/run", methods=["POST"])
def run_evaluation():
    try:
        metrics = EvaluationService.evaluate_detection_performance()
        return success_response(data=metrics, message="Operational detection ground-truth evaluation executed")
    except Exception as e:
        return error_response(str(e), error_code="EVALUATION_ERROR", status_code=500)

@ground_truth_bp.route("/metrics", methods=["GET"])
def get_metrics():
    metrics = EvaluationService.evaluate_detection_performance()
    return success_response(data=metrics["overall_metrics"], message="Evaluation metrics retrieved")

@ground_truth_bp.route("/confusion-matrix", methods=["GET"])
def get_confusion_matrix():
    metrics = EvaluationService.evaluate_detection_performance()
    return success_response(data=metrics["confusion_matrix"], message="Confusion matrix retrieved")

@ground_truth_bp.route("/anomaly-breakdown", methods=["GET"])
def get_anomaly_breakdown():
    metrics = EvaluationService.evaluate_detection_performance()
    return success_response(data=metrics["anomaly_breakdown"], message="Per-scenario evaluation breakdown retrieved")
