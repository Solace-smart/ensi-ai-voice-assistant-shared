from typing import Any, Dict

from pydantic import BaseModel, Field, model_validator

from ..context import VoiceAssistantAgentContext


class CloudVAAgentRequest(BaseModel):
    """Base request model for voice assistant API endpoints"""
    va_context: VoiceAssistantAgentContext = Field(..., description="Voice assistant context")

    class Config:
        arbitrary_types_allowed = True

class CloudVAAgentResponse(BaseModel):
    """Base response model for voice assistant API endpoints"""
    va_context: Dict[str, Any] = Field(..., description="Serialized voice assistant context")


class ProcessQueryRequest(CloudVAAgentRequest):
    """Request model for process_query endpoint"""
    pass

class ProcessQueryResponse(CloudVAAgentResponse):
    """Response model for process_query endpoint"""
    pass

class GenerateResponseRequest(CloudVAAgentRequest):
    """Request model for generate_response endpoint"""
    pass

class GenerateResponseResponse(CloudVAAgentResponse):
    """Response model for generate_response endpoint"""
    pass