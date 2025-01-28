from dataclasses import dataclass
from typing import List, Dict, Optional, Any
import time
from datetime import datetime
import traceback
from .path_mapping import PathNode
from pydantic import BaseModel


@dataclass
class StepMetrics:
    state: str
    start_time: float
    end_time: float
    result: Dict
    error: Optional[Exception] = None

    @staticmethod
    def from_json(json_str: str):
        return StepMetrics(
            json_str["state"],
            json_str.get("start_time", 0),
            json_str.get("end_time", 0),
            json_str.get("result", {}),
            json_str.get("error", None),
        )

    @property
    def duration(self) -> float:
        return self.end_time - self.start_time

    @property
    def status(self) -> str:
        return "FAILED" if self.error else "SUCCESS"


class PipelineMetrics(BaseModel):
    query: str
    start_time: Optional[float] = None
    steps: Optional[List[StepMetrics]] = None
    end_time: Optional[float] = None
    failed: Optional[bool] = None
    error: Optional[Exception] = None
    _path: Optional[str] = None  # Initialize path tracking

    @staticmethod
    def from_json(json_str: Dict[str, Any]):
        metrics = CloudPipelineMetrics(json_str["query"])
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
        self, state: str, result: Dict, start_time: float, error: Exception = None
    ):
        """Add a completed step with its timing and update path tracking"""
        step = StepMetrics(
            state=state,
            start_time=start_time,
            end_time=time.time(),
            result=result,
            error=error,
        )
        self.steps.append(step)

        # Update path based on the step result
        self._update_path(state, result)

        if error:
            self.failed = True
            self.error = error

    def _update_path(self, state: str, result: Dict):
        """Update path based on the step result"""
        if state == "automation_classification":
            value = "automation" if result.get(
                "is_automation") else "not_automation"
            self._path += str(PathNode.AUTOMATION.get(value, "x"))
        elif state == "general_domain_classification":
            value = result.get("general_domain")
            self._path += str(PathNode.GENERAL_DOMAIN.get(value, "x"))
        elif state == "tool_selection":
            value = result.get("tool")
            self._path += str(PathNode.TOOL.get(value, "x"))
        elif state == "time_related_selection":
            value = result.get("time_related_device")
            self._path += str(PathNode.TIME_DEVICE.get(value, "x"))

    @property
    def leaf_id(self) -> str:
        """Get the current leaf path ID"""
        return self._path

    def finish(self):
        self.end_time = time.time()

    @property
    def total_duration(self) -> float:
        if self.end_time is None:
            self.end_time = time.time()
        return self.end_time - self.start_time

    def get_summary(self) -> str:
        summary = [
            "\n=== Cloud Pipeline Execution Summary ===",
            f"Query: {self.query}",
            f"Started at: {datetime.fromtimestamp(
                self.start_time).strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total duration: {self.total_duration:.2f}s",
            # Add path ID prominently at the top
            f"Final Path ID: {self.leaf_id}",
            f"Status: {'FAILED' if self.failed else 'SUCCESS'}",
            "\nExecution path:",
        ]

        for i, step in enumerate(self.steps, 1):
            summary.append(
                f"{i}. {step.state} ({step.duration:.3f}s) - {step.status}")
            if step.error:
                summary.append(f"   ❌ Error: {str(step.error)}")
                summary.append(
                    f"   ❌ Traceback: {traceback.format_tb(
                        step.error.__traceback__)[-1]}"
                )
            else:
                for key, value in step.result.items():
                    summary.append(f"   └─ {key}: {value}")

        if self.failed:
            summary.append("\n=== Pipeline Failed ===")
            summary.append(f"Final Error: {str(self.error)}")
            summary.append("Traceback:")
            summary.append(traceback.format_exc())
        else:
            summary.append("\n=== Pipeline Completed Successfully ===")

        return "\n".join(summary)

    def get_step_metrics(self, state: str) -> Dict[str, Any]:
        """Get metrics for a specific step"""
        step = next((s for s in self.steps if s.state == state), None)
        if step is None:
            return {}

        return {
            "duration_ms": step.duration,
            "error": str(step.error) if step.error else None,
        }
