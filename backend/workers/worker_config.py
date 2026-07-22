# Celery settings configuration
task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]
timezone = "UTC"
enable_utc = True

# Fail-safe settings to prevent hung tasks
task_time_limit = 300
task_soft_time_limit = 120
