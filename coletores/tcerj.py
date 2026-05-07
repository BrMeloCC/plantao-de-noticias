import hashlib
import re
import time
from datetime import datetime
from urllib.parse import urljoin, urlparse, urlencode, parse_qsl, urlunparse

import requests
from bs4 import BeautifulSoup

_BASE = "https://www.tcerj.tc.br"
_LISTAGEM = f"{_BASE}/portalnovo/todas-noticias"
_HEADERS = {"User-Agent": "PlantaoDeNoticias/1.0 (monitoramento jornalistico municipal RJ)"}
_DELAY = 2.0

_MESES = {
    "jan": 1, "fev": 2, "mar": 3, "abr": 4, "mai": 5, "jun": 6,
    "jul": 7, "ago": 8, "set": 9, "out": 10, "nov": 11, "dez": 12,
}


def _normalizar_url(url: str) -> str:
    parsed = urlparse(url.lower().rstrip("/"))
    params = [(k, v) for k, v in parse_qsl(parsed.query) if not k.startswith("utm_")]
    return urlunparse(parsed._replace(query=urlencode(params), fragment=""))


def artigo_id(url: str) -> str:
    return hashlib.sha256(_normalizar_url(url).encode()).hexdigest()[:20]


def _parse_data_dom(card) -> str | None:
    bloco = card.find("div", class_="data")
    if not bloco:
        return None
    dia = bloco.find("span", class_="dia")
    mes_ano = bloco.find("span", class_="mes-ano")
    horario = bloco.find("span", class_="horario")
    if not (dia and mes_ano):
        return None
    try:
        dia_n = int(dia.get_text(strip=True))
        raw = mes_ano.get_text(strip=True).lower()       # "mai./2026"
        mes_str = raw[:3]
        ano = int(raw[-4:])
        mes_n = _MESES.get(mes_str)
        if not mes_n:
            return None
        hora, minuto = 0, 0
        if horario:
            m = re.search(r"(\d{1,2}):(\d{2})", horario.get_text())
            if m:
                hora, minuto = int(m.group(1)), int(m.group(2))
        return datetime(ano, mes_n, dia_n, hora, minuto).isoformat()
    except (ValueError, TypeError):
        return None


def _parse_data_slug(href: str) -> str | None:
    m = re.search(r"(\d{4})(\d{2})(\d{2})", href)
    if not m:
        return None
    try:
        return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3))).isoformat()
    except ValueError:
        return None


def _get(url: str) -> BeautifulSoup | None:
    try:
        r = requests.get(url, headers=_HEADERS, timeout=15)
        r.raise_for_status()
        return BeautifulSoup(r.text, "html.parser")
    except requests.RequestException:
        return None


def _corpo(url: str) -> str:
    soup = _get(url)
    if not soup:
        return ""
    area = (
        soup.find("div", class_=re.compile(r"noticia.?conteudo|article.?body|conteudo.?noticia", re.I))
        or soup.find("article")
        or soup.find("main")
        or soup
    )
    ps = area.find_all("p")
    return " ".join(p.get_text(separator=" ").strip() for p in ps if p.get_text(strip=True))


def coletar(fonte: dict, paginas: int = 1) -> list[dict]:
    agora = datetime.utcnow().isoformat()
    artigos = []
    seen: set[str] = set()

    for pagina in range(1, paginas + 1):
        url_pag = _LISTAGEM if pagina == 1 else f"{_LISTAGEM}?page={pagina}"
        soup = _get(url_pag)
        if not soup:
            if pagina == 1:
                raise RuntimeError("Falha ao acessar listagem TCE-RJ")
            break

        cards = soup.find_all("div", class_=lambda c: c and "d-flex" in c and "align-items-center" in c)
        if not cards:
            if pagina == 1:
                raise RuntimeError("Nenhum card encontrado na listagem TCE-RJ")
            break

        novos = 0
        for card in cards:
            a = card.find("h6", class_="mb-0")
            a = a.find("a", href=True) if a else None
            if not a:
                continue
            href = a["href"].strip()
            titulo = a.get_text(separator=" ").strip()
            if not href or len(titulo) < 10:
                continue
            url_art = urljoin(_BASE, href)
            if url_art in seen:
                continue
            seen.add(url_art)
            novos += 1

            data_pub = _parse_data_dom(card) or _parse_data_slug(href)
            preview_el = card.find("small")
            preview = preview_el.get_text(separator=" ").strip() if preview_el else ""

            time.sleep(_DELAY)
            corpo = _corpo(url_art) or preview
            artigos.append({
                "id": artigo_id(url_art),
                "url": url_art,
                "titulo": titulo,
                "corpo_texto": corpo,
                "data_publicacao": data_pub,
                "data_coleta": agora,
                "fonte_id": fonte["id"],
            })

        if novos == 0:
            break
        if pagina < paginas - 1:
            time.sleep(_DELAY)

    return artigos
