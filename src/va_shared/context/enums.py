from enum import StrEnum


class LocalVAAgentPipelineState(StrEnum):
    """States for local voice assistant pipeline"""

    INIT = "init"
    MEMORY_UPDATE = "memory_update"
    CLOUD_PROCESSING = "cloud_processing"
    ACTION_EXECUTION = "action_execution"
    CLOUD_RESPONSE_GENERATION = "cloud_response_generation"
    END = "end"


class CloudVAAgentPipelineState(StrEnum):
    """States for cloud voice assistant pipeline"""

    INIT = "init"

    AUTOMATION_CLASSIFICATION = "automation_classification"
    GENERAL_DOMAIN_CLASSIFICATION = "general_domain_classification"
    DEVICE_DOMAIN_CLASSIFICATION = "device_domain_classification"

    HOME_RELATED = "home_related"
    WEB_SEARCH = "web_search"
    GENERAL_CONVERSATION = "general_conversation"
    MUSIC_PLAYER = "music_player"
    TIME_RELATED = "time_related"

    GET_INFO = "get_info"
    EXECUTE_SERVICE = "execute_service"
    GET_HISTORY = "get_history"

    TOOL_SELECTION = "tool_selection"
    ENTITY_EXTRACTION = "entity_extraction"
    SERVICE_SELECTION = "service_selection"
    ARGUMENT_GENERATION = "argument_generation"
    TIME_RELATED_SELECTION = "time_related_selection"

    CALENDAR = "calendar"
    TIMER_STOPWATCH_ALARM = "timer_stopwatch_alarm"

    RESPONSE_GENERATION = "response_generation"

    SERVICE_AND_ARGUMENT_GENERATION = "service_and_argument_generation"

    END = "end"


class HASSPipelineStage(StrEnum):
    """Stages for HASS voice assistant pipeline"""

    WAKE_WORD = "wake_word"
    STT = "stt"
    INTENT = "intent"
    TTS = "tts"
    END = "end"
