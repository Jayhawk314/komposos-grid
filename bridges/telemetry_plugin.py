from __future__ import annotations

from collections import Counter, defaultdict


class TelemetryPlugin:
    """Minimal telemetry collector expected by copied Ruliad tests."""

    def __init__(self, core=None, category=None):
        self.core = core
        self.category = category
        self.co_occurrence = Counter()
        self.error_log = []

    def co_occurrence_matrix(self):
        matrix = defaultdict(dict)
        for (left, right), count in self.co_occurrence.items():
            matrix[left][right] = count
            matrix[right][left] = count
        return dict(matrix)

    def error_boundaries(self):
        counts = Counter(str(item.get("source_plugin", "unknown")) for item in self.error_log)
        return [
            {"plugin": plugin, "error_count": count}
            for plugin, count in counts.most_common()
        ]

