import json
from datetime import datetime
from pathlib import Path

import db

_DATA_DIR = Path(__file__).parent.parent / "data"

_RISCO_LABEL = {"alto": "🔴 Alto", "medio": "🟡 Médio", "baixo": "🟢 Baixo"}

_MUNICIPIO_NOME = {
    "nova-iguacu": "Nova Iguaçu",
    "duque-de-caxias": "Duque de Caxias",
    "sao-joao-de-meriti": "São João de Meriti",
    "belford-roxo": "Belford Roxo",
    "nilopolis": "Nilópolis",
    "mesquita": "Mesquita",
    "queimados": "Queimados",
    "japeri": "Japeri",
    "mage": "Magé",
    "guapimirim": "Guapimirim",
    "seropedica": "Seropédica",
    "itaguai": "Itaguaí",
    "paracambi": "Paracambi",
    "rio-de-janeiro": "Rio de Janeiro",
}


def _load_tema_nomes() -> dict:
    path = _DATA_DIR / "temas.json"
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        return {slug: cfg["nome"] for slug, cfg in data.items()}
    return {}


_TEMA_NOME = _load_tema_nomes()


def _nome_municipio(slug: str) -> str:
    return _MUNICIPIO_NOME.get(slug, slug.replace("-", " ").title())


def _nome_tema(slug: str) -> str:
    return _TEMA_NOME.get(slug, slug.replace("-", " ").title())


def gerar(data_str: str, data_fim: str = None, top_n: int = 10, municipio: str = None, tema: str = None, db_path=None) -> str:
    pautas = db.buscar_pautas_do_dia(data_str, data_fim=data_fim, municipio=municipio, tema=tema, top_n=top_n, db_path=db_path)

    periodo = f"{data_str} a {data_fim}" if data_fim and data_fim != data_str else data_str

    if not pautas:
        return (
            f"# Plantão de Notícias — {periodo}\n\n"
            "Nenhuma pauta encontrada para os filtros aplicados.\n"
        )

    conn = db.get_conn(db_path)
    artigos_info: dict[str, dict] = {}
    for p in pautas:
        aid = p["artigo_principal_id"]
        row = conn.execute("SELECT url, fonte_id FROM artigos WHERE id = ?", (aid,)).fetchone()
        if row:
            artigos_info[aid] = dict(row)
    conn.close()

    gerado_em = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    linhas = [
        f"# Plantão de Notícias — Relatório Diário",
        f"> **Data:** {periodo}  ",
        f"> **Pautas:** {len(pautas)}  ",
        f"> **Gerado em:** {gerado_em}",
        "",
        "---",
        "",
    ]

    for i, pauta in enumerate(pautas, 1):
        artigo = artigos_info.get(pauta["artigo_principal_id"], {})
        data_fato = (pauta.get("data_fato") or data_str)[:10]
        documento = pauta.get("documento_oficial_url") or "_não encontrado_"
        fonte_url = artigo.get("url", "#")
        fonte_nome = artigo.get("fonte_id", "fonte desconhecida")

        linhas += [
            f"## PAUTA #{i} — {_nome_municipio(pauta['municipio'])} — {data_fato}",
            "",
            f"**Tema:** {_nome_tema(pauta['tema'])}  ",
            f"**Qualidade:** Tier {pauta['tier']} · Score {pauta['score']:.1f}  ",
            f"**Risco jurídico:** {_RISCO_LABEL.get(pauta['risco_juridico'], pauta['risco_juridico'])}  ",
            f"**Cobertura cruzada:** {pauta['cobertura_cruzada']} fonte(s)",
            "",
            "**Resumo:**  ",
            pauta.get("resumo") or "_sem resumo disponível_",
            "",
            f"**Fonte principal:** [{fonte_nome}]({fonte_url})  ",
            f"**Documento oficial:** {documento}",
            "",
            "---",
            "",
        ]

    return "\n".join(linhas)


def _nome_arquivo(data_str: str, data_fim: str = None, municipio: str = None, tema: str = None) -> str:
    partes = [data_str]
    if data_fim and data_fim != data_str:
        partes += ["a", data_fim]
    if municipio:
        partes.append(municipio)
    if tema:
        partes.append(tema)
    return "_".join(partes) + ".md"


def salvar(conteudo: str, data_str: str, data_fim: str = None, municipio: str = None, tema: str = None, output_dir: str = "relatorios") -> Path:
    path = Path(output_dir) / _nome_arquivo(data_str, data_fim, municipio, tema)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(conteudo, encoding="utf-8")
    return path
