from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, ClassVar, List
from enum import Enum
import json
from pydantic import BaseModel

from ..context.enums import (
    LocalVAAgentPipelineState,
    CloudVAAgentPipelineState,
    HASSPipelineStage,
)
from ..metrics.local_pipeline_metrics import LocalPipelineMetrics
from ..metrics.cloud_pipeline_metrics import CloudPipelineMetrics


@dataclass
class STTContext(BaseModel):
    """Context for Speech-to-Text processing"""

    text_result: str = ""
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON serializable dict."""
        return asdict(self)

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "STTContext":
        """Create instance from JSON dict."""
        return cls(**data)


@dataclass
class TTSContext(BaseModel):
    """Context for Text-to-Speech processing"""

    speech_result: bytes = bytes()
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON serializable dict."""
        return {
            "speech_result": list(self.speech_result),  # Convert bytes to list
            "metadata": self.metadata,
        }

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "TTSContext":
        """Create instance from JSON dict."""
        return cls(
            speech_result=bytes(data["speech_result"]), metadata=data["metadata"]
        )


@dataclass
class LocalVAAgentContext(BaseModel):
    """Context specific to local voice assistant agent"""

    conversation_id: str = ""
    language: str | None = None
    local_processing_results: Dict[str, Any] = field(default_factory=dict)
    metrics: LocalPipelineMetrics = field(default_factory=LocalPipelineMetrics)
    leaf_id: str | None = None
    summary: str | None = None

    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON serializable dict."""
        return asdict(self)

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "LocalVAAgentContext":
        """Create instance from JSON dict."""
        return cls(**data)


@dataclass
class CloudVAAgentContext(BaseModel):
    """Context specific to cloud voice assistant agent"""

    cloud_processing_results: Dict[str, Any] = field(default_factory=dict)
    metrics: CloudPipelineMetrics = field(default_factory=CloudPipelineMetrics)
    leaf_id: str | None = None
    summary: str | None = None
    response: str = ""
    ha_states: Dict[str, Any] = field(default_factory=dict)
    ha_services: Dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON serializable dict."""
        return asdict(self)

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "CloudVAAgentContext":
        """Create instance from JSON dict."""
        return cls(**data)


@dataclass
class VoiceAssistantAgentContext(BaseModel):
    """Main context for voice assistant agent"""

    conversation_id: str = ""
    language: str | None = None
    query_id: str = ""
    query: str = ""

    in_session_memory: List[Dict[str, Any]] = field(default_factory=list)
    last_interaction: Dict[str, Any] | None = None
    persistent_memory: Dict[str, Any] = field(default_factory=dict)

    local_va_agent_start_stage: LocalVAAgentPipelineState
    local_va_agent_end_stage: LocalVAAgentPipelineState
    cloud_va_agent_start_stage: CloudVAAgentPipelineState
    cloud_va_agent_end_stage: CloudVAAgentPipelineState
    local_context: LocalVAAgentContext = field(default_factory=LocalVAAgentContext)
    cloud_context: CloudVAAgentContext = field(default_factory=CloudVAAgentContext)

    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON serializable dict."""
        return {
            "local_va_agent_start_stage": self.local_va_agent_start_stage.value,
            "local_va_agent_end_stage": self.local_va_agent_end_stage.value,
            "cloud_va_agent_start_stage": self.cloud_va_agent_start_stage.value,
            "cloud_va_agent_end_stage": self.cloud_va_agent_end_stage.value,
            "local_context": self.local_context.to_json(),
            "cloud_context": self.cloud_context.to_json(),
        }

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "VoiceAssistantAgentContext":
        """Create instance from JSON dict."""
        return cls(
            local_va_agent_start_stage=LocalVAAgentPipelineState(
                data["local_va_agent_start_stage"]
            ),
            local_va_agent_end_stage=LocalVAAgentPipelineState(
                data["local_va_agent_end_stage"]
            ),
            cloud_va_agent_start_stage=CloudVAAgentPipelineState(
                data["cloud_va_agent_start_stage"]
            ),
            cloud_va_agent_end_stage=CloudVAAgentPipelineState(
                data["cloud_va_agent_end_stage"]
            ),
            local_context=LocalVAAgentContext.from_json(data["local_context"]),
            cloud_context=CloudVAAgentContext.from_json(data["cloud_context"]),
        )


@dataclass
class HASSVoiceAssistantPipelineContext(BaseModel):
    """Global context for HASS voice assistant pipeline"""

    hass_va_pipeline_start_stage: HASSPipelineStage
    hass_va_pipeline_end_stage: HASSPipelineStage
    stt_context: STTContext = field(default_factory=STTContext)
    va_agent_context: VoiceAssistantAgentContext = field(
        default_factory=lambda: VoiceAssistantAgentContext(
            local_va_agent_start_stage=LocalVAAgentPipelineState.INIT,
            local_va_agent_end_stage=LocalVAAgentPipelineState.END,
            cloud_va_agent_start_stage=CloudVAAgentPipelineState.INIT,
            cloud_va_agent_end_stage=CloudVAAgentPipelineState.END,
        )
    )
    tts_context: TTSContext = field(default_factory=TTSContext)
    shared_data: Dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON serializable dict."""
        return {
            "hass_va_pipeline_start_stage": self.hass_va_pipeline_start_stage.value,
            "hass_va_pipeline_end_stage": self.hass_va_pipeline_end_stage.value,
            "stt_context": self.stt_context.to_json(),
            "va_agent_context": self.va_agent_context.to_json(),
            "tts_context": self.tts_context.to_json(),
            "shared_data": self.shared_data,
        }

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "HASSVoiceAssistantPipelineContext":
        """Create instance from JSON dict."""
        return cls(
            hass_va_pipeline_start_stage=HASSPipelineStage(
                data["hass_va_pipeline_start_stage"]
            ),
            hass_va_pipeline_end_stage=HASSPipelineStage(
                data["hass_va_pipeline_end_stage"]
            ),
            stt_context=STTContext.from_json(data["stt_context"]),
            va_agent_context=VoiceAssistantAgentContext.from_json(
                data["va_agent_context"]
            ),
            tts_context=TTSContext.from_json(data["tts_context"]),
            shared_data=data["shared_data"],
        )
