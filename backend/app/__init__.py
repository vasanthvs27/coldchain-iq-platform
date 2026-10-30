# backend/app/__init__.py
from flask import Flask, jsonify
from app.config import Config
from app.extensions import jwt, cors
from app.utils.response import error_response

# Import all route blueprints
from app.routes.health_routes import health_bp
from app.routes.auth_routes import auth_bp
from app.routes.dashboard_routes import dashboard_bp
from app.routes.product_routes import product_bp
from app.routes.lot_routes import lot_bp
from app.routes.shipment_routes import shipment_bp
from app.routes.packaging_routes import packaging_bp
from app.routes.logger_routes import logger_bp
from app.routes.temperature_routes import temp_bp
from app.routes.route_routes import route_bp
from app.routes.custody_routes import custody_bp
from app.routes.policy_routes import policy_bp
from app.routes.excursion_routes import excursion_bp
from app.routes.compliance_routes import compliance_bp
from app.routes.analytics_routes import analytics_bp
from app.routes.generator_routes import generator_bp
from app.routes.validation_routes import validation_bp
from app.routes.ground_truth_routes import ground_truth_bp
from app.routes.reproducibility_routes import reproducibility_bp
from app.routes.audit_routes import audit_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    jwt.init_app(app)

    # Register Blueprints under /api/v1
    api_prefix = "/api/v1"
    app.register_blueprint(health_bp, url_prefix=api_prefix)
    app.register_blueprint(auth_bp, url_prefix=f"{api_prefix}/auth")
    app.register_blueprint(dashboard_bp, url_prefix=f"{api_prefix}/dashboard")
    app.register_blueprint(product_bp, url_prefix=f"{api_prefix}/products")
    app.register_blueprint(lot_bp, url_prefix=f"{api_prefix}/lots")
    app.register_blueprint(shipment_bp, url_prefix=f"{api_prefix}/shipments")
    app.register_blueprint(packaging_bp, url_prefix=f"{api_prefix}/packaging")
    app.register_blueprint(logger_bp, url_prefix=f"{api_prefix}/loggers")
    app.register_blueprint(temp_bp, url_prefix=f"{api_prefix}/temperature")
    app.register_blueprint(route_bp, url_prefix=f"{api_prefix}/routes")
    app.register_blueprint(custody_bp, url_prefix=f"{api_prefix}/custody")
    app.register_blueprint(policy_bp, url_prefix=f"{api_prefix}/policies")
    app.register_blueprint(excursion_bp, url_prefix=f"{api_prefix}/excursions")
    app.register_blueprint(compliance_bp, url_prefix=f"{api_prefix}/compliance")
    app.register_blueprint(analytics_bp, url_prefix=f"{api_prefix}/analytics")
    app.register_blueprint(generator_bp, url_prefix=f"{api_prefix}/generator")
    app.register_blueprint(validation_bp, url_prefix=f"{api_prefix}/validation")
    app.register_blueprint(ground_truth_bp, url_prefix=f"{api_prefix}/evaluation")
    app.register_blueprint(reproducibility_bp, url_prefix=f"{api_prefix}/reproducibility")
    app.register_blueprint(audit_bp, url_prefix=f"{api_prefix}/audit")

    # OpenAPI / Swagger Specification Endpoint
    @app.route(f"{api_prefix}/docs", methods=["GET"])
    def get_openapi_spec():
        spec = {
            "openapi": "3.0.3",
            "info": {
                "title": "ColdChain IQ Intelligence Platform API",
                "version": "1.0.0",
                "description": "Enterprise Cold Chain Temperature Compliance & Shipment Telemetry Intelligence REST API"
            },
            "servers": [{"url": "/api/v1"}],
            "paths": {
                "/health": {"get": {"summary": "Service health check", "responses": {"200": {"description": "Healthy"}}}},
                "/auth/login": {"post": {"summary": "User authentication", "responses": {"200": {"description": "JWT tokens"}}}},
                "/dashboard/overview": {"get": {"summary": "Executive KPI overview", "responses": {"200": {"description": "KPI metrics"}}}},
                "/products": {"get": {"summary": "List products"}, "post": {"summary": "Create product"}},
                "/shipments": {"get": {"summary": "List shipments"}, "post": {"summary": "Create shipment"}},
                "/compliance/analyze/{shipment_id}": {"post": {"summary": "Run 12-step compliance engine on shipment"}},
                "/temperature/readings": {"get": {"summary": "List telemetry readings"}, "post": {"summary": "Ingest reading"}},
                "/generator/run": {"post": {"summary": "Trigger deterministic synthetic dataset generation"}},
                "/validation/run": {"post": {"summary": "Run comprehensive integrity validation"}},
                "/evaluation/run": {"post": {"summary": "Evaluate detection against ground-truth labels"}},
                "/reproducibility/run": {"post": {"summary": "Verify fixed-seed reproducibility"}}
            }
        }
        return jsonify(spec)

    # Standardized Error Handlers
    @app.errorhandler(400)
    def handle_bad_request(e):
        return error_response("Invalid request payload or query parameters", error_code="BAD_REQUEST", status_code=400)

    @app.errorhandler(401)
    def handle_unauthorized(e):
        return error_response("Authentication required", error_code="UNAUTHORIZED", status_code=401)

    @app.errorhandler(403)
    def handle_forbidden(e):
        return error_response("Access forbidden: insufficient role permissions", error_code="FORBIDDEN", status_code=403)

    @app.errorhandler(404)
    def handle_not_found(e):
        return error_response("Requested resource not found", error_code="NOT_FOUND", status_code=404)

    @app.errorhandler(409)
    def handle_conflict(e):
        return error_response("Resource conflict or unique constraint violation", error_code="CONFLICT", status_code=409)

    @app.errorhandler(422)
    def handle_unprocessable(e):
        return error_response("Business rule validation failure", error_code="UNPROCESSABLE_ENTITY", status_code=422)

    @app.errorhandler(500)
    def handle_server_error(e):
        return error_response("Internal server error", error_code="INTERNAL_SERVER_ERROR", status_code=500)

    return app
