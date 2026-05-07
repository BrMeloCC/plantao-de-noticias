import hashlib
from datetime import datetime
from urllib.parse import urlparse, urlencode, parse_qsl, urlunparse

import requests

_BASE = "https://www.alerj.rj.gov.br"
_API = f"{_BASE}/Listar/ConsultarNoticias"
_HEADERS = {
    "User-Agent": "PlantaoDeNoticias/1.0 (monitoramento jornalistico municipal RJ)",
    "X-Requested-With": "XMLHttpRequest",
    "Accept": "application/json",
    "Referer": f"{_BASE}/Listar/IndexNoticia",
}
_LIMITE = 25


def _normalizar_url(url: str) -> str:
    parsed = urlparse(url.lower().rstrip("/"))
    params = [(k, v) for k, v in parse_qsl(parsed.query) if not k.startswith("utm_")]
    return urlunparse(parsed._replace(query=urlencode(params), fragment=""))


def artigo_id(url: str) -> str:
    return hashlib.sha256(_normalizar_url(url).encode()).hexdigest()[:20]


def _parse_data(texto: str) -> str | None:
    # formato: "06.05.2026 - 18:35"
    try:
        return datetime.strptime(texto.strip(), "%d.%m.%Y - %H:%M").isoformat()
    except ValueError:
        return None


def coletar(fonte: dict, paginas: int = 1) -> list[dict]:
    agora = datetime.utcnow().isoformat()
    artigos = []
    vistos: set[str] = set()

    for pagina in range(1, paginas + 1):
        try:
            r = requests.get(
                _API,
                headers=_HEADERS,
                params={"pagina": pagina, "limite": _LIMITE, "order": "", "consultar": "true"},
                timeout=15,
            )
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            if pagina == 1:
                raise RuntimeError(f"Falha ao consultar API ALERJ: {e}")
            break

        lista = data.get("Lista") or []
        if not lista:
            if pagina == 1:
                raise RuntimeError("API ALERJ retornou lista vazia")
            break

        novos = 0
        for item in lista:
            nm_link = (item.get("NmLink") or "").strip()
            titulo = (item.get("NmTitulo") or "").strip()
            if not nm_link or not titulo:
                continue
            url_art = f"{_BASE}/{nm_link}"
            aid = artigo_id(url_art)
            if aid in vistos:
                continue
            vistos.add(aid)
            novos += 1
            artigos.append({
                "id": aid,
                "url": url_art,
                "titulo": titulo,
                "corpo_texto": (item.get("NmDescricao") or "").strip(),
                "data_publicacao": _parse_data(item.get("DataHoraPublicacao") or ""),
                "data_coleta": agora,
                "fonte_id": fonte["id"],
            })
        if novos == 0:
            break

    return artigos
