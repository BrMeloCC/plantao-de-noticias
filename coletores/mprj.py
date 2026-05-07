import hashlib
import re
import time
from datetime import datetime
from urllib.parse import urlparse, urlencode, parse_qsl, urlunparse

import requests
from bs4 import BeautifulSoup

_BASE = "https://www.mprj.mp.br"
_PP = "br_mp_mprj_internet_busca_web_BuscaPortlet"
_GET_URL = f"{_BASE}/busca?filtro_param=noticias"
_HEADERS = {"User-Agent": "PlantaoDeNoticias/1.0 (monitoramento jornalistico municipal RJ)"}
_PAGINAS_PADRAO = 2
_DELAY = 1.5


def _normalizar_url(url: str) -> str:
    parsed = urlparse(url.lower().rstrip("/"))
    params = [(k, v) for k, v in parse_qsl(parsed.query) if not k.startswith("utm_")]
    return urlunparse(parsed._replace(query=urlencode(params), fragment=""))


def artigo_id(url: str) -> str:
    return hashlib.sha256(_normalizar_url(url).encode()).hexdigest()[:20]


def _parse_data(texto: str) -> str | None:
    for fmt in ("%d/%m/%Y %H:%M", "%d/%m/%Y"):
        try:
            return datetime.strptime(texto.strip(), fmt).isoformat()
        except ValueError:
            pass
    return None


def _corpo_artigo(sess: requests.Session, url: str) -> str:
    try:
        r = sess.get(url, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
    except requests.RequestException:
        return ""
    area = (
        soup.find("div", class_=re.compile(r"noticia.?conteudo|content.?res.?busca|article.?body", re.I))
        or soup.find("article")
        or soup.find("main")
        or soup
    )
    ps = area.find_all("p")
    return " ".join(p.get_text(separator=" ").strip() for p in ps if p.get_text(strip=True))


def coletar(fonte: dict, paginas: int = _PAGINAS_PADRAO) -> list[dict]:
    agora = datetime.utcnow().isoformat()
    artigos = []

    sess = requests.Session()
    sess.headers.update(_HEADERS)

    r_get = sess.get(_GET_URL, timeout=15)
    if not r_get.ok:
        raise RuntimeError(f"Falha ao acessar MPRJ (HTTP {r_get.status_code})")
    soup_get = BeautifulSoup(r_get.text, "html.parser")
    form = soup_get.find("form", id="acervo-admin-dynamic-content")
    if not form:
        raise RuntimeError("Formulário MPRJ não encontrado na página")
    base_data = {inp["name"]: inp.get("value", "")
                 for inp in form.find_all("input", type="hidden") if inp.get("name")}
    action = form.get("action") or _GET_URL

    for pagina in range(paginas):
        post_data = {
            **base_data,
            f"_{_PP}_filtro_param": "noticias",
            f"_{_PP}_keywords": "",
        }
        if pagina > 0:
            post_data[f"_{_PP}_cur"] = str(pagina * 15)

        r_post = sess.post(action, data=post_data, timeout=15)
        if not r_post.ok:
            raise RuntimeError(f"Falha no POST MPRJ (pág. {pagina + 1}, HTTP {r_post.status_code})")

        soup = BeautifulSoup(r_post.text, "html.parser")
        container = soup.find("div", id="container-busca")
        if not container:
            if pagina == 0:
                raise RuntimeError("Container de resultados MPRJ não encontrado")
            break

        links = container.find_all("a", href=lambda h: h and "noticiaId=" in h)
        if not links:
            break

        for a in links:
            href = a.get("href", "").strip()
            if not href:
                continue
            url = f"{_BASE}{href}" if href.startswith("/") else href

            item = a.find("div", class_="content-res-busca")
            if not item:
                continue
            h3 = item.find("h3")
            titulo = h3.get_text(separator=" ").strip() if h3 else ""
            if not titulo:
                continue

            data_el = item.find("div", class_="data")
            data_pub = _parse_data(data_el.get_text()) if data_el else None
            preview_el = item.find("div", class_="span-res-busca")
            preview = preview_el.get_text(separator=" ").strip() if preview_el else ""

            time.sleep(_DELAY)
            corpo = _corpo_artigo(sess, url) or preview

            artigos.append({
                "id": artigo_id(url),
                "url": url,
                "titulo": titulo,
                "corpo_texto": corpo,
                "data_publicacao": data_pub,
                "data_coleta": agora,
                "fonte_id": fonte["id"],
            })

        if pagina < paginas - 1:
            time.sleep(_DELAY)

    return artigos
