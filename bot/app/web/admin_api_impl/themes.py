# ruff: noqa: F401,F403,F405,I001
from ._runtime import *  # noqa: F403,F405

import asyncio
import hashlib
import ipaddress
import re
import socket

from aiohttp import ClientSession, ClientTimeout

from config.webapp_themes_config import (
    WebappThemesConfig,
    ensure_webapp_core_themes,
    resolved_webapp_themes_catalog,
    write_webapp_theme_dir,
)


WEBAPP_LOGO_MAX_BYTES = 2 * 1024 * 1024
WEBAPP_UPLOADED_LOGO_DIR = Path(__file__).resolve().parents[4] / "data" / "webapp-logo" / "uploads"
WEBAPP_UPLOADED_LOGO_PATH = "/webapp-uploaded-logo"
WEBAPP_LOGO_UPLOAD_CONTENT_TYPES = {
    ".gif": "image/gif",
    ".ico": "image/x-icon",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".svg": "image/svg+xml",
    ".webp": "image/webp",
}


def _detect_logo_extension(
    body: bytes, content_type: str = "", filename: str = ""
) -> Optional[str]:
    content_type = (content_type or "").split(";", 1)[0].strip().lower()
    suffix = Path(filename or "").suffix.lower()
    if content_type == "image/png" or body.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if content_type == "image/jpeg" or body.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if content_type == "image/gif" or body.startswith((b"GIF87a", b"GIF89a")):
        return ".gif"
    if content_type == "image/webp" or (
        len(body) > 12 and body[:4] == b"RIFF" and body[8:12] == b"WEBP"
    ):
        return ".webp"
    if content_type in {"image/svg+xml", "image/svg"} or suffix == ".svg":
        head = body[:512].lstrip().lower()
        if head.startswith(b"<svg") or b"<svg" in head:
            return ".svg"
    if content_type == "image/x-icon" or suffix == ".ico":
        if body.startswith(b"\x00\x00\x01\x00"):
            return ".ico"
    return suffix if suffix in WEBAPP_LOGO_UPLOAD_CONTENT_TYPES else None


def _write_uploaded_logo(body: bytes, content_type: str = "", filename: str = "") -> str:
    if not body or len(body) > WEBAPP_LOGO_MAX_BYTES:
        raise ValueError("logo must be a non-empty image up to 2 MiB")
    ext = _detect_logo_extension(body, content_type, filename)
    if ext not in WEBAPP_LOGO_UPLOAD_CONTENT_TYPES:
        raise ValueError("unsupported image type")
    digest = hashlib.sha256(body).hexdigest()[:16]
    safe_name = f"logo-{digest}{ext}"
    WEBAPP_UPLOADED_LOGO_DIR.mkdir(parents=True, exist_ok=True)
    (WEBAPP_UPLOADED_LOGO_DIR / safe_name).write_bytes(body)
    return f"{WEBAPP_UPLOADED_LOGO_PATH}/{safe_name}"


async def _read_uploaded_logo_file(request: web.Request) -> tuple[bytes, str, str]:
    reader = await request.multipart()
    async for part in reader:
        if part.name != "file":
            continue
        body = bytearray()
        while True:
            chunk = await part.read_chunk(size=64 * 1024)
            if not chunk:
                break
            body.extend(chunk)
            if len(body) > WEBAPP_LOGO_MAX_BYTES:
                raise ValueError("logo must be up to 2 MiB")
        return bytes(body), part.headers.get("Content-Type", ""), part.filename or ""
    raise ValueError("file field is required")


async def _hostname_resolves_to_public_address(hostname: str) -> bool:
    if not hostname:
        return False
    try:
        ip_obj = ipaddress.ip_address(hostname)
        return not (
            ip_obj.is_private
            or ip_obj.is_loopback
            or ip_obj.is_link_local
            or ip_obj.is_unspecified
            or ip_obj.is_reserved
        )
    except ValueError:
        pass

    loop = asyncio.get_running_loop()
    try:
        resolved = await loop.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)
    except Exception:
        return False

    found_public_ip = False
    for entry in resolved:
        sockaddr = entry[4]
        candidate = sockaddr[0] if sockaddr else ""
        try:
            ip_obj = ipaddress.ip_address(candidate)
        except ValueError:
            continue
        if (
            ip_obj.is_private
            or ip_obj.is_loopback
            or ip_obj.is_link_local
            or ip_obj.is_unspecified
            or ip_obj.is_reserved
        ):
            return False
        found_public_ip = True
    return found_public_ip


async def _fetch_logo_from_url(url: str) -> tuple[bytes, str, str]:
    parsed = urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError("only https image URLs are supported")
    if not await _hostname_resolves_to_public_address(parsed.hostname):
        raise ValueError("logo URL must resolve to a public address")

    timeout = ClientTimeout(total=5)
    async with ClientSession(timeout=timeout, headers={"User-Agent": "Mozilla/5.0"}) as session:
        async with session.get(
            url,
            allow_redirects=False,
            headers={"Accept": "image/avif,image/webp,image/svg+xml,image/png,image/*,*/*;q=0.8"},
        ) as response:
            if response.status != 200:
                raise ValueError(f"logo URL returned HTTP {response.status}")
            content_type = (
                (response.headers.get("Content-Type") or "").split(";", 1)[0].strip().lower()
            )
            if content_type and not content_type.startswith("image/"):
                raise ValueError("logo URL returned non-image content")
            body = bytearray()
            async for chunk in response.content.iter_chunked(64 * 1024):
                body.extend(chunk)
                if len(body) > WEBAPP_LOGO_MAX_BYTES:
                    raise ValueError("logo must be up to 2 MiB")
            return bytes(body), content_type, Path(parsed.path).name


async def admin_appearance_logo_upload_route(request: web.Request) -> web.Response:
    _require_admin_user_id(request)
    content_type = (request.headers.get("Content-Type") or "").lower()
    try:
        if content_type.startswith("multipart/form-data"):
            body, detected_content_type, filename = await _read_uploaded_logo_file(request)
        else:
            payload = await _read_json(request)
            source_url = str(payload.get("url") or "").strip()
            if not source_url:
                return _error(400, "invalid_payload", "url or file is required")
            body, detected_content_type, filename = await _fetch_logo_from_url(source_url)
        logo_url = _write_uploaded_logo(body, detected_content_type, filename)
    except ValueError as exc:
        return _error(400, "invalid_logo", str(exc))
    except OSError as exc:
        logger.exception("Failed to save uploaded webapp logo")
        return _error(500, "write_failed", str(exc))

    return _ok({"logo_url": logo_url})


async def admin_themes_get_route(request: web.Request) -> web.Response:
    _require_admin_user_id(request)
    settings: Settings = request.app["settings"]
    primary = settings.WEBAPP_PRIMARY_COLOR or "#00fe7a"
    catalog = resolved_webapp_themes_catalog(
        primary_accent=primary,
        env_default_theme=settings.WEBAPP_DEFAULT_THEME,
        theme_dir=settings.WEBAPP_THEMES_DIR,
    )

    return _ok(
        {
            "exists": Path(settings.WEBAPP_THEMES_DIR).expanduser().exists(),
            "themes_dir": str(Path(settings.WEBAPP_THEMES_DIR).expanduser()),
            "catalog": _webapp_themes_catalog_payload(catalog),
        }
    )


async def admin_themes_save_route(request: web.Request) -> web.Response:
    _require_admin_user_id(request)
    settings: Settings = request.app["settings"]
    payload = await _read_json(request)
    catalog = payload.get("catalog") if "catalog" in payload else payload
    if not isinstance(catalog, dict):
        return _error(400, "invalid_payload", "catalog must be an object")

    try:
        config = WebappThemesConfig.model_validate(catalog)
    except (ValidationError, ValueError) as exc:
        return _error(400, "invalid_webapp_themes_config", str(exc))

    config, _changed = ensure_webapp_core_themes(config, settings.WEBAPP_PRIMARY_COLOR or "#00fe7a")

    try:
        write_webapp_theme_dir(settings.WEBAPP_THEMES_DIR, config, delete_missing=True)
    except OSError as exc:
        logger.exception("Failed to write webapp themes to %s", settings.WEBAPP_THEMES_DIR)
        return _error(500, "write_failed", str(exc))

    cache = request.app.get("webapp_settings_cache")
    if isinstance(cache, dict):
        cache["ts"] = 0.0
        cache["data"] = {}

    return _ok(
        {
            "exists": True,
            "themes_dir": str(Path(settings.WEBAPP_THEMES_DIR).expanduser()),
            "catalog": _webapp_themes_catalog_payload(config),
        }
    )
