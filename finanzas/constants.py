"""
Constants used throughout the Finanzas application.
Centralizes magic numbers and strings for better maintainability.
"""

# Budget Alert Thresholds (percentage)
BUDGET_WARNING_THRESHOLD = 80  # Show warning when 80% of budget is used
BUDGET_CRITICAL_THRESHOLD = 95  # Critical alert when 95% used

# Debt Capacity
DEFAULT_DEBT_CAPACITY_PERCENTAGE = 0.35  # 35% of net income

# Pagination Settings
DEFAULT_PAGE_SIZE = 20
TRANSACTIONS_PAGE_SIZE = 50
DASHBOARD_RECENT_TRANSACTIONS = 10
DASHBOARD_MAX_SIMULATIONS = 5
DASHBOARD_MAX_RECOMMENDATIONS = 3

# Cache Timeouts (seconds)
CACHE_SHORT = 300  # 5 minutes
CACHE_MEDIUM = 1800  # 30 minutes
CACHE_LONG = 3600  # 1 hour
CACHE_DASHBOARD = 600  # 10 minutes
CACHE_ACCOUNT_SUMMARY = 600  # 10 minutes

# Query Optimization
MAX_RELATED_OBJECTS = 100  # Limit for related objects to prevent memory issues

# Credit Score Range
MIN_CREDIT_SCORE = 300
MAX_CREDIT_SCORE = 850

# Interest Rate Limits
MIN_INTEREST_RATE = 0
MAX_INTEREST_RATE = 100

# Financial Limits
MIN_AMOUNT = 0.01
MAX_DECIMAL_PLACES = 2
MAX_DIGITS = 12

# Session Configuration
DEFAULT_SESSION_TIMEOUT = 86400  # 24 hours

# API Rate Limiting
API_RATE_LIMIT_PER_HOUR = 1000
API_RATE_LIMIT_PER_MINUTE = 60

# File Upload
MAX_RECEIPT_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_RECEIPT_FORMATS = ['jpg', 'jpeg', 'png', 'pdf']

# Date Ranges
DEFAULT_REPORT_DAYS = 30
MAX_REPORT_DAYS = 365

# Notifications
MAX_NOTIFICATIONS = 10
