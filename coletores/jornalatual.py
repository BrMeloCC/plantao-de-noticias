import hashlib
import re
from datetime import datetime
from urllib.parse import urlparse, urlencode, parse_qsl, urlunparse

import requests

_API = "https://jornalatual.com.br/wp-json/wp/v2/posts"
_HEADERS = {"User-Agent": "PlantaoDeNoticias/1.0 (monitoramento jornalistico municipal RJ)"}
# cat 31 = Itaguaí, cat 32 = Seropédica
_CATS = "31,32"
_PER_PAGE = 20
_FIELDS = "id,date,title,link,excerpt"


def _normalizar_url(url: str) -> str:
    parsed = urlparse(url.lower().rstrip("/"))
    params = [(k, v) for k, v in parse_qsl(parsed.query) if not k.startswith("utm_")]
    return urlunparse(parsed._replace(query=urlencode(params), fragment=""))


def artigo_id(url: str) -> str:
    return hashlib.sha256(_normalizar_url(url).encode()).hexdigest()[:20]


def _strip_html(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def coletar(fonte: dict, paginas: int = 1) -> list[dict]:
    agora = datetime.utcnow().isoformat()
    artigos = []
    vistos: set[str] = set()

    for pagina in range(1, paginas + 1):
        try:
            r = requests.get(
                _API,
                headers=_HEADERS,
                params={
                    "categories": _CATS,
                    "per_page": _PER_PAGE,
                    "page": pagina,
                    "_fields": _FIELDS,
                    "orderby": "date",
                    "order": "desc",
                },
                timeout=15,
            )
            r.raise_for_status()
            posts = r.json()
        except Exception as e:
            if pagina == 1:
                raise RuntimeError(f"Falha ao consultar API Jornal Atual: {e}")
            break

        if not posts:
            break

        novos = 0
        for post in posts:
            url = post.get("link", "").strip()
            titulo = _strip_html(post.get("title", {}).get("rendered", ""))
            if not url or not titulo:
                continue
            aid = artigo_id(url)
            if aid in vistos:
                continue
            vistos.add(aid)
            novos += 1

            corpo = _strip_html(post.get("excerpt", {}).get("rendered", ""))
            artigos.append({
                "id": aid,
                "url": url,
                "titulo": titulo,
                "corpo_texto": corpo,
                "data_publicacao": post.get("date") or None,
                "data_coleta": agora,
                "fonte_id": fonte["id"],
            })

        if novos == 0:
            break

    return artigos
