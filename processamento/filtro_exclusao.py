import json
import unicodedata
from pathlib import Path

_DATA_DIR = Path(__file__).parent.parent / "data"
_exclusoes: dict | None = None


def _carregar() -> dict:
    global _exclusoes
    if _exclusoes is None:
        path = _DATA_DIR / "exclusoes.json"
        _exclusoes = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    return _exclusoes


def _norm(texto: str) -> str:
    nfkd = unicodedata.normalize("NFKD", texto.lower())
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def verificar(titulo: str, corpo: str) -> str | None:
    """
    Retorna o slug do grupo de exclusão se o conteúdo bater em alguma keyword.
    Retorna None se o conteúdo é aceitável.
    """
    texto_n = _norm(titulo + " " + corpo[:1500])
    for slug, cfg in _carregar().items():
        for kw in cfg.get("keywords", []):
            if _norm(kw) in texto_n:
                return slug
    return None
