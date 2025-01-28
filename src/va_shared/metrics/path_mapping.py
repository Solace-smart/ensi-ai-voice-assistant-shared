from enum import Enum
from typing import Dict, Optional


class PathNode:
    AUTOMATION = {"automation": 0, "not_automation": 1}
    GENERAL_DOMAIN = {
        "home_related": 0,
        "web_search": 1,
        "general_conversation": 2,
        "music_player": 3,
        "time_related": 4,
    }
    TOOL = {"execute": 0, "get_info": 1, "get_history": 2}
    TIME_DEVICE = {
        "calendar": 0,
        "timer": 1,
        "stopwatch": 1,
        "alarm": 1,
    }


class LeafPathTracker:
    """Tracks the unique path through the decision tree using a compact numeric representation"""

    def __init__(self):
        self._path = ""

    def add_decision(self, decision_type: str, value: str) -> None:
        """Add a decision to the path using predefined mappings"""
        if decision_type == "automation":
            self._path += str(1 if value else 0)
        elif decision_type == "general_domain":
            self._path += str(PathNode.GENERAL_DOMAIN.get(value, "x"))
        elif decision_type == "tool":
            self._path += str(PathNode.TOOL.get(value, "x"))
        elif decision_type == "time_device":
            self._path += str(PathNode.TIME_DEVICE.get(value, "x"))

    @property
    def leaf_id(self) -> str:
        """Get the unique leaf identifier"""
        return self._path
