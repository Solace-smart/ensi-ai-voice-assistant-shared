# Ensi AI Voice Assistant Shared Package

Shared utilities for Ensi AI Voice Assistant components.

## Installation

```bash
pip install git+https://github.com/Solace-smart/ensi-ai-voice-assistant-shared.git@main
```

Or add to your requirements.txt:
```
va-shared @ git+https://github.com/Solace-smart/ensi-ai-voice-assistant-shared.git@main
```

## Components

- Context Management
- Pipeline Metrics
- Path Mapping
- Shared Enums

## Usage

```python
from va_shared.context import ContextManager
from va_shared.metrics import LocalPipelineMetrics, CloudPipelineMetrics

# Initialize context
context = ContextManager()

# Track metrics
metrics = LocalPipelineMetrics("user query")
```
