from dataclasses import dataclass, field
from typing import Protocol, overload, Awaitable, Any


class ListRowsFn(Protocol):
    @overload
    def __call__(
        self,
        *,
        page_size: int = ...,
        current_cursor: str | None = ...,
        page: None = ...,
    ) -> Awaitable[list[dict[str, Any]]]: ...

    @overload
    def __call__(
        self,
        *,
        page_size: int = ...,
        current_cursor: None = ...,
        page: int,
    ) -> Awaitable[list[dict[str, Any]]]: ...


class GetRowFn(Protocol):
    def __call__(
        self,
        row_id: Any,
    ) -> Awaitable[dict[str, Any] | None]: ...


class UpdateRowFn(Protocol):
    def __call__(self, row_id: Any, **kwargs) -> Awaitable[dict[str, Any] | None]: ...


class CreateRowFn(Protocol):
    def __call__(self, **kwargs) -> Awaitable[dict[str, Any] | None]: ...


class DeleteRowFn(Protocol):
    def __call__(self, row_id: Any) -> Awaitable[None]: ...
class CountRowsFn(Protocol):
    def __call__(self) -> Awaitable[int]: ...


class Composable(Protocol):
    """Objects that support a composable interface."""

    title: str
    """Short title"""
    label: str
    """Descriptive label"""
    column_mapping: str
    """The column this maps to in the DB."""


class Viewable(Composable, Protocol):
    @property
    def template_path(self) -> str:
        """Path to the template for this type."""


@dataclass(kw_only=True)
class Base:
    title: str
    """Short title"""
    label: str
    """Descriptive label"""
    column_mapping: str
    """The column this maps to in the DB."""
    optional: bool = field(default=False)
    """Whether this field is optional during creation"""


@dataclass(kw_only=True)
class Link(Base):
    href_column_mapping: str
    """The column to use as a URL slug."""


@dataclass(kw_only=True)
class Text(Base):
    @property
    def template_path(self) -> str:
        return "templates/types/text.jinja"


@dataclass(kw_only=True)
class Number(Base):
    @property
    def template_path(self) -> str:
        return "templates/types/number.jinja"


@dataclass(kw_only=True)
class TableList:
    name: str
    """Table Name"""
    description: str
    """Short description"""
    slug: str
    """Table slug for URLs"""
    pk_column: str
    """Table primary key to use in URLs"""
    count_rows: CountRowsFn
    """Get how many rows are present"""


@dataclass(kw_only=True)
class Table:
    details: TableList
    list_ui: list[Composable]
    detail_ui: list[Viewable]

    list_rows: ListRowsFn
    get_row: GetRowFn
    update_row: UpdateRowFn | None = None
    """How to update a row, None if not supported."""
    delete_row: DeleteRowFn | None = None
    """How to delete a row, None if not supported."""
    create_row: CreateRowFn | None = None
    create_ui: list[Viewable] = field(default_factory=list)
    """How to create a row, None if not supported."""


@dataclass(kw_only=True)
class AdminConfiguration:
    tables: list[Table]
    home_ui: list[TableList]

    _table_lookup: dict[str, Table] = field(default_factory=dict)

    def get_table(self, slug: str) -> Table | None:
        if not self._table_lookup:
            for table in self.tables:
                self._table_lookup[table.details.slug] = table

        return self._table_lookup.get(slug)
