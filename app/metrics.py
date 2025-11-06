"""Basic metrics collection for monitoring."""

from collections import defaultdict
from typing import Dict
from fastapi import APIRouter

router = APIRouter(tags=["Monitoring"])

# In-memory metrics storage (for production, use Redis or similar)
_metrics: Dict[str, int] = defaultdict(int)
_request_durations: Dict[str, list] = defaultdict(list)


class MetricsCollector:
    """Simple metrics collector."""

    @staticmethod
    def increment(metric_name: str, value: int = 1):
        """Increment a counter metric."""
        _metrics[metric_name] += value

    @staticmethod
    def record_duration(metric_name: str, duration: float):
        """Record a duration metric."""
        _request_durations[metric_name].append(duration)
        # Keep only last 1000 measurements to avoid memory issues
        if len(_request_durations[metric_name]) > 1000:
            _request_durations[metric_name] = _request_durations[metric_name][-1000:]

    @staticmethod
    def get_metrics() -> Dict:
        """Get all metrics."""
        metrics = dict(_metrics)

        # Calculate averages for durations
        durations = {}
        for key, values in _request_durations.items():
            if values:
                durations[f"{key}_avg"] = sum(values) / len(values)
                durations[f"{key}_count"] = len(values)

        return {
            "counters": metrics,
            "durations": durations,
        }


# Convenience instances
metrics = MetricsCollector()


@router.get("/metrics")
async def get_metrics():
    """
    Get application metrics.

    Returns counters and performance metrics for monitoring.
    """
    return metrics.get_metrics()


# Helper function to record request metrics
def record_request_metrics(
    method: str, endpoint: str, status_code: int, duration: float
):
    """Record HTTP request metrics."""
    metrics.increment(f"http_requests_total_{status_code}")
    metrics.increment(f"http_requests_{method}_{endpoint}")
    metrics.record_duration(f"http_request_duration_{method}_{endpoint}", duration)
