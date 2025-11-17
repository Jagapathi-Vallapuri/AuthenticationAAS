import enum

class AuditAction(enum.Enum):
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    PASSWORD_RESET_REQUEST = "password_reset_request"
    PASSWORD_RESET_SUCCESS = "password_reset_success"
    TOKEN_REFRESHED = "token_refreshed"
    ROLE_ASSIGNED = "role_assigned"
    ROLE_REMOVED = "role_removed"
    ROLE_CREATED = "role_created"
    ROLE_DELETED = "role_deleted"
    USER_REGISTERED = 'user_registered'
    PERMISSION_CREATED = 'permission_created'
    PERMISSION_ASSIGNED = 'permission_assigned'
    PERMISSION_REMOVED = 'permission_removed'
    USER_UPDATED = 'user_updated'
    LOGOUT = 'logout'
    LOGOUT_ALL_SESSIONS = 'logout_all_sessions'
    SESSION_REVOKED = 'session_revoked'
    SESSION_FORCE_REVOKED = 'session_force_revoked'
    ALL_SESSIONS_REVOKED = 'all_sessions_revoked'
