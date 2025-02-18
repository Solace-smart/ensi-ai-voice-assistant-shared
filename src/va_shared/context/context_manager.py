from dataclasses import asdict, dataclass, field
from typing import Any, AsyncIterable, Awaitable, Callable, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field
import ulid

from ..metrics.pipeline_metrics import PipelineMetrics as PipelineMetrics
from .enums import (
    CloudVAAgentPipelineState,
    HASSPipelineStage,
    LocalVAAgentPipelineState,
)


class STTContext(BaseModel):
    """Context for Speech-to-Text processing"""
    text_result: str | None = None
    confidence: float | None = None
    metadata: dict[str, Any] | None = None

    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON serializable dict."""
        return self.model_dump(exclude_none=True)

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "STTContext":
        """Create instance from JSON dict."""
        return cls(**data)


class TTSContext(BaseModel):
    """Context for Text-to-Speech processing"""
    speech_result: bytes | None = None
    metadata: dict[str, Any] | None = None

    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON serializable dict."""
        return {
            "speech_result": list(self.speech_result) if self.speech_result else None,
            "metadata": self.metadata,
        }

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "TTSContext":
        """Create instance from JSON dict."""
        if data.get("speech_result"):
            data["speech_result"] = bytes(data["speech_result"])
        return cls(**data)


class LocalVAAgentContext(BaseModel):
    """Context specific to local voice assistant agent"""

    local_processing_results: Dict[str, Any] = Field(default_factory=dict)
    metrics: PipelineMetrics = Field(default_factory=PipelineMetrics)
    leaf_id: str | None = None
    summary: str | None = None

    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON serializable dict."""
        return self.model_dump(exclude_none=True)

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "LocalVAAgentContext":
        """Create instance from JSON dict."""
        return cls(**data)


class CloudVAAgentContext(BaseModel):
    """Context specific to cloud voice assistant agent"""

    cloud_processing_results: Dict[str, Any] = {}
    metrics: PipelineMetrics = PipelineMetrics()
    leaf_id: str | None = ""
    summary: str | None = None
    response: str = ""
    ha_states: Dict[str, Any] = None
    ha_services: Dict[str, Any] = None

    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON serializable dict."""
        return self.model_dump(exclude_none=True)

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "CloudVAAgentContext":
        """Create instance from JSON dict."""
        return cls(**data)


class VoiceAssistantAgentContext(BaseModel):
    """Main context for voice assistant agent"""
    model_config = ConfigDict(
        extra='allow',
        arbitrary_types_allowed=True,
        validate_assignment=True
    )

    conversation_id: str | None = None
    language: str | None = None
    query_id: str | None = None
    query: str | None = None

    in_session_memory: list[dict[str, Any]] = []
    last_interaction: dict[str, Any] | None = None
    persistent_memory: dict[str, Any] = {}

    local_va_agent_start_stage: LocalVAAgentPipelineState = LocalVAAgentPipelineState.INIT
    local_va_agent_end_stage: LocalVAAgentPipelineState = LocalVAAgentPipelineState.END
    cloud_va_agent_start_stage: CloudVAAgentPipelineState = CloudVAAgentPipelineState.INIT
    cloud_va_agent_end_stage: CloudVAAgentPipelineState = CloudVAAgentPipelineState.END

    local_context: LocalVAAgentContext = LocalVAAgentContext()
    cloud_context: CloudVAAgentContext = CloudVAAgentContext()

    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON serializable dict."""
        return {
            "conversation_id": self.conversation_id,
            "language": self.language,
            "query_id": self.query_id,
            "query": self.query,
            "in_session_memory": self.in_session_memory,
            "last_interaction": self.last_interaction,
            "persistent_memory": self.persistent_memory,
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
        if isinstance(data, VoiceAssistantAgentContext):
            return data
        return cls(
            conversation_id=data["conversation_id"],
            language=data["language"],
            query_id=data["query_id"],
            query=data["query"],
            in_session_memory=data["in_session_memory"],
            last_interaction=data["last_interaction"],
            persistent_memory=data["persistent_memory"],
            local_va_agent_start_stage=LocalVAAgentPipelineState(
                data["local_va_agent_start_stage"]),
            local_va_agent_end_stage=LocalVAAgentPipelineState(
                data["local_va_agent_end_stage"]),
            cloud_va_agent_start_stage=CloudVAAgentPipelineState(
                data["cloud_va_agent_start_stage"]),
            cloud_va_agent_end_stage=CloudVAAgentPipelineState(
                data["cloud_va_agent_end_stage"]),
            local_context=LocalVAAgentContext.from_json(data["local_context"]),
            cloud_context=CloudVAAgentContext.from_json(data["cloud_context"]),
        )


class SatelliteInputContext(BaseModel):
    """Context for satellite input processing"""
    input_stream_method: Callable[[], AsyncIterable[bytes]] | None = None
    metadata: dict[str, Any] | None = None

    def to_json(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True)


class SatelliteOutputContext(BaseModel):
    """Context for satellite output processing"""
    output_stream_method: Callable[[], Awaitable[None]] | None = None
    metadata: dict[str, Any] | None = None

    def to_json(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True)


class HASSVoiceAssistantPipelineContext(BaseModel):
    """Global context for HASS voice assistant pipeline"""
    hass_va_pipeline_start_stage: HASSPipelineStage = HASSPipelineStage.INIT
    hass_va_pipeline_end_stage: HASSPipelineStage = HASSPipelineStage.END
    satellite_input_context: SatelliteInputContext = Field(default_factory=SatelliteInputContext)
    stt_context: STTContext = Field(default_factory=STTContext)
    va_agent_context: VoiceAssistantAgentContext = Field(
        default_factory=lambda: VoiceAssistantAgentContext(
            conversation_id=str(ulid.new()),
            query_id=str(ulid.new()),
            local_va_agent_start_stage=LocalVAAgentPipelineState.INIT,
            local_va_agent_end_stage=LocalVAAgentPipelineState.END,
            cloud_va_agent_start_stage=CloudVAAgentPipelineState.INIT,
            cloud_va_agent_end_stage=CloudVAAgentPipelineState.END,
        )
    )
    tts_context: TTSContext = Field(default_factory=TTSContext)
    satellite_output_context: SatelliteOutputContext = Field(default_factory=SatelliteOutputContext)
    shared_data: Dict[str, Any] = Field(default_factory=dict)


    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON serializable dict."""
        return {
            "hass_va_pipeline_start_stage": self.hass_va_pipeline_start_stage.value,
            "hass_va_pipeline_end_stage": self.hass_va_pipeline_end_stage.value,
            "stt_context": self.stt_context.to_json(),
            "va_agent_context": self.va_agent_context.to_json(),
            "tts_context": self.tts_context.to_json(),
            "shared_data": self.shared_data,
            "satellite_input_context": self.satellite_input_context.to_json(),
            "satellite_output_context": self.satellite_output_context.to_json(),
        }

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "HASSVoiceAssistantPipelineContext":
        """Create instance from JSON dict."""
        return cls(
            hass_va_pipeline_start_stage=HASSPipelineStage(
                data["hass_va_pipeline_start_stage"]),
            hass_va_pipeline_end_stage=HASSPipelineStage(
                data["hass_va_pipeline_end_stage"]),
            stt_context=STTContext.from_json(data["stt_context"]),
            va_agent_context=VoiceAssistantAgentContext.from_json(
                data["va_agent_context"]),
            tts_context=TTSContext.from_json(data["tts_context"]),
            shared_data=data["shared_data"],
            satellite_input_context=SatelliteInputContext.from_json(data["satellite_input_context"]),
            satellite_output_context=SatelliteOutputContext.from_json(data["satellite_output_context"]),
        )
