import hashlib
import re
from datetime import datetime
from urllib.parse import urlparse, urlencode, parse_qsl, urlunparse

import feedparser

_HEADERS = {"User-Agent": "PlantaoDeNoticias/1.0 (monitoramento jornalistico municipal RJ)"}
_TAG_RE = re.compile(r"<[^>]+>")


def _normalizar_url(url: str) -> str:
    parsed = urlparse(url.lower().rstrip("/"))
    params = [(k, v) for k, v in parse_qsl(parsed.query) if not k.startswith("utm_")]
    return urlunparse(parsed._replace(query=urlencode(params), fragment=""))


def artigo_id(url: str) -> str:
    return hashlib.sha256(_normalizar_url(url).encode()).hexdigest()[:20]


def _extrair_texto(entry) -> str:
    raw = ""
    if hasattr(entry, "content") and entry.content:
        raw = entry.content[0].get("value", "")
    elif hasattr(entry, "summary"):
        raw = entry.summary or ""
    elif hasattr(entry, "description"):
        raw = entry.description or ""
    return _TAG_RE.sub(" ", raw).strip()


def _parse_data(entry) -> str | None:
    for attr in ("published_parsed", "updated_parsed"):
        val = getattr(entry, attr, None)
        if val:
            try:
                return datetime(*val[:6]).isoformat()
            except (TypeError, ValueError):
                pass
    return None


def coletar(fonte: dict) -> list[dict]:
    """Coleta todos os itens de uma fonte RSS. Lança RuntimeError em caso de falha."""
    feed = feedparser.parse(fonte["url_feed"], request_headers=_HEADERS)

    if feed.bozo and not feed.entries:
        raise RuntimeError(f"Feed inválido: {feed.bozo_exception}")

    agora = datetime.utcnow().isoformat()
    artigos = []

    for entry in feed.entries:
        url = entry.get("link", "").strip()
        if not url:
            continue
        artigos.append(
            {
                "id": artigo_id(url),
                "url": url,
                "titulo": entry.get("title", "").strip(),
                "corpo_texto": _extrair_texto(entry),
                "data_publicacao": _parse_data(entry),
                "data_coleta": agora,
                "fonte_id": fonte["id"],
            }
        )

    return artigos
