import re
from urllib.parse import quote

_WEB_FONTES_OFICIAIS = frozenset(["mprj", "tcerj", "alerj"])

_ACORDAO_RE = re.compile(
    r"ac[oó]rd[aã]o\s+n[°º.o]?\s*(\d[\d.\-\/]+)",
    re.IGNORECASE,
)
_PROCESSO_CNJ_RE = re.compile(
    r"\b(\d{7}-\d{2}\.\d{4}\.\d{1,2}\.\d{2}\.\d{4})\b"
)
_PORTARIA_RE = re.compile(
    r"portaria\s+(?:\S+\s+)?n[°º.o]?\s*(\d+\s*[/\-]\s*\d{4})",
    re.IGNORECASE,
)
_RESOLUCAO_RE = re.compile(
    r"resolu[cç][aã]o\s+(?:\S+\s+)?n[°º.o]?\s*(\d+\s*[/\-]\s*\d{4})",
    re.IGNORECASE,
)


def extrair_doc_url(artigo_url: str, fonte_id: str, titulo: str, corpo: str) -> str | None:
    if fonte_id in _WEB_FONTES_OFICIAIS:
        return artigo_url

    texto = titulo + " " + corpo[:3000]

    m = _ACORDAO_RE.search(texto)
    if m:
        ref = re.sub(r"\s+", " ", m.group(1).strip())
        q = quote(f"acórdão {ref}")
        return f"https://www.tcerj.tc.br/portalnovo/pesquisar?q={q}"

    m = _PROCESSO_CNJ_RE.search(texto)
    if m:
        numero = m.group(1)
        return f"https://www.mprj.mp.br/busca?filtro_param=noticias&q={quote(numero)}"

    m = _PORTARIA_RE.search(texto) or _RESOLUCAO_RE.search(texto)
    if m:
        ref = re.sub(r"\s+", " ", m.group(0)).strip()
        return f"https://www.mprj.mp.br/busca?filtro_param=noticias&q={quote(ref)}"

    return None
