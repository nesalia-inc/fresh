"""Adapters module - I/O implementations for external services."""

from __future__ import annotations

from .protocols import (
    CacheRepository,
    HistoryRepository,
    HTTPFetcher,
    PageStorage,
    RobotsChecker,
    SearchIndex,
    SitemapDiscovery,
    URLNormalizer,
)

__all__ = [
    "CacheRepository",
    "HistoryRepository",
    "HTTPFetcher",
    "PageStorage",
    "RobotsChecker",
    "SearchIndex",
    "SitemapDiscovery",
    "URLNormalizer",
]
