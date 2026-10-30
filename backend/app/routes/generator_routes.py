# backend/app/routes/generator_routes.py
from flask import Blueprint, request
from app.services.generator_service import DataGeneratorService
from app.config.supabase_client import supabase
from app.utils.response import success_response, error_response

generator_bp = Blueprint("generator", __name__)

@generator_bp.route("/configure", methods=["POST"])
def configure_generator():
    data = request.get_json() or {}
    mode = data.get("mode", "STARTER")
    shipment_count = data.get("shipment_count", 50 if mode == "STARTER" else 5000)
    logger_count = data.get("logger_count", 25 if mode == "STARTER" else 1000)
    seed = data.get("seed", 20261022)
    interval = data.get("reading_interval_minutes", 10)

    config_spec = {
        "mode": mode,
        "shipment_count": shipment_count,
        "logger_count": logger_count,
        "seed": seed,
        "reading_interval_minutes": interval,
        "negative_scenarios_included": [
            "UNASSIGNED_LOGGER",
            "POLICY_MISMATCH",
            "MISSING_DATA",
            "CUSTODY_GAP",
            "CROSS_SHIPMENT_DURATION"
        ]
    }
    return success_response(data=config_spec, message="Generator configuration validated")

@generator_bp.route("/run", methods=["POST"])
def run_generator():
    data = request.get_json() or {}
    mode = data.get("mode", "STARTER")
    shipment_count = data.get("shipment_count")
    logger_count = data.get("logger_count")
    seed = int(data.get("seed", 20261022))
    interval = int(data.get("reading_interval_minutes", 10))

    try:
        run_result = DataGeneratorService.run_generation(
            mode=mode,
            shipment_count=shipment_count,
            logger_count=logger_count,
            seed=seed,
            reading_interval_minutes=interval
        )
        return success_response(data=run_result, message=f"Synthetic dataset generation ({mode} mode) completed successfully")
    except Exception as e:
        return error_response(str(e), error_code="GENERATION_FAILED", status_code=500)

@generator_bp.route("/runs", methods=["GET"])
def get_runs():
    res = supabase.table("data_generation_runs").select("*").order("started_at", desc=True).limit(20).execute()
    return success_response(data=res.data, message="Generation run history retrieved")

@generator_bp.route("/runs/<run_id>", methods=["GET"])
def get_run(run_id):
    res = supabase.table("data_generation_runs").select("*").eq("run_id", run_id).execute()
    if not res.data:
        return error_response("Run not found", error_code="NOT_FOUND", status_code=404)
    return success_response(data=res.data[0], message="Generation run details retrieved")

@generator_bp.route("/runs/<run_id>/status", methods=["GET"])
def get_run_status(run_id):
    res = supabase.table("data_generation_runs").select("run_id,status,records_generated,started_at,completed_at").eq("run_id", run_id).execute()
    if not res.data:
        return error_response("Run not found", error_code="NOT_FOUND", status_code=404)
    return success_response(data=res.data[0], message="Run status retrieved")

@generator_bp.route("/runs/<run_id>/cancel", methods=["POST"])
def cancel_run(run_id):
    res = supabase.table("data_generation_runs").update({"status": "CANCELLED"}).eq("run_id", run_id).execute()
    return success_response(message="Generation run cancelled")
