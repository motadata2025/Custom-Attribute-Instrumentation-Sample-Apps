from __future__ import annotations

from typing import Optional, Sequence
from opentelemetry import trace


class MotadataDynamicInstrumentation:
    """
    Simple utility to add custom attributes to the current OpenTelemetry span.
    Keys are automatically prefixed with 'apm.' if not already present.

    Never raises exceptions. Silently ignores everything invalid.
    """

    _PREFIX = "apm."

    def __init__(self) -> None:
        raise RuntimeError("This is a static utility class")

    @staticmethod
    def _add_prefix(key: Optional[str]) -> Optional[str]:
        if not key:
            return None
        try:
            return key if key.startswith(MotadataDynamicInstrumentation._PREFIX) else MotadataDynamicInstrumentation._PREFIX + key
        except Exception:
            return None

    @staticmethod
    def _try_set_attribute(key: str, value: any) -> None:
        try:
            span = trace.get_current_span()
            if span.is_recording():
                span.set_attribute(key, value)
        except Exception:
            pass

    # Scalar values

    @staticmethod
    def set(key: str, value: Optional[bool]) -> None:
        if key is None or value is None:
            return
        prefixed = MotadataDynamicInstrumentation._add_prefix(key)
        if prefixed:
            MotadataDynamicInstrumentation._try_set_attribute(prefixed, value)

    @staticmethod
    def set(key: str, value: Optional[int]) -> None:
        if key is None or value is None:
            return
        prefixed = MotadataDynamicInstrumentation._add_prefix(key)
        if prefixed:
            MotadataDynamicInstrumentation._try_set_attribute(prefixed, value)

    @staticmethod
    def set(key: str, value: Optional[float]) -> None:
        if key is None or value is None:
            return
        prefixed = MotadataDynamicInstrumentation._add_prefix(key)
        if prefixed:
            MotadataDynamicInstrumentation._try_set_attribute(prefixed, value)

    @staticmethod
    def set(key: str, value: Optional[str]) -> None:
        if key is None or value is None:
            return
        prefixed = MotadataDynamicInstrumentation._add_prefix(key)
        if prefixed:
            MotadataDynamicInstrumentation._try_set_attribute(prefixed, value)

    # List / Sequence values

    @staticmethod
    def set_bool_list(key: str, value: Optional[Sequence[bool]]) -> None:
        if not value or key is None or len(value) == 0:
            return
        prefixed = MotadataDynamicInstrumentation._add_prefix(key)
        if prefixed:
            try:
                MotadataDynamicInstrumentation._try_set_attribute(prefixed, list(value))
            except Exception:
                pass

    @staticmethod
    def set_int_list(key: str, value: Optional[Sequence[int]]) -> None:
        if not value or key is None or len(value) == 0:
            return
        prefixed = MotadataDynamicInstrumentation._add_prefix(key)
        if prefixed:
            try:
                MotadataDynamicInstrumentation._try_set_attribute(prefixed, list(value))
            except Exception:
                pass

    @staticmethod
    def set_float_list(key: str, value: Optional[Sequence[float]]) -> None:
        if not value or key is None or len(value) == 0:
            return
        prefixed = MotadataDynamicInstrumentation._add_prefix(key)
        if prefixed:
            try:
                MotadataDynamicInstrumentation._try_set_attribute(prefixed, list(value))
            except Exception:
                pass

    @staticmethod
    def set_string_list(key: str, value: Optional[Sequence[str]]) -> None:
        if not value or key is None or len(value) == 0:
            return
        prefixed = MotadataDynamicInstrumentation._add_prefix(key)
        if prefixed:
            try:
                MotadataDynamicInstrumentation._try_set_attribute(prefixed, list(value))
            except Exception:
                pass