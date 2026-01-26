"""
Notion MCP Fast - Fast MCP server for Notion local cache.

Reads Notion's local SQLite cache for fast, offline access without API calls.
"""

from .server import main

__all__ = ["main"]
