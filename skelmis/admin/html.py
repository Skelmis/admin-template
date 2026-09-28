import secrets
from typing import Literal

from litestar import MediaType, Request
from litestar.connection import ASGIConnection
from litestar.plugins.flash import flash
from litestar.response import Template


def alert(
    request: Request | ASGIConnection,
    message: str,
    level: Literal["info", "warning", "error", "success"] = "info",
):
    """A helper function given we hard code level in templates"""
    flash(request, message, category=level)


def get_csp(*, csp_allow_discord_cdn_in_images: bool = False) -> tuple[str, str]:
    nonce = secrets.token_urlsafe(16)
    text = (
        "default-src 'none'; frame-ancestors 'none'; object-src 'none'; base-uri 'none'; "
        f"script-src 'nonce-{nonce}' "
        f"'strict-dynamic'; style-src 'nonce-{nonce}'; require-trusted-types-for 'script'; "
        f"img-src 'nonce-{nonce}' data: 'self'"
        f"{' https://cdn.discordapp.com' if csp_allow_discord_cdn_in_images else ''}; "
        f"script-src-attr 'nonce-{nonce}'; frame-src https://challenges.cloudflare.com;"
    )
    return text, nonce


def html_template(
    template_name: str,
    context: dict | None = None,
    *,
    status_code: int = 200,
    csp_allow_discord_cdn_in_images: bool = False,
) -> Template:
    if context is None:
        context = {}

    csp, nonce = get_csp(
        csp_allow_discord_cdn_in_images=csp_allow_discord_cdn_in_images
    )
    context["csp_nonce"] = nonce
    context["site_name"] = "Admin Site"

    return Template(
        template_name=template_name,
        context=context,
        headers={"content-security-policy": csp},
        media_type=MediaType.HTML,
        status_code=status_code,
    )
