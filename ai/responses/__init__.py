"""Response Builder package.

Translates model text generations and event streams into standardized API schemas.
"""

from .service import DefaultResponseFormatter

__all__ = ["DefaultResponseFormatter"]
