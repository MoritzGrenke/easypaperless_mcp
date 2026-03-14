"""Singleton SyncPaperlessClient for easypaperless-mcp."""

import os
from typing import Optional

from easypaperless import SyncPaperlessClient

_client: Optional[SyncPaperlessClient] = None


def get_client() -> SyncPaperlessClient:
    """Return the shared SyncPaperlessClient, creating it on first call.

    Reads PAPERLESS_URL and PAPERLESS_TOKEN from the environment.

    Returns:
        The singleton SyncPaperlessClient instance.

    Raises:
        RuntimeError: If PAPERLESS_URL or PAPERLESS_TOKEN are not set.
    """
    global _client
    if _client is None:
        url = os.environ.get("PAPERLESS_URL")
        token = os.environ.get("PAPERLESS_TOKEN")
        if not url or not token:
            raise RuntimeError(
                "PAPERLESS_URL and PAPERLESS_TOKEN environment variables must be set"
            )
        _client = SyncPaperlessClient(url=url, api_key=token)
    return _client
