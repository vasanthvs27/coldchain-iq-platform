# backend/app/routes/policy_routes.py
from flask import Blueprint, request
from app.config.supabase_client import supabase
from app.utils.response import success_response, error_response

policy_bp = Blueprint("policies", __name__)

@policy_bp.route("", methods=["GET"])
def get_policies():
    product_id = request.args.get("product_id")
    status = request.args.get("status")
    query = supabase.table("threshold_policies").select("*")
    if product_id:
        query = query.eq("product_id", product_id)
    if status:
        query = query.eq("policy_status", status)
        
    policies = query.order("created_at", desc=True).execute().data
    return success_response(data=policies, meta={"total": len(policies)}, message="Threshold policies retrieved")

@policy_bp.route("", methods=["POST"])
def create_policy():
    data = request.get_json() or {}
    min_temp = float(data.get("minimum_temperature", 0))
    max_temp = float(data.get("maximum_temperature", 0))
    if min_temp >= max_temp:
        return error_response("Minimum temperature must be less than maximum temperature", error_code="INVALID_TEMP_RANGE", status_code=422)

    res = supabase.table("threshold_policies").insert(data).execute()
    return success_response(data=res.data[0] if res.data else data, message="Threshold policy created", status_code=201)

@policy_bp.route("/<policy_id>", methods=["GET"])
def get_policy(policy_id):
    res = supabase.table("threshold_policies").select("*").eq("policy_id", policy_id).execute()
    if not res.data:
        return error_response("Policy not found", error_code="NOT_FOUND", status_code=404)
    return success_response(data=res.data[0], message="Policy retrieved")

@policy_bp.route("/<policy_id>", methods=["PUT"])
def update_policy(policy_id):
    data = request.get_json() or {}
    res = supabase.table("threshold_policies").update(data).eq("policy_id", policy_id).execute()
    if not res.data:
        return error_response("Policy not found", error_code="NOT_FOUND", status_code=404)
    return success_response(data=res.data[0], message="Policy updated")

@policy_bp.route("/products/<product_id>", methods=["GET"])
def get_product_active_policy(product_id):
    res = supabase.table("threshold_policies").select("*").eq("product_id", product_id).eq("policy_status", "ACTIVE").execute()
    return success_response(data=res.data, message="Active policies for product retrieved")
