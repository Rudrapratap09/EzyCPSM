"""
finding_utils.py
Utility helpers for findings
"""

import json
from ..core.logging_config import logger


def get_property(resource, key, default=None):
    """
    Safely retrieve nested or flat properties from a resource.

    Supports:
    - dict
    - JSON string
    - dot notation (e.g. "Configuration.State")
    """

    props = {}

    if hasattr(resource, "properties"):
        if isinstance(resource.properties, dict):
            props = resource.properties
        elif isinstance(resource.properties, str):
            try:
                props = json.loads(resource.properties)
            except json.JSONDecodeError:
                logger.debug(f"Invalid JSON properties for {resource.resource_id}")
                return default

    # Traverse dot-notation path
    current = props
    for part in key.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return default

    return current
