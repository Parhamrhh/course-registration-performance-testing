"""
Stress test configuration (beyond normal capacity).
"""

CONFIG = {
    "users": 300,
    "spawn_rate": 30,
    "run_time": "15m",
    "host": "http://api:8500",
    "class_picker": "StudentUser:1",
    "description": "Push system beyond expected capacity to find breaking points.",
}

