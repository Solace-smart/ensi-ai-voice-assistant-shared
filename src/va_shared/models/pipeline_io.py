from typing import Any, Dict, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from ..context import (
    CloudVAAgentContext,
    LocalVAAgentContext,
    VoiceAssistantAgentContext,
)
from ..context.enums import CloudVAAgentPipelineState, LocalVAAgentPipelineState

#########################################
### MODELS FOR VOICE ASSISTANT AGENTS ###
#########################################

class VoiceAssistantAgentInput(BaseModel):
    """Base input model for voice assistant processing"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    query: str = Field(..., description="The user's query string")
    va_context: VoiceAssistantAgentContext = Field(..., description="Voice assistant context")

class VoiceAssistantAgentOutput(BaseModel):
    """Base output model for voice assistant processing"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    va_context: VoiceAssistantAgentContext = Field(..., description="Updated voice assistant context")

class LocalVoiceAssistantInput(VoiceAssistantAgentInput):
    """Input model for local voice assistant"""

    @model_validator(mode='after')
    def validate_local_context(self):
        """Validate local pipeline stages"""
        if not hasattr(self.va_context, 'local_va_agent_start_stage'):
            self.va_context.local_va_agent_start_stage = LocalVAAgentPipelineState.INIT
        if not hasattr(self.va_context, 'local_va_agent_end_stage'):
            self.va_context.local_va_agent_end_stage = LocalVAAgentPipelineState.END
        return self

class LocalVoiceAssistantOutput(VoiceAssistantAgentOutput):
    """Output model for local voice assistant"""

    @model_validator(mode='after')
    def validate_local_results(self):
        """Validate local processing results exist"""
        if not self.va_context.local_context.local_processing_results:
            self.va_context.local_context.local_processing_results = {}
        return self

class CloudVoiceAssistantInput(VoiceAssistantAgentInput):
    """Input model for cloud voice assistant"""

    ha_states: Dict[str, Any] = Field(default_factory=dict, description="Home Assistant states")
    ha_services: Dict[str, Any] = Field(default_factory=dict, description="Home Assistant services")

    @model_validator(mode='after')
    def validate_cloud_context(self):
        """Validate cloud pipeline stages and HA data"""
        if not hasattr(self.va_context, 'cloud_va_agent_start_stage'):
            self.va_context.cloud_va_agent_start_stage = CloudVAAgentPipelineState.INIT
        if not hasattr(self.va_context, 'cloud_va_agent_end_stage'):
            self.va_context.cloud_va_agent_end_stage = CloudVAAgentPipelineState.END

        # Update cloud context with HA data
        self.va_context.cloud_context.ha_states = self.ha_states
        self.va_context.cloud_context.ha_services = self.ha_services
        return self

class CloudVoiceAssistantOutput(VoiceAssistantAgentOutput):
    """Output model for cloud voice assistant"""

    @model_validator(mode='after')
    def validate_cloud_results(self):
        """Validate cloud processing results exist and are not None"""
        # Check if cloud_processing_results exists and is not None
        if not self.va_context.cloud_context.cloud_processing_results:
            raise ValueError("Cloud processing results cannot be None or empty")

        return self

###################################
### MODELS FOR BLOCK PROCESSORS ###
###################################

class BlockProcessorInput(BaseModel):
    """Input model for pipeline block processors"""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    query: str = Field(..., description="The user's query string")
    va_context: VoiceAssistantAgentContext = Field(..., description="Voice assistant context")

class BlockProcessorOutput(BaseModel):
    """Output model for pipeline block processors
        Block processors should output a dictionary of results or an updated context or none
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    result: Union[Dict[str, Any], VoiceAssistantAgentContext, None] = Field(
        ...,
        description="Processing result or updated context"
    )