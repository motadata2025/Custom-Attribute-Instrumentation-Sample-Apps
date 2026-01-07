"""
Main Flask application entry point with Manual Tracer instrumentation

This module demonstrates:
- Manual Tracer approach: Full control over span lifecycle
- Auto-instrumentation for Flask, PostgreSQL (creates base spans)
- Complex workflows with custom span hierarchies
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
    setup_opentelemetry(app, service_name="PythonCustomAttributesTracer")

    # Home route
    @app.route('/')
    def home():
        """Home route with API information"""
        return jsonify({
            "message": "Welcome to User Management API with OpenTelemetry",
            "version": "2.0.0",
            "instrumentation": "OpenTelemetry Manual Tracer (Method 3)",
            "documentation": "/swagger",
            "primary_key": "username",
            "endpoints": {
                "get_all_users": "GET /api/users (Complex workflow with nested spans)",
                "get_user_by_username": "GET /api/users/<username> (Validation workflow)",
                "create_user": "POST /api/users (5-step creation workflow)",
                "update_user": "PUT /api/users/<username> (Change tracking workflow)",
                "delete_user": "DELETE /api/users/<username> (Backup & cleanup workflow)"
            },
            "note": "Username is the primary key. No auto-generated IDs are used.",
            "telemetry_features": [
                "MANUAL TRACER: Full control over span lifecycle",
                "Complex nested span hierarchies",
                "Multi-step workflows with custom spans",
                "Events and audit trails in each step",
                "Perfect for complex business logic",
                "Uses tracer.start_as_current_span() context manager"
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

