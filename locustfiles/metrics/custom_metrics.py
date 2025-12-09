"""
Custom metrics collection for Locust performance tests.

Collects p95/p99 latency, throughput (RPS), and error rates
at test end, logging them for later analysis.
"""

from __future__ import annotations

from typing import Dict, Any
from locust import events
from locust.env import Environment
from statistics import quantiles


def _compute_percentiles(values: list[float]) -> tuple[float, float]:
    """
    Compute p95 and p99 for a list of response times.
    """
    if not values:
        return 0.0, 0.0
    # statistics.quantiles with n=100 gives percentile cut points
    q = quantiles(values, n=100)
    # p95 is index 94, p99 is index 98 (0-based)
    p95 = q[94]
    p99 = q[98]
    return p95, p99


def _aggregate_stats(env: Environment) -> Dict[str, Any]:
    """
    Aggregate stats from Locust Environment.
    """
    stats = env.stats
    total = stats.total

    response_times = []
    for entry in stats.entries.values():
        response_times.extend([entry.avg_response_time] * entry.num_requests)

    p95, p99 = _compute_percentiles(response_times)

    # Throughput (requests per second)
    rps = total.total_rps

    # Error rate
    total_requests = total.num_requests
    total_failures = total.num_failures
    error_rate = (total_failures / total_requests) * 100 if total_requests else 0.0

    return {
        "p95_ms": round(p95, 2),
        "p99_ms": round(p99, 2),
        "rps": round(rps, 2),
        "error_rate_pct": round(error_rate, 2),
        "requests": total_requests,
        "failures": total_failures,
    }


@events.test_stop.add_listener
def on_test_stop(environment: Environment, **_kwargs):
    """
    Hook executed when a Locust test stops. Logs aggregated metrics.
    """
    metrics = _aggregate_stats(environment)
    environment.logger.info("Custom Metrics Summary: %s", metrics)

