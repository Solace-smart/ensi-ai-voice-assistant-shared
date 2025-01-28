def test_imports():
    from va_shared.context import ContextManager
    from va_shared.metrics import LocalPipelineMetrics, CloudPipelineMetrics

    assert ContextManager is not None
    assert LocalPipelineMetrics is not None
    assert CloudPipelineMetrics is not None
