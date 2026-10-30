# backend/app/routes/packaging_routes.py
from flask import Blueprint, request
from app.config.supabase_client import supabase
from app.utils.response import success_response, error_response

packaging_bp = Blueprint("packaging", __name__)

@packaging_bp.route("", methods=["GET"])
def get_packaging():
    packagings = supabase.table("packaging").select("*").order("packaging_id").execute().data
    return success_response(data=packagings, meta={"total": len(packagings)}, message="Packaging list retrieved")

@packaging_bp.route("", methods=["POST"])
def create_packaging():
    data = request.get_json() or {}
    min_temp = float(data.get("minimum_temperature", 0))
    max_temp = float(data.get("maximum_temperature", 0))
    if min_temp >= max_temp:
        return error_response("Minimum temperature must be less than maximum temperature", error_code="INVALID_TEMP_RANGE", status_code=422)

    res = supabase.table("packaging").insert(data).execute()
    return success_response(data=res.data[0] if res.data else data, message="Packaging unit created", status_code=201)

@packaging_bp.route("/<packaging_id>", methods=["GET"])
def get_packaging_unit(packaging_id):
    res = supabase.table("packaging").select("*").eq("packaging_id", packaging_id).execute()
    if not res.data:
        return error_response("Packaging unit not found", error_code="NOT_FOUND", status_code=404)
    return success_response(data=res.data[0], message="Packaging retrieved")

@packaging_bp.route("/<packaging_id>", methods=["PUT"])
def update_packaging_unit(packaging_id):
    data = request.get_json() or {}
    res = supabase.table("packaging").update(data).eq("packaging_id", packaging_id).execute()
    if not res.data:
        return error_response("Packaging unit not found", error_code="NOT_FOUND", status_code=404)
    return success_response(data=res.data[0], message="Packaging updated")

@packaging_bp.route("/<packaging_id>/compatibility", methods=["GET"])
def get_packaging_compatibility(packaging_id):
    res = supabase.table("packaging_product_compatibilities").select("*").eq("packaging_id", packaging_id).execute()
    return success_response(data=res.data, message="Packaging product compatibility list retrieved")
