"""Custom exceptions for ccusage-py."""

from __future__ import annotations


class CcusageError(Exception):
    """Base exception for ccusage-py."""

    pass


class DataLoadError(CcusageError):
    """Error loading usage data from JSONL files."""

    pass


class PricingError(CcusageError):
    """Error fetching or calculating pricing information."""

    pass


class ValidationError(CcusageError):
    """Error validating data models."""

    pass


class ConfigurationError(CcusageError):
    """Error with configuration or setup."""

    pass


class ProcessingError(CcusageError):
    """Error processing usage data."""

    pass


class FileSystemError(CcusageError):
    """Error accessing files or directories."""

    pass


class NetworkError(CcusageError):
    """Error with network operations."""

    pass
