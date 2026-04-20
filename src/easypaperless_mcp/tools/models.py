"""Shared response models for MCP tools."""

from typing import Generic, List, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ListResult(BaseModel, Generic[T]):
    """Wrapper returned by all ``list_*`` MCP tools.

    Attributes:
        count: Total number of items matching the applied filters in the
            paperless-ngx instance — **not** just the number of items on the
            current page. Use this value to plan pagination or report
            accurate counts to users.
        items: The resource objects returned for the requested page / all
            fetched pages.
        omitted_fields: Field names excluded from items due to return_fields
            filtering, plus a retrieval hint as the last element. Empty when
            all fields are included.
    """

    count: int
    items: List[T]
    omitted_fields: list[str] = []
