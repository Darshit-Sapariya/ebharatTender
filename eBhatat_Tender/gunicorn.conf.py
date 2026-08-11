import os

# Gunicorn configuration file for eBharatTender on Render
bind = "0.0.0.0:" + os.environ.get("PORT", "8000")

# Worker timeout configuration (seconds)
# Increases timeout from 30s default to 120s to prevent SIGKILL timeouts on slow network calls
timeout = 120
graceful_timeout = 30
keepalive = 5

# Worker processes
workers = int(os.environ.get("WEB_CONCURRENCY", 2))
threads = 2

# Logging
loglevel = os.environ.get("LOG_LEVEL", "info")
accesslog = "-"
errorlog = "-"
