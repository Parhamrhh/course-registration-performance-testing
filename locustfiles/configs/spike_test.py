"""
Spike test configuration (sudden traffic spikes).
"""

CONFIG = {
    "users": 200,
    "spawn_rate": 200,  # rapid spike
    "run_time": "5m",
    "host": "http://api:8500",
    "class_picker": "StudentUser:1",
    "description": "Sudden spike to observe system response to abrupt load.",
}

