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


_BLOGGER_TAG = "feeds/posts/default"
_BLOGGER_MAX = 25


def _urls_paginadas(base_url: str, paginas: int) -> list[str]:
    if paginas <= 1:
        return [base_url]
    if _BLOGGER_TAG in base_url:
        # Blogger: ?start-index=26&max-results=25
        sep = "&" if "?" in base_url else "?"
        return [base_url] + [
            f"{base_url}{sep}start-index={1 + p * _BLOGGER_MAX}&max-results={_BLOGGER_MAX}"
            for p in range(1, paginas)
        ]
    # WordPress e compatíveis: ?paged=N
    sep = "&" if "?" in base_url else "?"
    return [base_url] + [f"{base_url.rstrip('/')}{sep}paged={p}" for p in range(2, paginas + 1)]


def coletar(fonte: dict, paginas: int = 1) -> list[dict]:
    base_url = fonte["url_feed"]
    urls = _urls_paginadas(base_url, paginas)

    agora = datetime.utcnow().isoformat()
    artigos: list[dict] = []
    vistos: set[str] = set()

    for url in urls:
        feed = feedparser.parse(url, request_headers=_HEADERS)
        if feed.bozo and not feed.entries:
            if url == base_url:
                raise RuntimeError(f"Feed inválido: {feed.bozo_exception}")
            break

        novos = 0
        for entry in feed.entries:
            link = entry.get("link", "").strip()
            if not link:
                continue
            aid = artigo_id(link)
            if aid in vistos:
                continue
            vistos.add(aid)
            novos += 1
            artigos.append({
                "id": aid,
                "url": link,
                "titulo": entry.get("title", "").strip(),
                "corpo_texto": _extrair_texto(entry),
                "data_publicacao": _parse_data(entry),
                "data_coleta": agora,
                "fonte_id": fonte["id"],
            })
        if novos == 0:
            break

    return artigos
