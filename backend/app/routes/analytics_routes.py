# backend/app/routes/analytics_routes.py
from flask import Blueprint
from app.services.analytics_service import AnalyticsService
from app.utils.response import success_response

analytics_bp = Blueprint("analytics", __name__)

@analytics_bp.route("/overview", methods=["GET"])
def get_overview():
    return success_response(data=AnalyticsService.get_dashboard_overview(), message="Analytics overview retrieved")

@analytics_bp.route("/temperature", methods=["GET"])
def get_temperature_analytics():
    return success_response(data=AnalyticsService.get_excursions_by_product(), message="Temperature excursion analytics retrieved")

@analytics_bp.route("/excursions", methods=["GET"])
def get_excursion_analytics():
    return success_response(data=AnalyticsService.get_excursions_by_product(), message="Excursion breakdown retrieved")

@analytics_bp.route("/compliance", methods=["GET"])
def get_compliance_analytics():
    return success_response(data=AnalyticsService.get_compliance_distribution(), message="Compliance distribution analytics retrieved")

@analytics_bp.route("/carriers", methods=["GET"])
def get_carrier_analytics():
    return success_response(data=AnalyticsService.get_carrier_risk_metrics(), message="Carrier reliability analytics retrieved")

@analytics_bp.route("/routes", methods=["GET"])
def get_route_analytics():
    return success_response(data=AnalyticsService.get_route_dwell_metrics(), message="Route dwell analytics retrieved")

@analytics_bp.route("/risk", methods=["GET"])
def get_risk_analytics():
    carriers = AnalyticsService.get_carrier_risk_metrics()
    high_risk_carriers = [c for c in carriers if c.get("risk_rating") == "HIGH"]
    return success_response(data={
        "high_risk_carrier_count": len(high_risk_carriers),
        "carrier_profiles": carriers
    }, message="Risk assessment metrics retrieved")
