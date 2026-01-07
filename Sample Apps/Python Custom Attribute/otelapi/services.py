"""
Business logic services with OpenTelemetry API-based instrumentation

This module demonstrates:
1. ONLY API-based instrumentation (trace.get_current_span())
2. NO decorators - enriches existing auto-instrumented spans
3. Various data types: string, int, float, bool, list, dict

API-BASED IMPLEMENTATION - Enriches existing HTTP/DB spans
NO DECORATORS - No new spans created
"""
from opentelemetry import trace
from models import User
from datetime import datetime
import json


class UserService:
    """
    User service with API-based OpenTelemetry instrumentation
    
    Enriches existing auto-instrumented spans (HTTP, DB) with custom attributes
    """

    def __init__(self):
        """Initialize the UserService instance"""
        self.service_name = "UserService"

    def validate_user_data(self, data):
        """
        Validate user data - API-based (enriches existing span)
        Demonstrates: string, int, bool, list attributes
        
        Args:
            data (dict): User data to validate
            
        Returns:
            tuple: (is_valid, errors_list)
        """
        # Get the current active span (HTTP span from auto-instrumentation)
        span = trace.get_current_span()
        
        # Only add attributes if span is recording
        if span and span.is_recording():
            # String attributes
            span.set_attribute("apm.operation", "user_validation")
            span.set_attribute("apm.validation_type", "create_user")
            span.set_attribute("apm.service", self.service_name)
            
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
        
        # Add validation results to span
        if span and span.is_recording():
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
        
        return len(errors) == 0, errors

    def enrich_user_data(self, data):
        """
        Enrich user data with computed fields - API-based
        Demonstrates: string, float, dict attributes
        
        Args:
            data (dict): User data
            
        Returns:
            dict: Enriched user data
        """
        span = trace.get_current_span()
        
        if span and span.is_recording():
            # String attributes
            span.set_attribute("apm.enrichment_operation", "data_enrichment")
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
        data['full_name'] = f"{data.get('first_name', '')} {data.get('last_name', '')}".strip()
        data['data_completeness'] = round(sum(1 for v in data.values() if v) / len(data) * 100, 2)
        
        return data
    
    def get_all_users_with_stats(self):
        """
        Get all users with statistics - API-based
        Demonstrates: Enriching existing span with statistics
        """
        span = trace.get_current_span()

        if span and span.is_recording():
            # String attribute
            span.set_attribute("apm.operation", "get_all_users")
            span.set_attribute("apm.data_source", "postgresql")
            span.set_attribute("apm.service", self.service_name)

            # Add event before fetching
            span.add_event("Fetching users from database")

        # Fetch users
        users = User.get_all()

        if span and span.is_recording():
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

    def get_user_by_username_enriched(self, username):
        """
        Get user by username with enrichment - API-based
        Demonstrates: Enriching existing span with various data types
        """
        span = trace.get_current_span()

        if span and span.is_recording():
            # String attributes
            span.set_attribute("apm.operation", "get_user_by_username")
            span.set_attribute("apm.username_requested", username)
            span.set_attribute("apm.lookup_type", "primary_key")
            span.set_attribute("apm.service", self.service_name)

            # Boolean attribute
            span.set_attribute("apm.cache_enabled", False)  # Example

        # Fetch user
        user = User.get_by_username(username)

        if span and span.is_recording():
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

    def create_user_with_validation(self, data):
        """
        Create user with validation - API-based
        Demonstrates: Comprehensive attribute types on existing span
        """
        span = trace.get_current_span()

        if span and span.is_recording():
            # String attributes
            span.set_attribute("apm.operation", "create_user")
            span.set_attribute("apm.username", data.get('username', 'unknown'))
            span.set_attribute("apm.service", self.service_name)

            # Dict attribute (input data summary)
            input_summary = {
                "has_username": 'username' in data,
                "has_email": 'email' in data,
                "has_optional_fields": any(k in data for k in ['age', 'phone', 'address'])
            }
            span.set_attribute("apm.input_summary", json.dumps(input_summary))

        # Validate data (no new span created - enriches same span)
        is_valid, errors = self.validate_user_data(data)

        if not is_valid:
            if span and span.is_recording():
                # List attribute
                span.set_attribute("apm.validation_errors", json.dumps(errors))
                span.set_attribute("apm.creation_status", "failed_validation")
            return None, errors[0] if errors else "Validation failed"

        # Enrich data (no new span created - enriches same span)
        enriched_data = self.enrich_user_data(data)

        # Create user
        username, error = User.create(data)

        if span and span.is_recording():
            # Boolean attribute
            span.set_attribute("apm.creation_successful", error is None)

            if error:
                span.set_attribute("apm.creation_status", "failed_database")
                span.set_attribute("apm.error_message", error)
            else:
                span.set_attribute("apm.creation_status", "success")
                span.set_attribute("apm.created_username", username)

        return username, error

    def update_user_with_tracking(self, username, data):
        """
        Update user with change tracking - API-based
        Demonstrates: Change tracking on existing span
        """
        span = trace.get_current_span()

        if span and span.is_recording():
            # String attributes
            span.set_attribute("apm.operation", "update_user")
            span.set_attribute("apm.username", username)
            span.set_attribute("apm.service", self.service_name)

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

        if span and span.is_recording():
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

    def delete_user_with_audit(self, username):
        """
        Delete user with audit trail - API-based
        Demonstrates: Audit logging with comprehensive attributes
        """
        span = trace.get_current_span()

        if span and span.is_recording():
            # String attributes
            span.set_attribute("apm.operation", "delete_user")
            span.set_attribute("apm.username", username)
            span.set_attribute("apm.audit_action", "user_deletion")
            span.set_attribute("apm.service", self.service_name)

        # Get user before deletion for audit
        user = User.get_by_username(username)

        if span and span.is_recording():
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

        if span and span.is_recording():
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


