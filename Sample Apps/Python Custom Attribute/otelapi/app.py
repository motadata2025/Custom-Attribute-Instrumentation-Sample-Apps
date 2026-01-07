"""
Main Flask application entry point with OpenTelemetry API-based instrumentation

This module demonstrates:
- API-based approach: Enriches existing auto-instrumented spans
- Auto-instrumentation for Flask, PostgreSQL
- No decorators - all attributes added via trace.get_current_span()
"""
from flask import Flask, jsonify
from flasgger import Swagger
from config import config
from database import init_db
from routes import user_bp
from otel_config import setup_opentelemetry

def create_app(config_name='default'):
    """
    Application factory pattern

    Args:
        config_name (str): Configuration name (development, production, default)

    Returns:
        Flask: Configured Flask application
    """
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config[config_name])

    # Initialize Swagger
    swagger = Swagger(app,
                     config=app.config['SWAGGER_CONFIG'],
                     template=app.config['SWAGGER_TEMPLATE'])

    # Register blueprints
    app.register_blueprint(user_bp)

    # Initialize OpenTelemetry
    setup_opentelemetry(app, service_name="PythonCustomAttributesAPI")

    # Home route
    @app.route('/')
    def home():
        """Home route with API information"""
        return jsonify({
            "message": "Welcome to User Management API with OpenTelemetry",
            "version": "2.0.0",
            "instrumentation": "OpenTelemetry API-Based ONLY (No Decorators)",
            "documentation": "/swagger",
            "primary_key": "username",
            "endpoints": {
                "get_all_users": "GET /api/users (API-based - enriches HTTP span)",
                "get_user_by_username": "GET /api/users/<username> (API-based - enriches HTTP span)",
                "create_user": "POST /api/users (API-based - enriches HTTP span)",
                "update_user": "PUT /api/users/<username> (API-based - enriches HTTP span)",
                "delete_user": "DELETE /api/users/<username> (API-based - enriches HTTP span)",
                "test_motadata": "GET /api/test/motadata (Tests MotadataDynamicInstrumentation)"
            },
            "note": "Username is the primary key. No auto-generated IDs are used.",
            "telemetry_features": [
                "API-BASED ONLY: All methods use trace.get_current_span()",
                "NO decorators - no new spans created",
                "Enriches existing auto-instrumented spans (HTTP, DB)",
                "Various data types: string, int, float, bool, list, dict",
                "Flat span structure - all attributes on HTTP span",
                "Events and audit trails"
            ]
        })

    return app

if __name__ == '__main__':
    # Initialize database
    init_db()

    # Create and run application
    app = create_app('development')
    app.run(
        debug=app.config['DEBUG'],
        host=app.config['HOST'],
        port=app.config['PORT'],
        use_reloader=False
    )

