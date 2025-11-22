"""Telemetry initialization (OpenTelemetry + Sentry)."""
from app.core.settings import settings
from typing import Optional

_initialized = False

def init_tracing(app):
    global _initialized
    if _initialized or not settings.enable_tracing:
        return
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        resource = Resource.create({"service.name": settings.app_name})
        provider = TracerProvider(resource=resource)
        exporter = OTLPSpanExporter(endpoint=settings.otlp_endpoint) if settings.otlp_endpoint else OTLPSpanExporter()
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)
        _initialized = True
    except Exception as e:
        app.logger if hasattr(app, 'logger') else print(f"Tracing init failed: {e}")


def init_sentry():
    if not settings.enable_sentry or not settings.sentry_dsn:
        return
    try:
        import sentry_sdk
        sentry_sdk.init(dsn=settings.sentry_dsn, traces_sample_rate=0.1)
    except Exception as e:
        print(f"Sentry init failed: {e}")
