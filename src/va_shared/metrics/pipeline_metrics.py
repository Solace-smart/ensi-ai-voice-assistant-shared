from dataclasses import dataclass
from datetime import datetime
import time
import traceback
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from .path_mapping import PathNode


class StepMetrics(BaseModel):
    """Metrics for a single pipeline step"""
    state: str
    start_time: float
    end_time: float
    result: dict[str, Any] | None = None
    error: str | None = None
    error_traceback: str | None = None  # Added field for traceback

    @staticmethod
    def from_json(data: Dict[str, Any]) -> "StepMetrics":
        """Create instance from JSON dict."""
        return StepMetrics(**data)

    @property
    def duration(self) -> float:
        """Calculate step duration."""
        return self.end_time - self.start_time

    @property
    def status(self) -> str:
        """Get step status."""
        return "FAILED" if self.error else "SUCCESS"


class PipelineMetrics(BaseModel):
    query: Optional[str] = None
    start_time: Optional[float] = time.time()
    steps: Optional[List[StepMetrics]] = []
    end_time: Optional[float] = None
    failed: Optional[bool] = None
    error: Optional[str] = None
    summary: Optional[str] = None
    _path: Optional[str] = ""  # Initialize path tracking

    @staticmethod
    def from_json(json_str: str):
        metrics = PipelineMetrics(json_str["query"])
        metrics.start_time = json_str["start_time"]
        metrics.steps = [StepMetrics.from_json(
            step) for step in json_str["steps"]]
        metrics.end_time = json_str["end_time"]
        metrics.failed = json_str["failed"]
        metrics.error = json_str.get("error", None)
        metrics._path = json_str.get("path", "")
        return metrics

    def start_step(self, state: str) -> float:
        """Start timing a new step"""
        return time.time()

    def add_step(
        self, state: str, result: Dict, start_time: float, end_time: float, error: Exception | None = None
    ):
        """Add a completed step with its timing and error details if any."""
        error_str = None
        error_traceback = None

        if error:
            error_str = str(error)
            error_traceback = ''.join(traceback.format_exception(
                type(error), error, error.__traceback__))

            # Also store at pipeline level
            self.failed = True
            self.error = error_str

        step = StepMetrics(
            state=state,
            start_time=start_time,
            end_time=end_time,
            result=result,
            error=error_str,
            error_traceback=error_traceback
        )
        self.steps.append(step)

        # Update path based on the step result
        self._update_path(state, result)

    def _update_path(self, state: str, result: Dict):
        """Update path based on the step result"""
        if state == "all_classification":
            value = "automation" if result.get(
                "is_automation") else "not_automation"
            self._path += str(PathNode.AUTOMATION.get(value, "x"))

            value = result.get("general_domain")
            self._path += str(PathNode.GENERAL_DOMAIN.get(value, "x"))

            value = result.get("tool")
            self._path += str(PathNode.TOOL.get(value, "x"))

            # value = result.get("time_related_device")
            # self._path += str(PathNode.TIME_DEVICE.get(value, "x"))

            print(f"All classification path: {self._path}")

        # elif state == "automation_classification":
        #     value = "automation" if result.get(
        #         "is_automation") else "not_automation"
        #     self._path += str(PathNode.AUTOMATION.get(value, "x"))
        # elif state == "general_domain_classification":
        #     value = result.get("general_domain")
        #     self._path += str(PathNode.GENERAL_DOMAIN.get(value, "x"))
        # elif state == "tool_selection":
        #     value = result.get("tool")
        #     self._path += str(PathNode.TOOL.get(value, "x"))
        # elif state == "time_related_selection":
        #     value = result.get("time_related_device")
        #     self._path += str(PathNode.TIME_DEVICE.get(value, "x"))

    @property
    def leaf_id(self) -> str:
        """Get the current leaf path ID"""
        return self._path

    @leaf_id.setter
    def leaf_id(self, value: str):
        """Set the leaf path ID"""
        self._path = value

    def start_process(self):
        self.start_time = time.time()

    def finish_process(self):
        self.end_time = time.time()

    @property
    def total_duration(self) -> float:
        """Calculate total duration, ensuring end_time is set and not in the future"""
        if self.end_time is None:
            self.finish_process()
        # Ensure we don't get negative duration if timestamps are mismatched
        return max(0.0, self.end_time - self.start_time)

    def get_summary(self) -> str:
        """Get a formatted summary of the pipeline execution."""
        summary = [
            "\n=== Pipeline Execution Summary ===",
            f"Query: {self.query}",
            f"Started at: {datetime.fromtimestamp(self.start_time).strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total duration: {self.total_duration:.2f}s",
            f"Final Path ID: {self.leaf_id}",
            f"Status: {'FAILED' if self.failed else 'SUCCESS'}",
            "\nExecution path:",
        ]

        for i, step in enumerate(self.steps, 1):
            summary.append(
                f"{i}. {step.state} ({step.duration:.3f}s) - {step.status}")
            if step.error:
                summary.append(f"   ❌ Error: {step.error}")
                if step.error_traceback:
                    summary.append(f"   ❌ Traceback:\n{step.error_traceback}")
            else:
                for key, value in (step.result or {}).items():
                    summary.append(f"   └─ {key}: {value}")

        if self.failed:
            summary.append("\n=== Pipeline Failed ===")
            summary.append(f"Final Error: {self.error}")

        else:
            summary.append("\n=== Pipeline Completed Successfully ===")

        return "\n".join(summary)
