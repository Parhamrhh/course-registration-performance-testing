"""
Soak test configuration (sustained load over time).
"""

CONFIG = {
    "users": 80,
    "spawn_rate": 5,
    "run_time": "60m",
    "host": "http://api:8500",
    "class_picker": "StudentUser:1",
    "description": "Sustained load to observe resource leaks and long-running stability.",
}

