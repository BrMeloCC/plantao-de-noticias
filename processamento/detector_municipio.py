import re
import unicodedata

_KEYWORDS_POLITICAS = frozenset([
    "prefeito", "prefeitura", "camara", "vereador", "secretaria", "secretario",
    "licitacao", "contrato", "obra", "servidor", "tce", "mpe", "mpf", "mprj",
    "improbidade", "inquerito", "acao penal", "milicia", "faccao", "desvio",
    "superfaturamento", "dispensa", "fraude", "denuncia", "fiscalizacao",
    "condenacao", "reu", "bloqueio", "suspensao", "irregularidade",
])


def _norm(texto: str) -> str:
    nfkd = unicodedata.normalize("NFKD", texto.lower())
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def _termo_exato(termo_n: str, texto_n: str) -> bool:
    return bool(re.search(r"(?<![a-z0-9])" + re.escape(termo_n) + r"(?![a-z0-9])", texto_n))


def _tem_contexto_politico(texto: str) -> bool:
    t = _norm(texto)
    return any(k in t for k in _KEYWORDS_POLITICAS)


def detectar(
    titulo: str,
    corpo: str,
    url: str,
    municipios_cobertos: list[str],
    municipios: dict,
) -> tuple[str | None, float]:
    """
    Retorna (slug_municipio, confianca) — confiança de 0.0 a 1.0.
    Abaixo de 0.50 é indeterminado e deve ser ignorado.
    """
    # Camada 1 — fonte exclusiva de município (valida se o artigo é realmente local)
    if municipios_cobertos != ["*"] and len(municipios_cobertos) == 1:
        slug = municipios_cobertos[0]
        dados = municipios.get(slug, {})
        texto_n = _norm(titulo + " " + corpo[:2000])
        for termo in dados.get("termos_exatos", []) + dados.get("termos_contextuais", []):
            if _termo_exato(_norm(termo), texto_n):
                return slug, 1.0
        curto_n = _norm(titulo + " " + corpo[:500])
        if any(_termo_exato(k, curto_n) for k in _KEYWORDS_POLITICAS):
            return slug, 0.80
        return slug, 0.20

    titulo_n = _norm(titulo)
    corpo_n = _norm(corpo[:2000])
    url_n = _norm(url)
    ctx_titulo = _tem_contexto_politico(titulo)
    ctx_corpo = _tem_contexto_politico(corpo[:2000])

    candidatos: dict[str, float] = {}

    for slug, dados in municipios.items():
        slug_n = _norm(slug)
        nome_n = _norm(dados["nome"])
        conf = 0.0

        # Camada 2 — slug ou nome na URL
        if _termo_exato(slug_n, url_n) or _termo_exato(nome_n, url_n):
            conf = max(conf, 0.95)

        # Camada 3 — termo exato no título
        for termo in dados.get("termos_exatos", []):
            if _termo_exato(_norm(termo), titulo_n):
                conf = max(conf, 0.85)
                break

        # Camada 4a — termo exato no corpo com contexto político
        if conf < 0.70:
            for termo in dados.get("termos_exatos", []):
                if _termo_exato(_norm(termo), corpo_n) and ctx_corpo:
                    conf = max(conf, 0.70)
                    break

        # Camada 4b — termo contextual no título com keyword política
        if conf < 0.65:
            for termo in dados.get("termos_contextuais", []):
                if _norm(termo) in titulo_n and ctx_titulo:
                    conf = max(conf, 0.65)
                    break

        # Camada 4c — termo contextual no corpo com keyword política
        if conf < 0.55:
            for termo in dados.get("termos_contextuais", []):
                if _norm(termo) in corpo_n and ctx_corpo:
                    conf = max(conf, 0.55)
                    break

        if conf > 0:
            candidatos[slug] = conf

    if not candidatos:
        return None, 0.0

    melhor = max(candidatos, key=candidatos.get)
    return melhor, candidatos[melhor]
