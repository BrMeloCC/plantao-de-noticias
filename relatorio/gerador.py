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
    "estado-rio": "Estado do Rio",
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


def _render_pautas(linhas: list, pautas: list, artigos_info: dict, data_str: str, prefixo: str = "PAUTA") -> None:
    for i, pauta in enumerate(pautas, 1):
        artigo = artigos_info.get(pauta["artigo_principal_id"], {})
        data_fato = (pauta.get("data_fato") or data_str)[:10]
        fonte_url = artigo.get("url", "#")
        fonte_nome = artigo.get("fonte_nome", "fonte desconhecida")
        doc_url = pauta.get("documento_oficial_url")

        linhas += [
            f"## {prefixo} #{i} — {_nome_municipio(pauta['municipio'])} — {data_fato}",
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
        ]
        if doc_url:
            linhas.append(f"**Documento oficial:** {doc_url}")
        linhas += ["", "---", ""]


def gerar(data_str: str, data_fim: str = None, top_n: int = 10, municipio: str = None, tema: str = None, incluir_outros: bool = False, db_path=None) -> str:
    mostrar_estado = municipio is None

    pautas = db.buscar_pautas_do_dia(
        data_str, data_fim=data_fim, municipio=municipio,
        municipio_excluir="estado-rio" if mostrar_estado else None,
        tema=tema, top_n=top_n, incluir_outros=incluir_outros, db_path=db_path,
    )

    pautas_estado = []
    if mostrar_estado:
        pautas_estado = db.buscar_pautas_do_dia(
            data_str, data_fim=data_fim, municipio="estado-rio",
            top_n=5, incluir_outros=incluir_outros, db_path=db_path,
        )

    periodo = f"{data_str} a {data_fim}" if data_fim and data_fim != data_str else data_str

    if not pautas and not pautas_estado:
        return (
            f"# Plantão de Notícias — {periodo}\n\n"
            "Nenhuma pauta encontrada para os filtros aplicados.\n"
        )

    todas = pautas + pautas_estado
    conn = db.get_conn(db_path)
    artigos_info: dict[str, dict] = {}
    ids = [p["artigo_principal_id"] for p in todas]
    placeholders = ",".join("?" * len(ids))
    rows = conn.execute(
        f"SELECT a.id, a.url, COALESCE(f.nome, a.fonte_id) AS fonte_nome"
        f" FROM artigos a LEFT JOIN fontes f ON a.fonte_id = f.id"
        f" WHERE a.id IN ({placeholders})",
        ids,
    ).fetchall()
    for row in rows:
        artigos_info[row["id"]] = dict(row)
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

    _render_pautas(linhas, pautas, artigos_info, data_str)

    if pautas_estado:
        linhas += [
            "# Estado do Rio — Destaques",
            "",
            "---",
            "",
        ]
        _render_pautas(linhas, pautas_estado, artigos_info, data_str, prefixo="ESTADO")

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
