# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2024-2026 James Ray Hawkins
#
# Licensed under the Apache License, Version 2.0 (see LICENSE file).

"""
COG Serializers — JSON encoding for KOMPOSOS types.
"""

from datetime import datetime
from enum import Enum
from typing import Any

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


def cog_json_default(obj: Any) -> Any:
    """Default JSON serializer for COG types."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, set):
        return list(obj)
    if HAS_NUMPY:
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.floating, np.complexfloating)):
            return float(obj)
        if isinstance(obj, np.integer):
            return int(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
