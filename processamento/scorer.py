import json
from datetime import datetime, timezone
from pathlib import Path

_DATA_DIR = Path(__file__).parent.parent / "data"

_TIER_BASE = {"A": 10, "B": 7, "C": 4, "D": 0}

_RECENCIA = [
    (0, 1.00),
    (1, 0.85),
    (2, 0.70),
    (5, 0.55),
    (14, 0.40),
]
_RECENCIA_ANTIGO = 0.25

_DOCS_OFICIAIS = frozenset([
    "tce-rj", "tcerj", "mprj", "mpf", "doerj", "acórdão", "acordao",
    "sentença", "sentenca", "resolução", "resolucao", "portaria",
])

_TEMA_PADRAO = "improbidade-administrativa"


def _load_temas() -> dict:
    path = _DATA_DIR / "temas.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


_TEMAS_CONFIG = _load_temas()


def inferir_tema(titulo: str, corpo: str) -> str:
    texto = (titulo + " " + corpo[:1000]).lower()
    for slug, cfg in _TEMAS_CONFIG.items():
        if any(k in texto for k in cfg.get("keywords", [])):
            return slug
    return _TEMA_PADRAO


def _fator_recencia(data_fato: str | None) -> float:
    if not data_fato:
        return 0.70
    try:
        dt = datetime.fromisoformat(data_fato.replace("Z", "+00:00"))
        agora = datetime.now(timezone.utc) if dt.tzinfo else datetime.utcnow()
        dias = max((agora - dt).days, 0)
        for limite, fator in _RECENCIA:
            if dias <= limite:
                return fator
        return _RECENCIA_ANTIGO
    except (ValueError, TypeError):
        return 0.70


def calcular_score(
    tier: str,
    cobertura_cruzada: int,
    tem_documento_oficial: bool,
    data_fato: str | None,
    tema: str | None = None,
    municipio_boost: int = 0,
) -> tuple[float, dict]:
    base = _TIER_BASE.get(tier, 0)
    cobertura_bonus = min((cobertura_cruzada - 1) * 2, 6)
    doc_bonus = 5 if tem_documento_oficial else 0
    recencia = _fator_recencia(data_fato)
    peso = _TEMAS_CONFIG.get(tema or _TEMA_PADRAO, {}).get("peso", 1.0)
    score = round((base + cobertura_bonus + doc_bonus + municipio_boost) * recencia * peso, 2)
    return score, {
        "tier_base": base,
        "cobertura_bonus": cobertura_bonus,
        "documento_bonus": doc_bonus,
        "fator_recencia": recencia,
        "municipio_boost": municipio_boost,
        "peso_tema": peso,
        "score_final": score,
    }


def inferir_risco(tema: str, tier: str, cobertura_cruzada: int, tem_documento_oficial: bool) -> str:
    if tier == "D":
        return "alto"
    if tema == "crime-organizado":
        return "medio" if tem_documento_oficial else "alto"
    if not tem_documento_oficial and cobertura_cruzada == 1 and tema in (
        "improbidade-administrativa", "compra-de-voto", "licitacao-suspeita"
    ):
        return "medio"
    if tem_documento_oficial:
        return "baixo"
    return "medio"


def tem_documento_oficial(titulo: str, corpo: str) -> bool:
    texto = (titulo + " " + corpo[:2000]).lower()
    return any(k in texto for k in _DOCS_OFICIAIS)
