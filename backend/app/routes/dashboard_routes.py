# backend/app/routes/dashboard_routes.py
from flask import Blueprint
from app.services.analytics_service import AnalyticsService
from app.utils.response import success_response

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/overview", methods=["GET"])
def get_overview():
    data = AnalyticsService.get_dashboard_overview()
    return success_response(data=data, message="Dashboard overview retrieved")

@dashboard_bp.route("/compliance-summary", methods=["GET"])
def get_compliance_summary():
    data = AnalyticsService.get_compliance_distribution()
    return success_response(data=data, message="Compliance summary retrieved")

@dashboard_bp.route("/excursion-summary", methods=["GET"])
def get_excursion_summary():
    data = AnalyticsService.get_excursions_by_product()
    return success_response(data=data, message="Excursion summary retrieved")

@dashboard_bp.route("/shipment-trends", methods=["GET"])
def get_shipment_trends():
    data = AnalyticsService.get_carrier_risk_metrics()
    return success_response(data=data, message="Shipment trends retrieved")

@dashboard_bp.route("/temperature-trends", methods=["GET"])
def get_temperature_trends():
    data = AnalyticsService.get_route_dwell_metrics()
    return success_response(data=data, message="Route & temperature dwell trends retrieved")
