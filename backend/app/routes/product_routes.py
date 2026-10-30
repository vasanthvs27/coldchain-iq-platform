# backend/app/routes/product_routes.py
from flask import Blueprint, request
from app.services.product_service import ProductService
from app.utils.response import success_response, error_response

product_bp = Blueprint("products", __name__)

@product_bp.route("", methods=["GET"])
def get_products():
    category = request.args.get("category")
    status = request.args.get("status")
    items = ProductService.get_all(category=category, status=status)
    return success_response(data=items, meta={"total": len(items)}, message="Products retrieved successfully")

@product_bp.route("", methods=["POST"])
def create_product():
    data = request.get_json() or {}
    try:
        created = ProductService.create(data)
        return success_response(data=created, message="Product created successfully", status_code=201)
    except ValueError as e:
        return error_response(str(e), error_code="INVALID_TEMPERATURE_RANGE", status_code=422)
    except Exception as e:
        return error_response(str(e), error_code="CREATION_ERROR", status_code=400)

@product_bp.route("/<product_id>", methods=["GET"])
def get_product(product_id):
    product = ProductService.get_by_id(product_id)
    if not product:
        return error_response("Product not found", error_code="PRODUCT_NOT_FOUND", status_code=404)
    return success_response(data=product, message="Product retrieved successfully")

@product_bp.route("/<product_id>", methods=["PUT"])
def update_product(product_id):
    data = request.get_json() or {}
    try:
        updated = ProductService.update(product_id, data)
        if not updated:
            return error_response("Product not found", error_code="PRODUCT_NOT_FOUND", status_code=404)
        return success_response(data=updated, message="Product updated successfully")
    except ValueError as e:
        return error_response(str(e), error_code="INVALID_TEMPERATURE_RANGE", status_code=422)

@product_bp.route("/<product_id>", methods=["DELETE"])
def delete_product(product_id):
    deleted = ProductService.delete(product_id)
    if not deleted:
        return error_response("Product not found", error_code="PRODUCT_NOT_FOUND", status_code=404)
    return success_response(message="Product deleted successfully")

@product_bp.route("/<product_id>/lots", methods=["GET"])
def get_product_lots(product_id):
    lots = ProductService.get_lots(product_id)
    return success_response(data=lots, message="Product lots retrieved successfully")

@product_bp.route("/<product_id>/policies", methods=["GET"])
def get_product_policies(product_id):
    policies = ProductService.get_policies(product_id)
    return success_response(data=policies, message="Product policies retrieved successfully")
