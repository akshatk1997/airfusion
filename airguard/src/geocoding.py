"""
Geocoding module for AirGuard — My Safe Outdoor Plan.
Resolves human-readable city names, states, and coordinates via Open-Meteo Geocoding API,
local SQLite database, and built-in preset hubs.
"""

from __future__ import annotations

import logging
from typing import Dict, Any, Optional

# Re-export geocode_city from data_collection to provide clean modular access
from src.data_collection import geocode_city

logger = logging.getLogger("airguard.geocoding")

__all__ = ["geocode_city"]
