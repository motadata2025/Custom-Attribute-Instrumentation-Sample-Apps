"""
API routes and controllers with OpenTelemetry API-based instrumentation

This module demonstrates:
- API-based approach: Enriches existing auto-instrumented HTTP spans
- No decorators on routes
- Uses UserService which enriches spans with custom attributes
"""
from flask import Blueprint, request, jsonify
from opentelemetry import trace
from models import User
from services import UserService
import json
import base64
from util.MotadataDynamicInstrumentation import MotadataDynamicInstrumentation

# Create Blueprint for user routes
user_bp = Blueprint('users', __name__, url_prefix='/api')

# Create service instance
user_service = UserService()

@user_bp.route('/users', methods=['GET'])
def get_users():
    """
    Get all users with API-based instrumentation
    ---
    tags:
      - Users
    responses:
      200:
        description: A list of all users
        schema:
          type: array
          items:
            type: object
            properties:
              username:
                type: string
                description: Username (Primary Key)
              email:
                type: string
                description: Email address
              first_name:
                type: string
                description: First name
              last_name:
                type: string
                description: Last name
              age:
                type: integer
                description: Age
              phone:
                type: string
                description: Phone number
              address:
                type: string
                description: Address
              created_at:
                type: string
                description: Creation timestamp
              updated_at:
                type: string
                description: Last update timestamp
    """
    # API-based: Enrich the existing HTTP span
    span = trace.get_current_span()
    if span and span.is_recording():
        span.set_attribute("apm.endpoint", "get_all_users")
        span.set_attribute("apm.method", "GET")

    # Uses service which enriches the same span (no new span created)
    users = user_service.get_all_users_with_stats()
    return jsonify(users), 200

@user_bp.route('/users/<string:username>', methods=['GET'])
def get_user(username):
    """
    Get a specific user by username with API-based instrumentation
    ---
    tags:
      - Users
    parameters:
      - name: username
        in: path
        type: string
        required: true
        description: The username (Primary Key)
        example: john_doe
    responses:
      200:
        description: User details
        schema:
          type: object
          properties:
            username:
              type: string
            email:
              type: string
            first_name:
              type: string
            last_name:
              type: string
            age:
              type: integer
            phone:
              type: string
            address:
              type: string
            created_at:
              type: string
            updated_at:
              type: string
      404:
        description: User not found
        schema:
          type: object
          properties:
            error:
              type: string
    """
    # API-based: Enrich the existing HTTP span
    span = trace.get_current_span()
    if span and span.is_recording():
        span.set_attribute("apm.endpoint", "get_user_by_username")
        span.set_attribute("apm.method", "GET")
        span.set_attribute("apm.username_param", username)

    # Uses service which enriches the same span (no new span created)
    user = user_service.get_user_by_username_enriched(username)

    if user is None:
        if span and span.is_recording():
            span.set_attribute("apm.result", "not_found")
        return jsonify({"error": "User not found"}), 404

    if span and span.is_recording():
        span.set_attribute("apm.result", "success")

    return jsonify(user), 200

@user_bp.route('/users', methods=['POST'])
def create_user():
    """
    Create a new user with API-based instrumentation
    ---
    tags:
      - Users
    parameters:
      - name: body
        in: body
        required: true
        description: User data to create
        schema:
          type: object
          required:
            - username
            - email
            - first_name
            - last_name
          properties:
            username:
              type: string
              description: Unique username (Primary Key)
              example: john_doe
            email:
              type: string
              description: Email address
              example: john@example.com
            first_name:
              type: string
              description: First name
              example: John
            last_name:
              type: string
              description: Last name
              example: Doe
            age:
              type: integer
              description: Age (optional)
              example: 30
            phone:
              type: string
              description: Phone number (optional)
              example: +1-555-0111
            address:
              type: string
              description: Address (optional)
              example: 123 Main St, City, State
    responses:
      201:
        description: User created successfully
        schema:
          type: object
          properties:
            message:
              type: string
            username:
              type: string
      400:
        description: Invalid input or username already exists
        schema:
          type: object
          properties:
            error:
              type: string
    """
    # API-based: Enrich the existing HTTP span
    span = trace.get_current_span()
    if span and span.is_recording():
        span.set_attribute("apm.endpoint", "create_user")
        span.set_attribute("apm.method", "POST")

    data = request.get_json()

    if span and span.is_recording():
        span.set_attribute("apm.request_body_size", len(json.dumps(data)))

    # Uses service which enriches the same span (no new span created)
    username, error = user_service.create_user_with_validation(data)

    if error:
        if span and span.is_recording():
            span.set_attribute("apm.result", "failed")
        return jsonify({"error": error}), 400

    if span and span.is_recording():
        span.set_attribute("apm.result", "success")

    return jsonify({"message": "User created successfully", "username": username}), 201

@user_bp.route('/users/<string:username>', methods=['PUT'])
def update_user(username):
    """
    Update an existing user with API-based instrumentation
    ---
    tags:
      - Users
    parameters:
      - name: username
        in: path
        type: string
        required: true
        description: The username (Primary Key) - Note username cannot be changed
        example: john_doe
      - name: body
        in: body
        required: true
        description: Fields to update (username cannot be updated)
        schema:
          type: object
          properties:
            email:
              type: string
              description: Email address
              example: newemail@example.com
            first_name:
              type: string
              description: First name
              example: John
            last_name:
              type: string
              description: Last name
              example: Doe
            age:
              type: integer
              description: Age
              example: 35
            phone:
              type: string
              description: Phone number
              example: +1-555-0112
            address:
              type: string
              description: Address
              example: 456 New St, City, State
    responses:
      200:
        description: User updated successfully
        schema:
          type: object
          properties:
            message:
              type: string
      404:
        description: User not found
        schema:
          type: object
          properties:
            error:
              type: string
      400:
        description: Invalid input
        schema:
          type: object
          properties:
            error:
              type: string
    """
    # API-based: Enrich the existing HTTP span
    span = trace.get_current_span()
    if span and span.is_recording():
        span.set_attribute("apm.endpoint", "update_user")
        span.set_attribute("apm.method", "PUT")
        span.set_attribute("apm.username_param", username)

    data = request.get_json()

    # Uses service which enriches the same span (no new span created)
    success, error = user_service.update_user_with_tracking(username, data)

    if error:
        status_code = 404 if error == "User not found" else 400
        if span and span.is_recording():
            span.set_attribute("apm.result", "failed")
            span.set_attribute("apm.error_type", "not_found" if status_code == 404 else "validation_error")
        return jsonify({"error": error}), status_code

    if span and span.is_recording():
        span.set_attribute("apm.result", "success")

    return jsonify({"message": "User updated successfully"}), 200

@user_bp.route('/users/<string:username>', methods=['DELETE'])
def delete_user(username):
    """
    Delete a user with API-based instrumentation
    ---
    tags:
      - Users
    parameters:
      - name: username
        in: path
        type: string
        required: true
        description: The username (Primary Key)
        example: john_doe
    responses:
      200:
        description: User deleted successfully
        schema:
          type: object
          properties:
            message:
              type: string
      404:
        description: User not found
        schema:
          type: object
          properties:
            error:
              type: string
    """
    # API-based: Enrich the existing HTTP span
    span = trace.get_current_span()
    if span and span.is_recording():
        span.set_attribute("apm.endpoint", "delete_user")
        span.set_attribute("apm.method", "DELETE")
        span.set_attribute("apm.username_param", username)

    # Uses service which enriches the same span (no new span created)
    success, error = user_service.delete_user_with_audit(username)

    if error:
        if span and span.is_recording():
            span.set_attribute("apm.result", "failed")
        return jsonify({"error": error}), 404

    if span and span.is_recording():
        span.set_attribute("apm.result", "success")

    return jsonify({"message": "User deleted successfully"}), 200


@user_bp.route('/test/datatypes', methods=['GET'])
def test_all_datatypes():
    """
    Test endpoint demonstrating ALL supported OpenTelemetry data types
    ---
    tags:
      - Testing
    responses:
      200:
        description: Successfully demonstrated all OTel data types in span attributes
        schema:
          type: object
          properties:
            message:
              type: string
            datatypes_tested:
              type: object
    """
    span = trace.get_current_span()

    if span and span.is_recording():
        # ============================================================
        # PRIMITIVE DATA TYPES (Fully Supported)
        # ============================================================

        # 1. STRING (str)
        span.set_attribute("apm.string.simple", "Hello OpenTelemetry")
        span.set_attribute("apm.string.with_special_chars", "Special: @#$%^&*()")
        span.set_attribute("apm.string.unicode", "Unicode: 你好 🌍 مرحبا")
        span.set_attribute("apm.string.empty", "")
        span.set_attribute("apm.string.long", "A" * 100)

        # 2. BOOLEAN (bool)
        span.set_attribute("apm.bool.true", True)
        span.set_attribute("apm.bool.false", False)

        # 3. INTEGER (int)
        span.set_attribute("apm.int.positive", 42)
        span.set_attribute("apm.int.negative", -100)
        span.set_attribute("apm.int.zero", 0)
        span.set_attribute("apm.int.large", 9999999999)
        span.set_attribute("apm.int.max_safe", 2**53 - 1)  # JavaScript safe integer

        # 4. FLOAT (float)
        span.set_attribute("apm.float.positive", 3.14159)
        span.set_attribute("apm.float.negative", -2.71828)
        span.set_attribute("apm.float.zero", 0.0)
        span.set_attribute("apm.float.scientific", 1.23e-4)
        span.set_attribute("apm.float.large", 1.7976931348623157e+308)

        # ============================================================
        # SEQUENCE/ARRAY DATA TYPES (Fully Supported - Homogeneous)
        # ============================================================

        # 5. SEQUENCE OF STRINGS (Sequence[str])
        span.set_attribute("apm.array.strings", ["apple", "banana", "cherry"])
        span.set_attribute("apm.array.strings.empty", [])
        span.set_attribute("apm.array.strings.single", ["solo"])
        span.set_attribute("apm.array.strings.with_unicode", ["Hello", "世界", "🎉"])

        # 6. SEQUENCE OF BOOLEANS (Sequence[bool])
        span.set_attribute("apm.array.bools", [True, False, True, True])
        span.set_attribute("apm.array.bools.all_true", [True, True, True])
        span.set_attribute("apm.array.bools.all_false", [False, False])

        # 7. SEQUENCE OF INTEGERS (Sequence[int])
        span.set_attribute("apm.array.ints", [1, 2, 3, 4, 5])
        span.set_attribute("apm.array.ints.negative", [-10, -20, -30])
        span.set_attribute("apm.array.ints.mixed", [-5, 0, 5, 10])
        span.set_attribute("apm.array.ints.large", [1000000, 2000000, 3000000])

        # 8. SEQUENCE OF FLOATS (Sequence[float])
        span.set_attribute("apm.array.floats", [1.1, 2.2, 3.3, 4.4])
        span.set_attribute("apm.array.floats.negative", [-1.5, -2.5, -3.5])
        span.set_attribute("apm.array.floats.scientific", [1.23e-4, 5.67e8])
        span.set_attribute("apm.array.floats.mixed", [-1.1, 0.0, 1.1, 2.2])

        # ============================================================
        # COMPLEX DATA TYPES (Serialized as JSON strings)
        # Note: These are not natively supported in current stable version
        # but can be serialized to JSON strings for compatibility
        # ============================================================

        # 9. NESTED DICTIONARIES (as JSON string)
        nested_dict = {
            "user": {
                "name": "John Doe",
                "age": 30,
                "active": True
            },
            "metadata": {
                "created": "2025-12-23",
                "version": 1.0
            }
        }
        span.set_attribute("apm.dict.nested", json.dumps(nested_dict))

        # 10. HETEROGENEOUS ARRAYS (as JSON string)
        mixed_array = ["string", 123, True, 3.14, None]
        span.set_attribute("apm.array.mixed_types", json.dumps(mixed_array))

        # 11. COMPLEX NESTED STRUCTURE (as JSON string)
        complex_structure = {
            "items": [
                {"id": 1, "name": "Item 1", "price": 10.99, "available": True},
                {"id": 2, "name": "Item 2", "price": 20.50, "available": False}
            ],
            "total": 31.49,
            "count": 2
        }
        span.set_attribute("apm.complex.structure", json.dumps(complex_structure))

        # ============================================================
        # SPECIAL CASES
        # ============================================================

        # 12. NULL/NONE VALUES (represented as empty string or omitted)
        # Note: None is not directly supported in AttributeValue, but is in AnyValue
        span.set_attribute("apm.special.null_as_string", "null")

        # 13. BYTES (not supported in AttributeValue, but in AnyValue for logs)
        # For now, encode as base64 string
        byte_data = b"Binary data \x00\x01\x02"
        span.set_attribute("apm.bytes.base64", base64.b64encode(byte_data).decode('utf-8'))

        # ============================================================
        # SPAN EVENTS (can also have attributes)
        # ============================================================

        span.add_event("DataTypeTest.Started", {
            "apm.event.string": "Event attribute",
            "apm.event.int": 100,
            "apm.event.bool": True,
            "apm.event.float": 99.99
        })

        span.add_event("DataTypeTest.ArraysDemo", {
            "apm.event.array.strings": json.dumps(["event", "array", "demo"]),
            "apm.event.array.ints": json.dumps([10, 20, 30])
        })

        span.add_event("DataTypeTest.Completed", {
            "apm.event.status": "success",
            "apm.event.types_tested": 13
        })

    # Response with summary
    response = {
        "message": "All OpenTelemetry data types demonstrated successfully",
        "datatypes_tested": {
            "primitives": {
                "string": "✓ Tested with simple, special chars, unicode, empty, long",
                "boolean": "✓ Tested with true and false",
                "integer": "✓ Tested with positive, negative, zero, large values",
                "float": "✓ Tested with positive, negative, zero, scientific notation"
            },
            "sequences": {
                "sequence_of_strings": "✓ Tested with various string arrays",
                "sequence_of_booleans": "✓ Tested with boolean arrays",
                "sequence_of_integers": "✓ Tested with integer arrays",
                "sequence_of_floats": "✓ Tested with float arrays"
            },
            "complex_serialized": {
                "nested_dictionaries": "✓ Serialized as JSON string",
                "heterogeneous_arrays": "✓ Serialized as JSON string",
                "complex_structures": "✓ Serialized as JSON string"
            },
            "special": {
                "null_values": "✓ Represented as string 'null'",
                "bytes": "✓ Encoded as base64 string"
            },
            "events": {
                "span_events": "✓ Added 3 events with various attribute types"
            }
        },
        "note": "Check your OpenTelemetry backend to see all attributes in the span",
        "specification": {
            "stable_types": [
                "str", "bool", "int", "float",
                "Sequence[str]", "Sequence[bool]", "Sequence[int]", "Sequence[float]"
            ],
            "extended_types_for_logs": [
                "bytes", "Sequence[AnyValue]", "Mapping[str, AnyValue]", "None"
            ],
            "future_support": "Complex attribute types (maps, heterogeneous arrays) coming to all signals in OTLP 1.9.0+"
        }
    }

    return jsonify(response), 200

@user_bp.route('/test/motadata', methods=['GET'])
def test_motadata_instrumentation():
    """
    Test MotadataDynamicInstrumentation utility methods
    ---
    tags:
      - Testing
    responses:
      200:
        description: Successfully tested MotadataDynamicInstrumentation methods
        schema:
          type: object
          properties:
            message:
              type: string
            tested_values:
              type: object
    """
    # Scalar values
    MotadataDynamicInstrumentation.set("test.bool", True)
    MotadataDynamicInstrumentation.set("test.int", 42)
    MotadataDynamicInstrumentation.set("test.float", 3.14)
    MotadataDynamicInstrumentation.set("test.string", "Motadata Test")

    # List values
    MotadataDynamicInstrumentation.set_bool_list("test.bool_list", [True, False, True])
    MotadataDynamicInstrumentation.set_int_list("test.int_list", [1, 2, 3, 4, 5])
    MotadataDynamicInstrumentation.set_float_list("test.float_list", [1.1, 2.2, 3.3])
    MotadataDynamicInstrumentation.set_string_list("test.string_list", ["one", "two", "three"])

    return jsonify({
        "message": "MotadataDynamicInstrumentation methods invoked",
        "tested_values": {
            "scalars": {
                "test.bool": True,
                "test.int": 42,
                "test.float": 3.14,
                "test.string": "Motadata Test"
            },
            "lists": {
                "test.bool_list": [True, False, True],
                "test.int_list": [1, 2, 3, 4, 5],
                "test.float_list": [1.1, 2.2, 3.3],
                "test.string_list": ["one", "two", "three"]
            }
        }
    }), 200
