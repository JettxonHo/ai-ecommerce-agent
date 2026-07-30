"""AI E-commerce Agent backend production package.

Importing this package is intentionally side-effect free: it performs no
environment-variable reads, no ``.env`` loading, no network or database
connections, no model-client initialization, no LangGraph startup, no file
creation, and no emission of configuration or secrets.
"""

__version__ = "0.1.0"

__all__ = ["__version__"]
