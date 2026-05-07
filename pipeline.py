#!/usr/bin/env python3
"""
Plantão de Notícias — Pipeline principal.

Uso:
  python pipeline.py
  python pipeline.py --data 2026-05-06
  python pipeline.py --municipio belford-roxo --top 5
"""
import argparse
import json
import uuid
from datetime import date, datetime
from pathlib import Path

import db
from coletores import alerj as _coletor_alerj
from coletores import mprj as _coletor_mprj
from coletores import rss
from coletores import tcerj as _coletor_tcerj
from processamento import detector_municipio, scorer
from relatorio import gerador

_DATA_DIR = Path(__file__).parent / "data"
_CONFIANCA_MINIMA = 0.50
_JACCARD_MIN = 0.55
_WEB_COLETORES = {
    "mprj": _coletor_mprj,
    "tcerj": _coletor_tcerj,
    "alerj": _coletor_alerj,
}


def _jaccard_bigramas(a: str, b: str) -> float:
    bg = lambda s: {s[i : i + 2] for i in range(len(s) - 1)}
    A, B = bg(a.lower()), bg(b.lower())
    return len(A & B) / len(A | B) if A | B else 0.0


def _resumo(titulo: str, corpo: str) -> str:
    texto = corpo.strip() or titulo
    if len(texto) <= 280:
        return texto
    return texto[:280].rsplit(" ", 1)[0] + "…"


def _processar(artigo: dict, fonte: dict, municipios: dict, data_hoje: str):
    """Enriquece artigo e cria pauta. Retorna (artigo, pauta|None)."""
    cobertos = json.loads(fonte.get("municipios_cobertos", '["*"]'))

    slug, confianca = detector_municipio.detectar(
        titulo=artigo["titulo"],
        corpo=artigo.get("corpo_texto", ""),
        url=artigo["url"],
        municipios_cobertos=cobertos,
        municipios=municipios,
    )

    artigo["municipio"] = slug
    artigo["confianca_municipio"] = confianca

    if confianca < _CONFIANCA_MINIMA:
        artigo["status"] = "ignorado"
        return artigo, None

    titulo = artigo["titulo"]
    corpo = artigo.get("corpo_texto", "")
    tem_doc = scorer.tem_documento_oficial(titulo, corpo)
    tema = scorer.inferir_tema(titulo, corpo)
    boost = municipios.get(slug, {}).get("boost", 0)
    score_val, breakdown = scorer.calcular_score(
        tier=fonte["tier"],
        cobertura_cruzada=1,
        tem_documento_oficial=tem_doc,
        data_fato=artigo.get("data_publicacao"),
        tema=tema,
        municipio_boost=boost,
    )
    risco = scorer.inferir_risco(tema, fonte["tier"], 1, tem_doc)

    if fonte["tier"] == "D" and risco == "alto":
        artigo["status"] = "ignorado"
        return artigo, None

    pauta = {
        "id": str(uuid.uuid4()),
        "titulo": titulo,
        "municipio": slug,
        "tema": tema,
        "resumo": _resumo(titulo, corpo),
        "artigo_principal_id": artigo["id"],
        "artigos_secundarios_ids": [],
        "documento_oficial_url": None,
        "tier": fonte["tier"],
        "score": score_val,
        "score_breakdown": breakdown,
        "cobertura_cruzada": 1,
        "risco_juridico": risco,
        "status": "pendente_humano",
        "data_fato": (artigo.get("data_publicacao") or data_hoje)[:10],
        "data_geracao": f"{data_hoje}T{datetime.utcnow().strftime('%H:%M:%S')}",
    }
    return artigo, pauta


def _pauta_existente(pauta: dict, db_path=None) -> str | None:
    recentes = db.buscar_pautas_recentes_por_municipio(pauta["municipio"], horas=48, db_path=db_path)
    for existente in recentes:
        if _jaccard_bigramas(pauta["titulo"], existente["titulo"]) >= _JACCARD_MIN:
            return existente["id"]
    return None


def run(data_str: str, data_fim: str = None, municipio: str = None, tema: str = None, top_n: int = 10, paginas: int = 1, incluir_outros: bool = False, db_path=None) -> Path:
    print(f"\n{'=' * 50}")
    print(f"  Plantão de Notícias — {data_str}")
    print(f"{'=' * 50}\n")

    fontes_json = json.loads((_DATA_DIR / "fontes.json").read_text(encoding="utf-8"))
    municipios = json.loads((_DATA_DIR / "municipios.json").read_text(encoding="utf-8"))

    db.init_db(db_path)
    db.sincronizar_fontes(fontes_json, db_path)

    fontes_ativas = [
        f for f in db.carregar_fontes(db_path)
        if f["tipo_acesso"] == "rss" or (f["tipo_acesso"] == "web" and f["id"] in _WEB_COLETORES)
    ]
    print(f"Fontes ativas: {len(fontes_ativas)}\n")

    novos_artigos = ignorados = novas_pautas = cruzamentos = 0

    for fonte in fontes_ativas:
        print(f"  -> {fonte['nome']}...", end=" ", flush=True)
        try:
            if fonte["tipo_acesso"] == "rss":
                artigos = rss.coletar(fonte, paginas=paginas)
            else:
                artigos = _WEB_COLETORES[fonte["id"]].coletar(fonte, paginas=paginas)
            db.marcar_fonte_coletada(fonte["id"], db_path)
            print(f"{len(artigos)} itens")
        except RuntimeError as e:
            print(f"ERRO — {e}")
            db.marcar_fonte_falha(fonte["id"], db_path)
            continue

        for artigo_raw in artigos:
            if db.artigo_existe(artigo_raw["id"], db_path):
                continue

            artigo, pauta = _processar(artigo_raw, fonte, municipios, data_str)
            db.salvar_artigo(artigo, db_path)
            novos_artigos += 1

            if pauta is None:
                ignorados += 1
                continue

            existente_id = _pauta_existente(pauta, db_path)
            if existente_id:
                db.incrementar_cobertura(existente_id, artigo["id"], db_path)
                cruzamentos += 1
            else:
                db.salvar_pauta(pauta, db_path)
                novas_pautas += 1

    print(f"\nResultado:")
    print(f"  Novos artigos coletados : {novos_artigos}")
    print(f"  Ignorados (sem município): {ignorados}")
    print(f"  Novas pautas geradas    : {novas_pautas}")
    print(f"  Coberturas cruzadas     : {cruzamentos}")

    conteudo = gerador.gerar(data_str, data_fim=data_fim, top_n=top_n, municipio=municipio, tema=tema, incluir_outros=incluir_outros, db_path=db_path)
    caminho = gerador.salvar(conteudo, data_str, data_fim=data_fim, municipio=municipio, tema=tema)
    print(f"\nRelatório salvo em: {caminho}\n")
    return caminho


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plantão de Notícias — Coletor de pautas")
    parser.add_argument("--data", default=date.today().isoformat(), help="Data inicial YYYY-MM-DD (padrão: hoje)")
    parser.add_argument("--data-fim", default=None, dest="data_fim", help="Data final do relatório YYYY-MM-DD (padrão: igual a --data)")
    parser.add_argument("--municipio", default=None, help="Filtrar por município (slug, ex: belford-roxo)")
    parser.add_argument("--tema", default=None, help="Filtrar por tema (slug, ex: crime-organizado)")
    parser.add_argument("--top", type=int, default=10, help="Top N pautas no relatório (padrão: 10)")
    parser.add_argument("--paginas", type=int, default=1, help="Páginas por fonte (padrão: 1 = coleta rápida; use 10+ para backfill histórico)")
    parser.add_argument("--incluir-outros", action="store_true", dest="incluir_outros",
        help="Incluir pautas com tema 'outros' no relatório (excluídas por padrão)")
    parser.add_argument("--db", default=None, help="Caminho para o arquivo SQLite")
    args = parser.parse_args()

    run(data_str=args.data, data_fim=args.data_fim, municipio=args.municipio, tema=args.tema, top_n=args.top, paginas=args.paginas, incluir_outros=args.incluir_outros, db_path=args.db)
