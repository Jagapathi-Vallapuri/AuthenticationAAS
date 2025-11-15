import enum

class AuditAction(enum.Enum):
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    PASSWORD_RESET_REQUEST = "password_reset_request"
    PASSWORD_RESET_SUCCESS = "password_reset_success"
    TOKEN_REFRESHED = "token_refreshed"
    ROLE_ASSIGNED = "role_assigned"
    ROLE_REMOVED = "role_removed"
    USER_REGISTERED = 'user_registered'
    USER_UPDATED = 'user_updated'
    LOGOUT = 'logout'
    LOGOUT_ALL_SESSIONS = 'logout_all_sessions'
