"""
Business logic with Manual Tracer & Span Creation (Method 3)

This module demonstrates:
- Manual span creation with tracer.start_as_current_span()
- Complex nested span hierarchies
- Full control over span lifecycle
- Multi-step workflows with custom spans
"""
from opentelemetry import trace
from models import User
import time
import json

# Get a tracer instance (done once at module level)
tracer = trace.get_tracer(__name__)


class UserService:
    """
    User service with manual tracer instrumentation

    Demonstrates Method 3: Manual Tracer & Span Creation
    - Creates custom spans with full lifecycle control
    - Builds complex span hierarchies
    - Perfect for multi-step workflows
    """

    def __init__(self):
        self.service_name = "UserService"

    def get_all_users_with_workflow(self):
        """
        Get all users with a complex multi-step workflow

        Creates custom span hierarchy:
        - Parent: user_workflow.get_all_users
          - Child: user_workflow.fetch_from_db
          - Child: user_workflow.enrich_data
          - Child: user_workflow.calculate_stats
        """
        # Create parent span for the entire workflow
        with tracer.start_as_current_span("user_workflow.get_all_users") as workflow_span:
            workflow_span.set_attribute("apm.service", self.service_name)
            workflow_span.set_attribute("apm.operation", "get_all_users")
            workflow_span.set_attribute("workflow.type", "get_all_users")
            workflow_span.set_attribute("workflow.service", self.service_name)
            workflow_span.add_event("Workflow started")

            # Step 1: Fetch from database (child span)
            with tracer.start_as_current_span("user_workflow.fetch_from_db") as fetch_span:
                fetch_span.set_attribute("apm.step", "fetch_from_db")
                fetch_span.set_attribute("db.operation", "SELECT")
                fetch_span.set_attribute("db.table", "users")
                fetch_span.add_event("Fetching users from database")

                users = User.get_all()
                fetch_span.set_attribute("db.result_count", len(users))
                fetch_span.set_attribute("apm.result_count", len(users))
                fetch_span.add_event("Database fetch completed", {
                    "user_count": len(users)
                })

            # Step 2: Enrich data (child span)
            with tracer.start_as_current_span("user_workflow.enrich_data") as enrich_span:
                enrich_span.set_attribute("apm.step", "enrich_data")
                enrich_span.set_attribute("enrichment.type", "user_data")
                enrich_span.add_event("Starting data enrichment")

                enriched_users = []
                for user in users:
                    enriched_user = dict(user)
                    # Add computed fields
                    enriched_user['full_name'] = f"{user['first_name']} {user['last_name']}"
                    enriched_user['has_phone'] = user['phone'] is not None
                    enriched_user['has_address'] = user['address'] is not None
                    enriched_users.append(enriched_user)

                enrich_span.set_attribute("enrichment.fields_added", 3)
                enrich_span.set_attribute("apm.enriched_count", len(enriched_users))
                enrich_span.add_event("Data enrichment completed")

            # Step 3: Calculate statistics (child span)
            with tracer.start_as_current_span("user_workflow.calculate_stats") as stats_span:
                stats_span.set_attribute("apm.step", "calculate_stats")
                stats_span.set_attribute("stats.type", "user_statistics")

                total_users = len(enriched_users)
                users_with_phone = sum(1 for u in enriched_users if u['has_phone'])
                users_with_address = sum(1 for u in enriched_users if u['has_address'])
                avg_age = sum(u['age'] for u in enriched_users if u['age']) / total_users if total_users > 0 else 0

                stats_span.set_attribute("stats.total_users", total_users)
                stats_span.set_attribute("stats.users_with_phone", users_with_phone)
                stats_span.set_attribute("stats.users_with_address", users_with_address)
                stats_span.set_attribute("stats.average_age", round(avg_age, 2))
                stats_span.set_attribute("apm.total_users", total_users)
                stats_span.add_event("Statistics calculated")

            # Add final workflow attributes
            workflow_span.set_attribute("workflow.steps_completed", 3)
            workflow_span.set_attribute("workflow.result_count", len(enriched_users))
            workflow_span.set_attribute("apm.result", "success")
            workflow_span.set_attribute("apm.result_count", len(enriched_users))
            workflow_span.add_event("Workflow completed successfully")

            return {
                "users": enriched_users,
                "stats": {
                    "total": total_users,
                    "with_phone": users_with_phone,
                    "with_address": users_with_address,
                    "average_age": round(avg_age, 2)
                }
            }

    def get_user_with_validation(self, username):
        """
        Get user with multi-step validation workflow

        Creates custom span hierarchy:
        - Parent: user_workflow.get_user_validated
          - Child: user_workflow.validate_input
          - Child: user_workflow.fetch_user
          - Child: user_workflow.validate_result
        """
        with tracer.start_as_current_span("user_workflow.get_user_validated") as workflow_span:
            workflow_span.set_attribute("apm.service", self.service_name)
            workflow_span.set_attribute("apm.operation", "get_user_validated")
            workflow_span.set_attribute("apm.username_requested", username)
            workflow_span.set_attribute("workflow.type", "get_user_validated")
            workflow_span.set_attribute("workflow.username", username)
            workflow_span.add_event("Starting validated user retrieval")

            # Step 1: Validate input
            with tracer.start_as_current_span("user_workflow.validate_input") as validate_span:
                validate_span.set_attribute("apm.step", "validate_input")
                validate_span.set_attribute("validation.field", "username")
                validate_span.set_attribute("validation.value", username)

                is_valid = len(username) >= 3 and username.replace('_', '').isalnum()
                validate_span.set_attribute("validation.result", is_valid)

                if not is_valid:
                    validate_span.set_attribute("validation.error", "Invalid username format")
                    validate_span.add_event("Validation failed")
                    workflow_span.set_attribute("workflow.result", "validation_failed")
                    return None

                validate_span.add_event("Validation passed")

            # Step 2: Fetch user
            with tracer.start_as_current_span("user_workflow.fetch_user") as fetch_span:
                fetch_span.set_attribute("apm.step", "fetch_user")
                fetch_span.set_attribute("db.operation", "SELECT")
                fetch_span.set_attribute("db.table", "users")
                fetch_span.set_attribute("db.where", f"username = {username}")

                user = User.get_by_username(username)
                fetch_span.set_attribute("db.found", user is not None)
                fetch_span.set_attribute("apm.user_found", user is not None)

            # Step 3: Validate result
            with tracer.start_as_current_span("user_workflow.validate_result") as result_span:
                result_span.set_attribute("apm.step", "validate_result")
                if user is None:
                    result_span.set_attribute("validation.result", "user_not_found")
                    result_span.set_attribute("apm.result", "not_found")
                    result_span.add_event("User not found in database")
                    workflow_span.set_attribute("workflow.result", "not_found")
                    workflow_span.set_attribute("apm.result", "not_found")
                    return None

                result_span.set_attribute("validation.result", "success")
                result_span.set_attribute("user.email", user['email'])
                result_span.set_attribute("apm.result", "success")
                result_span.add_event("User found and validated")

            workflow_span.set_attribute("workflow.result", "success")
            workflow_span.set_attribute("apm.result", "success")
            workflow_span.add_event("Workflow completed successfully")
            return user

    def create_user_with_workflow(self, data):
        """
        Create user with complex validation and processing workflow

        Creates custom span hierarchy:
        - Parent: user_workflow.create_user
          - Child: user_workflow.validate_required_fields
          - Child: user_workflow.validate_data_types
          - Child: user_workflow.enrich_user_data
          - Child: user_workflow.persist_to_db
          - Child: user_workflow.post_creation_tasks
        """
        with tracer.start_as_current_span("user_workflow.create_user") as workflow_span:
            workflow_span.set_attribute("apm.service", self.service_name)
            workflow_span.set_attribute("apm.operation", "create_user")
            workflow_span.set_attribute("apm.username_requested", data.get('username', 'unknown'))
            workflow_span.set_attribute("workflow.type", "create_user")
            workflow_span.set_attribute("workflow.service", self.service_name)
            workflow_span.add_event("User creation workflow started")

            # Step 1: Validate required fields
            with tracer.start_as_current_span("user_workflow.validate_required_fields") as validate_span:
                validate_span.set_attribute("apm.step", "validate_required_fields")
                required_fields = ['username', 'email', 'first_name', 'last_name']
                validate_span.set_attribute("validation.required_fields", json.dumps(required_fields))

                missing_fields = [f for f in required_fields if f not in data]
                validate_span.set_attribute("validation.missing_count", len(missing_fields))
                validate_span.set_attribute("apm.validation_passed", len(missing_fields) == 0)

                if missing_fields:
                    validate_span.set_attribute("validation.result", "failed")
                    validate_span.set_attribute("validation.missing_fields", json.dumps(missing_fields))
                    validate_span.add_event("Required field validation failed")
                    workflow_span.set_attribute("workflow.result", "validation_failed")
                    return None, f"Missing required fields: {', '.join(missing_fields)}"

                validate_span.set_attribute("validation.result", "passed")
                validate_span.add_event("Required fields validated")

            # Step 2: Validate data types
            with tracer.start_as_current_span("user_workflow.validate_data_types") as type_span:
                type_span.set_attribute("apm.step", "validate_data_types")
                type_span.set_attribute("validation.type", "data_types")

                validation_errors = []
                if 'age' in data and data['age'] is not None:
                    if not isinstance(data['age'], int) or data['age'] < 0 or data['age'] > 150:
                        validation_errors.append("Invalid age")

                if '@' not in data.get('email', ''):
                    validation_errors.append("Invalid email format")

                type_span.set_attribute("validation.error_count", len(validation_errors))
                type_span.set_attribute("apm.validation_passed", len(validation_errors) == 0)

                if validation_errors:
                    type_span.set_attribute("validation.result", "failed")
                    type_span.set_attribute("validation.errors", json.dumps(validation_errors))
                    type_span.set_attribute("apm.result", "validation_failed")
                    type_span.add_event("Data type validation failed")
                    workflow_span.set_attribute("workflow.result", "validation_failed")
                    workflow_span.set_attribute("apm.result", "validation_failed")
                    return None, f"Validation errors: {', '.join(validation_errors)}"

                type_span.set_attribute("validation.result", "passed")
                type_span.set_attribute("apm.result", "success")
                type_span.add_event("Data types validated")

            # Step 3: Enrich user data
            with tracer.start_as_current_span("user_workflow.enrich_user_data") as enrich_span:
                enrich_span.set_attribute("apm.step", "enrich_user_data")
                enrich_span.set_attribute("enrichment.type", "user_creation")

                # Add computed fields for tracking
                full_name = f"{data['first_name']} {data['last_name']}"
                enrich_span.set_attribute("enrichment.full_name", full_name)
                enrich_span.set_attribute("enrichment.has_optional_fields",
                                        'age' in data or 'phone' in data or 'address' in data)
                enrich_span.set_attribute("apm.full_name", full_name)
                enrich_span.add_event("User data enriched")

            # Step 4: Persist to database
            with tracer.start_as_current_span("user_workflow.persist_to_db") as persist_span:
                persist_span.set_attribute("apm.step", "persist_to_db")
                persist_span.set_attribute("db.operation", "INSERT")
                persist_span.set_attribute("db.table", "users")
                persist_span.set_attribute("db.username", data['username'])
                persist_span.add_event("Persisting user to database")

                username, error = User.create(data)

                if error:
                    persist_span.set_attribute("db.result", "failed")
                    persist_span.set_attribute("db.error", error)
                    persist_span.set_attribute("apm.result", "db_error")
                    persist_span.add_event("Database persistence failed")
                    workflow_span.set_attribute("workflow.result", "db_error")
                    workflow_span.set_attribute("apm.result", "db_error")
                    return None, error

                persist_span.set_attribute("db.result", "success")
                persist_span.set_attribute("db.created_username", username)
                persist_span.set_attribute("apm.result", "success")
                persist_span.set_attribute("apm.username_created", username)
                persist_span.add_event("User persisted successfully")

            # Step 5: Post-creation tasks
            with tracer.start_as_current_span("user_workflow.post_creation_tasks") as post_span:
                post_span.set_attribute("apm.step", "post_creation_tasks")
                post_span.set_attribute("task.type", "post_creation")
                post_span.add_event("Running post-creation tasks")

                # Simulate post-creation tasks (e.g., send welcome email, log audit)
                post_span.set_attribute("task.audit_logged", True)
                post_span.set_attribute("task.notification_queued", True)
                post_span.set_attribute("apm.result", "success")
                post_span.add_event("Post-creation tasks completed")

            # Workflow completion
            workflow_span.set_attribute("workflow.result", "success")
            workflow_span.set_attribute("workflow.created_username", username)
            workflow_span.set_attribute("workflow.steps_completed", 5)
            workflow_span.set_attribute("apm.result", "success")
            workflow_span.set_attribute("apm.username_created", username)
            workflow_span.add_event("User creation workflow completed successfully")

            return username, None

    def update_user_with_workflow(self, username, data):
        """
        Update user with validation and change tracking workflow

        Creates custom span hierarchy:
        - Parent: user_workflow.update_user
          - Child: user_workflow.fetch_existing
          - Child: user_workflow.detect_changes
          - Child: user_workflow.validate_changes
          - Child: user_workflow.apply_updates
          - Child: user_workflow.audit_changes
        """
        with tracer.start_as_current_span("user_workflow.update_user") as workflow_span:
            workflow_span.set_attribute("apm.service", self.service_name)
            workflow_span.set_attribute("apm.operation", "update_user")
            workflow_span.set_attribute("apm.username_requested", username)
            workflow_span.set_attribute("workflow.type", "update_user")
            workflow_span.set_attribute("workflow.username", username)
            workflow_span.add_event("User update workflow started")

            # Step 1: Fetch existing user
            with tracer.start_as_current_span("user_workflow.fetch_existing") as fetch_span:
                fetch_span.set_attribute("apm.step", "fetch_existing")
                fetch_span.set_attribute("db.operation", "SELECT")
                fetch_span.set_attribute("db.table", "users")

                existing_user = User.get_by_username(username)

                if existing_user is None:
                    fetch_span.set_attribute("db.found", False)
                    fetch_span.set_attribute("apm.user_found", False)
                    fetch_span.set_attribute("apm.result", "not_found")
                    fetch_span.add_event("User not found")
                    workflow_span.set_attribute("workflow.result", "not_found")
                    workflow_span.set_attribute("apm.result", "not_found")
                    return False, "User not found"

                fetch_span.set_attribute("db.found", True)
                fetch_span.set_attribute("apm.user_found", True)
                fetch_span.add_event("Existing user fetched")

            # Step 2: Detect changes
            with tracer.start_as_current_span("user_workflow.detect_changes") as detect_span:
                detect_span.set_attribute("apm.step", "detect_changes")
                detect_span.set_attribute("change_detection.type", "field_comparison")

                changes = []
                for field in data.keys():
                    if field in existing_user and existing_user[field] != data[field]:
                        changes.append(field)

                detect_span.set_attribute("change_detection.fields_changed", len(changes))
                detect_span.set_attribute("change_detection.changed_fields", json.dumps(changes))
                detect_span.set_attribute("apm.fields_changed", len(changes))
                detect_span.add_event("Changes detected", {"changed_fields": changes})

                if not changes:
                    detect_span.set_attribute("apm.result", "no_changes")
                    detect_span.add_event("No changes detected")
                    workflow_span.set_attribute("workflow.result", "no_changes")
                    workflow_span.set_attribute("apm.result", "no_changes")
                    return False, "No fields to update"

            # Step 3: Validate changes
            with tracer.start_as_current_span("user_workflow.validate_changes") as validate_span:
                validate_span.set_attribute("apm.step", "validate_changes")
                validate_span.set_attribute("validation.type", "update_validation")

                if 'age' in data and data['age'] is not None:
                    if not isinstance(data['age'], int) or data['age'] < 0:
                        validate_span.set_attribute("validation.result", "failed")
                        validate_span.set_attribute("apm.validation_passed", False)
                        validate_span.set_attribute("apm.result", "validation_failed")
                        validate_span.add_event("Age validation failed")
                        workflow_span.set_attribute("workflow.result", "validation_failed")
                        workflow_span.set_attribute("apm.result", "validation_failed")
                        return False, "Invalid age value"

                validate_span.set_attribute("validation.result", "passed")
                validate_span.set_attribute("apm.validation_passed", True)
                validate_span.add_event("Changes validated")

            # Step 4: Apply updates
            with tracer.start_as_current_span("user_workflow.apply_updates") as update_span:
                update_span.set_attribute("apm.step", "apply_updates")
                update_span.set_attribute("db.operation", "UPDATE")
                update_span.set_attribute("db.table", "users")
                update_span.set_attribute("db.fields_updated", len(changes))

                success, error = User.update(username, data)

                if error:
                    update_span.set_attribute("db.result", "failed")
                    update_span.set_attribute("apm.result", "db_error")
                    update_span.add_event("Update failed")
                    workflow_span.set_attribute("workflow.result", "db_error")
                    workflow_span.set_attribute("apm.result", "db_error")
                    return False, error

                update_span.set_attribute("db.result", "success")
                update_span.set_attribute("apm.result", "success")
                update_span.add_event("Updates applied successfully")

            # Step 5: Audit changes
            with tracer.start_as_current_span("user_workflow.audit_changes") as audit_span:
                audit_span.set_attribute("apm.step", "audit_changes")
                audit_span.set_attribute("audit.type", "user_update")
                audit_span.set_attribute("audit.username", username)
                audit_span.set_attribute("audit.fields_changed", json.dumps(changes))
                audit_span.set_attribute("apm.audit_logged", True)
                audit_span.add_event("Audit trail created")

            workflow_span.set_attribute("workflow.result", "success")
            workflow_span.set_attribute("workflow.steps_completed", 5)
            workflow_span.set_attribute("apm.result", "success")
            workflow_span.add_event("User update workflow completed successfully")

            return True, None

    def delete_user_with_workflow(self, username):
        """
        Delete user with validation and cleanup workflow

        Creates custom span hierarchy:
        - Parent: user_workflow.delete_user
          - Child: user_workflow.validate_deletion
          - Child: user_workflow.backup_user_data
          - Child: user_workflow.delete_from_db
          - Child: user_workflow.cleanup_tasks
        """
        with tracer.start_as_current_span("user_workflow.delete_user") as workflow_span:
            workflow_span.set_attribute("apm.service", self.service_name)
            workflow_span.set_attribute("apm.operation", "delete_user")
            workflow_span.set_attribute("apm.username_requested", username)
            workflow_span.set_attribute("workflow.type", "delete_user")
            workflow_span.set_attribute("workflow.username", username)
            workflow_span.add_event("User deletion workflow started")

            # Step 1: Validate deletion
            with tracer.start_as_current_span("user_workflow.validate_deletion") as validate_span:
                validate_span.set_attribute("apm.step", "validate_deletion")
                validate_span.set_attribute("validation.type", "deletion_check")

                user = User.get_by_username(username)

                if user is None:
                    validate_span.set_attribute("validation.result", "user_not_found")
                    validate_span.set_attribute("apm.user_found", False)
                    validate_span.set_attribute("apm.result", "not_found")
                    validate_span.add_event("User not found")
                    workflow_span.set_attribute("workflow.result", "not_found")
                    workflow_span.set_attribute("apm.result", "not_found")
                    return False, "User not found"

                validate_span.set_attribute("validation.result", "passed")
                validate_span.set_attribute("validation.user_email", user['email'])
                validate_span.set_attribute("apm.user_found", True)
                validate_span.add_event("Deletion validated")

            # Step 2: Backup user data
            with tracer.start_as_current_span("user_workflow.backup_user_data") as backup_span:
                backup_span.set_attribute("apm.step", "backup_user_data")
                backup_span.set_attribute("backup.type", "user_deletion")
                backup_span.set_attribute("backup.username", username)
                backup_span.set_attribute("backup.data", json.dumps(dict(user)))
                backup_span.set_attribute("apm.backup_created", True)
                backup_span.add_event("User data backed up")

            # Step 3: Delete from database
            with tracer.start_as_current_span("user_workflow.delete_from_db") as delete_span:
                delete_span.set_attribute("apm.step", "delete_from_db")
                delete_span.set_attribute("db.operation", "DELETE")
                delete_span.set_attribute("db.table", "users")
                delete_span.set_attribute("db.username", username)

                success, error = User.delete(username)

                if error:
                    delete_span.set_attribute("db.result", "failed")
                    delete_span.set_attribute("apm.result", "db_error")
                    delete_span.add_event("Deletion failed")
                    workflow_span.set_attribute("workflow.result", "db_error")
                    workflow_span.set_attribute("apm.result", "db_error")
                    return False, error

                delete_span.set_attribute("db.result", "success")
                delete_span.set_attribute("apm.result", "success")
                delete_span.add_event("User deleted from database")

            # Step 4: Cleanup tasks
            with tracer.start_as_current_span("user_workflow.cleanup_tasks") as cleanup_span:
                cleanup_span.set_attribute("apm.step", "cleanup_tasks")
                cleanup_span.set_attribute("cleanup.type", "post_deletion")
                cleanup_span.set_attribute("cleanup.audit_logged", True)
                cleanup_span.set_attribute("cleanup.cache_cleared", True)
                cleanup_span.set_attribute("apm.cleanup_completed", True)
                cleanup_span.add_event("Cleanup tasks completed")

            workflow_span.set_attribute("workflow.result", "success")
            workflow_span.set_attribute("workflow.steps_completed", 4)
            workflow_span.set_attribute("apm.result", "success")
            workflow_span.add_event("User deletion workflow completed successfully")

            return True, None
