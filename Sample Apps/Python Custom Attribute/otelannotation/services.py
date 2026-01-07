"""
Business logic services with OpenTelemetry annotation-based instrumentation

This module demonstrates:
1. ONLY Decorator-based instrumentation (@tracer.start_as_current_span)
2. Creates NEW spans for all operations
3. Various data types: string, int, float, bool, list, dict

OOP-BASED IMPLEMENTATION - All methods use 'self' (instance methods)
ANNOTATION-ONLY - No API-based approach (no trace.get_current_span())
"""
from opentelemetry import trace
from otel_config import get_tracer
from models import User
from datetime import datetime
import json

# Get tracer instance for this module
tracer = get_tracer(__name__)


class UserService:
    """
    User service with comprehensive OpenTelemetry instrumentation

    OOP-based implementation using instance methods with 'self'
    """

    def __init__(self):
        """Initialize the UserService instance"""
        self.tracer = tracer
        self.service_name = "UserService"

    @tracer.start_as_current_span("user_service.validate_user_data")
    def validate_user_data(self, data):
        """
        Validate user data - Creates NEW SPAN with decorator
        Demonstrates: string, int, bool, list attributes
        
        Args:
            data (dict): User data to validate
            
        Returns:
            tuple: (is_valid, errors_list)
        """
        span = trace.get_current_span()
        
        # String attributes
        span.set_attribute("apm.operation", "user_validation")
        span.set_attribute("apm.validation_type", "create_user")
        
        # Integer attributes
        span.set_attribute("apm.field_count", len(data))
        
        # Boolean attributes
        has_optional_fields = any(key in data for key in ['age', 'phone', 'address'])
        span.set_attribute("apm.has_optional_fields", has_optional_fields)

        errors = []
        required_fields = ['username', 'email', 'first_name', 'last_name']
        
        for field in required_fields:
            if field not in data or not data[field]:
                errors.append(f"Missing required field: {field}")
        
        # List attributes (convert to JSON string for complex types)
        if errors:
            span.set_attribute("apm.validation_errors", json.dumps(errors))
        
        # Integer attribute
        span.set_attribute("apm.error_count", len(errors))
        
        # Boolean attribute
        is_valid = len(errors) == 0
        span.set_attribute("apm.validation_passed", is_valid)
        
        # Add event
        span.add_event("Validation completed", {
            "validation.result": "success" if is_valid else "failed",
            "validation.error_count": len(errors)
        })
        
        return is_valid, errors

    @tracer.start_as_current_span("user_service.enrich_user_data")
    def enrich_user_data(self, data):
        """
        Enrich user data with computed fields - Creates NEW SPAN
        Demonstrates: string, float, dict attributes
        
        Args:
            data (dict): User data
            
        Returns:
            dict: Enriched user data
        """
        span = trace.get_current_span()
        
        # String attributes
        span.set_attribute("apm.operation", "data_enrichment")
        span.set_attribute("apm.username", data.get('username', 'unknown'))
        
        # Compute full name
        full_name = f"{data.get('first_name', '')} {data.get('last_name', '')}".strip()
        span.set_attribute("apm.full_name", full_name)
        
        # Float attribute (simulated score)
        data_completeness = sum(1 for v in data.values() if v) / len(data) * 100
        span.set_attribute("apm.data_completeness_percent", round(data_completeness, 2))
        
        # Dict attributes (as JSON string)
        metadata = {
            "enriched_at": datetime.now().isoformat(),
            "enrichment_version": "1.0",
            "fields_present": list(data.keys())
        }
        span.set_attribute("apm.enrichment_metadata", json.dumps(metadata))
        
        # Add enriched fields to data
        data['full_name'] = full_name
        data['data_completeness'] = round(data_completeness, 2)
        
        return data
    
    @tracer.start_as_current_span("user_service.get_all_users_with_stats")
    def get_all_users_with_stats(self):
        """
        Get all users with statistics - Creates NEW SPAN with decorator
        Demonstrates: Annotation-based instrumentation with statistics
        """
        span = trace.get_current_span()

        # String attribute
        span.set_attribute("apm.operation", "get_all_users")
        span.set_attribute("apm.data_source", "postgresql")

        # Add event before fetching
        span.add_event("Fetching users from database")

        # Fetch users
        users = User.get_all()

        # Integer attributes
        span.set_attribute("apm.user_count", len(users))
        span.set_attribute("apm.result_size", len(users))

        # Boolean attribute
        span.set_attribute("apm.has_results", len(users) > 0)

        # List attribute (user IDs)
        if users:
            usernames = [user.get('username') for user in users if user.get('username')]
            span.set_attribute("apm.usernames_fetched", json.dumps(usernames[:10]))  # Limit to 10

        # Float attribute (average age if available)
        ages = [user.get('age') for user in users if user.get('age')]
        if ages:
            avg_age = sum(ages) / len(ages)
            span.set_attribute("apm.average_user_age", round(avg_age, 2))

        # Add completion event
        span.add_event("Users fetched successfully", {
            "fetch.count": len(users),
            "fetch.duration_ms": 0  # Would be calculated in real scenario
        })

        return users

    @tracer.start_as_current_span("user_service.get_user_by_username_enriched")
    def get_user_by_username_enriched(self, username):
        """
        Get user by username with enrichment - Creates NEW SPAN with decorator
        Demonstrates: Annotation-based instrumentation with various data types
        """
        span = trace.get_current_span()

        # String attributes
        span.set_attribute("apm.operation", "get_user_by_username")
        span.set_attribute("apm.username_requested", username)
        span.set_attribute("apm.lookup_type", "primary_key")

        # Boolean attribute
        span.set_attribute("apm.cache_enabled", False)  # Example

        # Fetch user
        user = User.get_by_username(username)

        # Boolean attribute
        span.set_attribute("apm.user_found", user is not None)

        if user:
            # String attributes
            span.set_attribute("apm.user_email", user.get('email', 'N/A'))

            # Integer attribute
            if user.get('age'):
                span.set_attribute("apm.user_age", user.get('age'))

            # Dict attribute (user summary)
            user_summary = {
                "username": user.get('username'),
                "has_phone": bool(user.get('phone')),
                "has_address": bool(user.get('address')),
                "created_at": str(user.get('created_at'))
            }
            span.set_attribute("apm.user_summary", json.dumps(user_summary))

            span.add_event("User found", {"username": username})
        else:
            span.add_event("User not found", {"username": username})

        return user

    @tracer.start_as_current_span("user_service.create_user_with_validation")
    def create_user_with_validation(self, data):
        """
        Create user with validation - Creates NEW SPAN
        Demonstrates: Nested spans and comprehensive attribute types
        """
        span = trace.get_current_span()

        # String attributes
        span.set_attribute("apm.operation", "create_user")
        span.set_attribute("apm.username", data.get('username', 'unknown'))

        # Dict attribute (input data summary)
        input_summary = {
            "has_username": 'username' in data,
            "has_email": 'email' in data,
            "has_optional_fields": any(k in data for k in ['age', 'phone', 'address'])
        }
        span.set_attribute("apm.input_summary", json.dumps(input_summary))

        # Validate data (creates nested span)
        is_valid, errors = self.validate_user_data(data)

        if not is_valid:
            # List attribute
            span.set_attribute("apm.validation_errors", json.dumps(errors))
            span.set_attribute("apm.creation_status", "failed_validation")
            return None, errors[0] if errors else "Validation failed"

        # Enrich data (creates nested span)
        enriched_data = self.enrich_user_data(data)

        # Create user
        username, error = User.create(data)

        # Boolean attribute
        span.set_attribute("apm.creation_successful", error is None)

        if error:
            span.set_attribute("apm.creation_status", "failed_database")
            span.set_attribute("apm.error_message", error)
        else:
            span.set_attribute("apm.creation_status", "success")
            span.set_attribute("apm.created_username", username)

        return username, error

    @tracer.start_as_current_span("user_service.update_user_with_tracking")
    def update_user_with_tracking(self, username, data):
        """
        Update user with change tracking - Creates NEW SPAN with decorator
        Demonstrates: Annotation-based instrumentation with change tracking
        """
        span = trace.get_current_span()

        # String attributes
        span.set_attribute("apm.operation", "update_user")
        span.set_attribute("apm.username", username)

        # Integer attribute
        span.set_attribute("apm.fields_to_update", len(data))

        # List attribute (fields being updated)
        span.set_attribute("apm.updated_fields", json.dumps(list(data.keys())))

        # Dict attribute (update summary)
        update_summary = {
            "timestamp": datetime.now().isoformat(),
            "field_count": len(data),
            "fields": list(data.keys())
        }
        span.set_attribute("apm.update_summary", json.dumps(update_summary))

        # Perform update
        success, error = User.update(username, data)

        # Boolean attribute
        span.set_attribute("apm.update_successful", success)

        if error:
            span.set_attribute("apm.error_message", error)
            span.set_attribute("apm.error_type", "not_found" if "not found" in error.lower() else "database_error")

        # Add event
        span.add_event("Update completed", {
            "success": success,
            "username": username
        })

        return success, error

    @tracer.start_as_current_span("user_service.delete_user_with_audit")
    def delete_user_with_audit(self, username):
        """
        Delete user with audit trail - Creates NEW SPAN
        Demonstrates: Audit logging with comprehensive attributes
        """
        span = trace.get_current_span()

        # String attributes
        span.set_attribute("apm.operation", "delete_user")
        span.set_attribute("apm.username", username)
        span.set_attribute("apm.audit_action", "user_deletion")

        # Get user before deletion for audit
        user = User.get_by_username(username)

        if user:
            # Dict attribute (audit trail)
            audit_data = {
                "deleted_username": username,
                "deleted_email": user.get('email'),
                "deletion_timestamp": datetime.now().isoformat(),
                "user_existed_since": str(user.get('created_at'))
            }
            span.set_attribute("apm.audit_trail", json.dumps(audit_data))

            # Boolean attribute
            span.set_attribute("apm.user_existed", True)
        else:
            span.set_attribute("apm.user_existed", False)

        # Perform deletion
        success, error = User.delete(username)

        # Boolean attribute
        span.set_attribute("apm.deletion_successful", success)

        if error:
            span.set_attribute("apm.error_message", error)

        # Add event
        span.add_event("Deletion attempt completed", {
            "success": success,
            "username": username,
            "user_existed": user is not None
        })

        return success, error


