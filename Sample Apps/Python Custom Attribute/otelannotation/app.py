"""
Main Flask application entry point with OpenTelemetry instrumentation
"""
from flask import Flask, jsonify
from flasgger import Swagger
from config import config
from database import init_db
from routes import user_bp
from otel_config import init_telemetry

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

    # Initialize OpenTelemetry (must be done before other initializations)
    init_telemetry(app)

    # Initialize Swagger
    swagger = Swagger(app,
                     config=app.config['SWAGGER_CONFIG'],
                     template=app.config['SWAGGER_TEMPLATE'])

    # Register blueprints
    app.register_blueprint(user_bp)

    # Home route
    @app.route('/')
    def home():
        """Home route with API information"""
        return jsonify({
            "message": "Welcome to User Management API with OpenTelemetry",
            "version": "2.0.0",
            "instrumentation": "OpenTelemetry Annotation-Based ONLY (Decorator)",
            "documentation": "/swagger",
            "primary_key": "username",
            "endpoints": {
                "get_all_users": "GET /api/users (@decorator - creates new span)",
                "get_user_by_username": "GET /api/users/<username> (@decorator - creates new span)",
                "create_user": "POST /api/users (@decorator - creates nested spans)",
                "update_user": "PUT /api/users/<username> (@decorator - creates new span)",
                "delete_user": "DELETE /api/users/<username> (@decorator - creates new span)"
            },
            "note": "Username is the primary key. No auto-generated IDs are used.",
            "telemetry_features": [
                "ANNOTATION-ONLY: All methods use @tracer.start_as_current_span() decorator",
                "NO API-based approach (no trace.get_current_span())",
                "All service methods create NEW spans",
                "Various data types: string, int, float, bool, list, dict",
                "Nested spans for complex operations",
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

