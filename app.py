import os
import sqlite3
from contextlib import asynccontextmanager
from sqlite3 import Row
from typing import AsyncIterator, Awaitable, Any

import aiosqlite
import jinja2
from litestar import Litestar
from litestar.config.cors import CORSConfig
from litestar.config.csrf import CSRFConfig
from litestar.middleware.rate_limit import RateLimitConfig
from litestar.middleware.session.client_side import CookieBackendConfig
from litestar.plugins.flash import FlashPlugin, FlashConfig
from litestar.plugins.jinja import JinjaTemplateEngine
from litestar.plugins.opentelemetry import OpenTelemetryConfig
from litestar.template import TemplateConfig

from skelmis.admin.config import (
    AdminConfiguration,
    Table,
    Text,
    Number,
    TableList,
    Link,
)
from skelmis.admin.plugin import AdminPlugin


@asynccontextmanager
async def lifespan(app: Litestar) -> AsyncIterator[None]:
    async with aiosqlite.connect("example.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                location TEXT,
                age INTEGER
            )
        """)
        await db.commit()
    yield


async def list_rows() -> list[dict]:
    async with aiosqlite.connect("example.db") as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users") as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


async def get_row(row_id: Any) -> dict | None:
    async with aiosqlite.connect("example.db") as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE id = ?", row_id) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def count_rows() -> int:
    async with aiosqlite.connect("example.db") as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            row = await cursor.fetchone()
        return row[0]


utl = TableList(
    slug="users",
    name="Users",
    description="Users in the app",
    count_rows=count_rows,
    pk_column="id",
)
config = AdminConfiguration(
    tables=[
        Table(
            list_rows=list_rows,
            get_row=get_row,
            detail_ui=[
                Number(title="ID", label="Row ID", column_mapping="id"),
                Text(title="Name", label="Your Name", column_mapping="name"),
                Number(title="Age", label="Your Age", column_mapping="age"),
            ],
            list_ui=[
                Link(
                    title="Name",
                    label="Your Name",
                    column_mapping="name",
                    href_column_mapping="id",
                ),
                Text(
                    title="Location",
                    label="Location of user",
                    column_mapping="location",
                ),
                Number(title="Age", label="Your Age", column_mapping="age"),
            ],
            details=utl,
        )
    ],
    home_ui=[
        utl,
        TableList(
            slug="test",
            name="Test",
            description="Blah",
            count_rows=count_rows,
            pk_column="id",
        ),
    ],
)

IS_PRODUCTION = False
CSRF_TOKEN = b"55e3f2304c9e8fc7a6dd501e50402890"
SESSION_KEY = b"5f1532d0ef6930776c415efcdf52451f"
cors_config = CORSConfig(
    allow_origins=[],
    allow_headers=[],
    allow_methods=[],
    allow_credentials=False,
)
csrf_config = CSRFConfig(
    secret=CSRF_TOKEN,
    # Aptly named so it doesnt clash
    # with piccolo 'csrftoken' cookies
    cookie_name="csrf_token",
    cookie_secure=IS_PRODUCTION,
    cookie_httponly=IS_PRODUCTION,
)
# noinspection PyTypeChecker
rate_limit_config = RateLimitConfig(rate_limit=("second", 10))


ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(
        searchpath=[
            os.path.join(os.path.dirname(__file__), "skelmis", "admin", "templates"),
        ]
    ),
    autoescape=True,
)

template_config = TemplateConfig(
    directory="skelmis/admin/templates",
    engine=JinjaTemplateEngine.from_environment(ENVIRONMENT),
)
flash_plugin = FlashPlugin(
    config=FlashConfig(template_config=template_config),
)
session_config = CookieBackendConfig(secret=SESSION_KEY)
app = Litestar(
    plugins=[AdminPlugin(config=config), flash_plugin],
    debug=not IS_PRODUCTION,
    template_config=template_config,
    cors_config=cors_config,
    csrf_config=csrf_config,
    middleware=[session_config.middleware],
    lifespan=[lifespan],
)
