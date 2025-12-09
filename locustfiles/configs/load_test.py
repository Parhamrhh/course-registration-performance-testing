"""
Load test configuration (normal expected load).
"""

CONFIG = {
    "users": 100,
    "spawn_rate": 10,
    "run_time": "10m",
    "host": "http://api:8500",
    "class_picker": "StudentUser:1",
    "description": "Normal expected load with baseline mix.",
}

