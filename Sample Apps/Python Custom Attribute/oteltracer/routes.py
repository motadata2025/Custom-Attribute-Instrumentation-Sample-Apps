"""
API routes and controllers with Manual Tracer instrumentation

This module demonstrates:
- Manual Tracer approach: Creates custom spans with full lifecycle control
- Uses UserService which creates complex span hierarchies
- Perfect for multi-step workflows
"""
from flask import Blueprint, request, jsonify
from opentelemetry import trace
from models import User
from services import UserService

# Create Blueprint for user routes
user_bp = Blueprint('users', __name__, url_prefix='/api')

# Get tracer instance
tracer = trace.get_tracer(__name__)

# Create service instance
user_service = UserService()

@user_bp.route('/users', methods=['GET'])
def get_users():
    """
    Get all users with Manual Tracer workflow
    ---
    tags:
      - Users
    responses:
      200:
        description: A list of all users with statistics
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
    # Manual Tracer: Service creates complex workflow with nested spans
    result = user_service.get_all_users_with_workflow()
    return jsonify(result), 200

@user_bp.route('/users/<string:username>', methods=['GET'])
def get_user(username):
    """
    Get a specific user by username with validation workflow
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
    # Manual Tracer: Service creates validation workflow with nested spans
    user = user_service.get_user_with_validation(username)

    if user is None:
        return jsonify({"error": "User not found"}), 404

    return jsonify(user), 200

@user_bp.route('/users', methods=['POST'])
def create_user():
    """
    Create a new user with complex validation workflow
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
    data = request.get_json()

    # Manual Tracer: Service creates complex creation workflow with nested spans
    username, error = user_service.create_user_with_workflow(data)

    if error:
        return jsonify({"error": error}), 400

    return jsonify({"message": "User created successfully", "username": username}), 201

@user_bp.route('/users/<string:username>', methods=['PUT'])
def update_user(username):
    """
    Update an existing user with change tracking workflow
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
    data = request.get_json()

    # Manual Tracer: Service creates update workflow with change tracking
    success, error = user_service.update_user_with_workflow(username, data)

    if error:
        status_code = 404 if error == "User not found" else 400
        return jsonify({"error": error}), status_code

    return jsonify({"message": "User updated successfully"}), 200

@user_bp.route('/users/<string:username>', methods=['DELETE'])
def delete_user(username):
    """
    Delete a user with backup and cleanup workflow
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
    # Manual Tracer: Service creates deletion workflow with backup and cleanup
    success, error = user_service.delete_user_with_workflow(username)

    if error:
        return jsonify({"error": error}), 404

    return jsonify({"message": "User deleted successfully"}), 200

