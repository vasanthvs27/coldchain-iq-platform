# backend/app/routes/health_routes.py
from flask import Blueprint
from datetime import datetime, timezone
from app.utils.response import success_response

health_bp = Blueprint("health", __name__)

@health_bp.route("/health", methods=["GET"])
def health_check():
    return success_response(
        data={
            "service": "ColdChain IQ Intelligence Platform API",
            "version": "1.0.0",
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "database": "Supabase PostgreSQL",
            "features": {
                "rule_engine": "active",
                "synthetic_generator": "active",
                "validation_engine": "active",
                "ground_truth_evaluator": "active"
            }
        },
        message="ColdChain IQ backend service is running and healthy"
    )
