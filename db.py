import json
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "db" / "plantao.db"

_CREATE_FONTES = """
CREATE TABLE IF NOT EXISTS fontes (
    id TEXT PRIMARY KEY,
    nome TEXT NOT NULL,
    tier TEXT NOT NULL,
    tipo_acesso TEXT,
    url_feed TEXT,
    municipios_cobertos TEXT DEFAULT '["*"]',
    ativo INTEGER DEFAULT 1,
    ultima_coleta TEXT,
    falhas_consecutivas INTEGER DEFAULT 0
)"""

_CREATE_ARTIGOS = """
CREATE TABLE IF NOT EXISTS artigos (
    id TEXT PRIMARY KEY,
    url TEXT UNIQUE NOT NULL,
    titulo TEXT,
    corpo_texto TEXT,
    data_publicacao TEXT,
    data_coleta TEXT,
    fonte_id TEXT,
    municipio TEXT,
    confianca_municipio REAL DEFAULT 0,
    status TEXT DEFAULT 'novo',
    FOREIGN KEY (fonte_id) REFERENCES fontes(id)
)"""

_CREATE_PAUTAS = """
CREATE TABLE IF NOT EXISTS pautas (
    id TEXT PRIMARY KEY,
    titulo TEXT,
    municipio TEXT,
    tema TEXT,
    resumo TEXT,
    artigo_principal_id TEXT,
    artigos_secundarios_ids TEXT DEFAULT '[]',
    documento_oficial_url TEXT,
    tier TEXT,
    score REAL DEFAULT 0,
    score_breakdown TEXT DEFAULT '{}',
    cobertura_cruzada INTEGER DEFAULT 1,
    risco_juridico TEXT DEFAULT 'medio',
    status TEXT DEFAULT 'pendente_humano',
    data_fato TEXT,
    data_geracao TEXT,
    FOREIGN KEY (artigo_principal_id) REFERENCES artigos(id)
)"""


def get_conn(db_path=None) -> sqlite3.Connection:
    path = Path(db_path) if db_path else DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path=None):
    conn = get_conn(db_path)
    with conn:
        conn.execute(_CREATE_FONTES)
        conn.execute(_CREATE_ARTIGOS)
        conn.execute(_CREATE_PAUTAS)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_artigos_municipio ON artigos(municipio)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_pautas_score ON pautas(score DESC)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_pautas_municipio_data ON pautas(municipio, data_geracao)")
    conn.close()


def sincronizar_fontes(fontes_json: list, db_path=None):
    conn = get_conn(db_path)
    with conn:
        for f in fontes_json:
            ativo = 1 if f.get("ativo", True) else 0
            conn.execute(
                """INSERT INTO fontes (id, nome, tier, tipo_acesso, url_feed, municipios_cobertos, ativo)
                   VALUES (?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(id) DO UPDATE SET
                     nome = excluded.nome,
                     tier = excluded.tier,
                     url_feed = excluded.url_feed,
                     municipios_cobertos = excluded.municipios_cobertos,
                     ativo = excluded.ativo""",
                (
                    f["id"], f["nome"], f["tier"], f["tipo_acesso"],
                    f.get("url_feed"), json.dumps(f.get("municipios_cobertos", ["*"])),
                    ativo,
                ),
            )
    conn.close()


def carregar_fontes(db_path=None) -> list[dict]:
    conn = get_conn(db_path)
    rows = conn.execute("SELECT * FROM fontes WHERE ativo = 1").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def artigo_existe(artigo_id: str, db_path=None) -> bool:
    conn = get_conn(db_path)
    row = conn.execute("SELECT 1 FROM artigos WHERE id = ?", (artigo_id,)).fetchone()
    conn.close()
    return row is not None


def salvar_artigo(artigo: dict, db_path=None):
    conn = get_conn(db_path)
    with conn:
        conn.execute(
            """INSERT OR IGNORE INTO artigos
               (id, url, titulo, corpo_texto, data_publicacao, data_coleta,
                fonte_id, municipio, confianca_municipio, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                artigo["id"], artigo["url"], artigo.get("titulo", ""),
                artigo.get("corpo_texto", ""), artigo.get("data_publicacao"),
                artigo["data_coleta"], artigo["fonte_id"],
                artigo.get("municipio"), artigo.get("confianca_municipio", 0),
                artigo.get("status", "novo"),
            ),
        )
    conn.close()


def salvar_pauta(pauta: dict, db_path=None):
    conn = get_conn(db_path)
    with conn:
        conn.execute(
            """INSERT OR REPLACE INTO pautas
               (id, titulo, municipio, tema, resumo, artigo_principal_id,
                artigos_secundarios_ids, documento_oficial_url, tier, score,
                score_breakdown, cobertura_cruzada, risco_juridico, status,
                data_fato, data_geracao)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                pauta["id"], pauta["titulo"], pauta["municipio"],
                pauta["tema"], pauta["resumo"], pauta["artigo_principal_id"],
                json.dumps(pauta.get("artigos_secundarios_ids", [])),
                pauta.get("documento_oficial_url"), pauta["tier"],
                pauta["score"], json.dumps(pauta.get("score_breakdown", {})),
                pauta.get("cobertura_cruzada", 1), pauta["risco_juridico"],
                pauta.get("status", "pendente_humano"),
                pauta.get("data_fato"), pauta["data_geracao"],
            ),
        )
    conn.close()


def buscar_pautas_do_dia(data: str, data_fim: str = None, municipio: str = None, tema: str = None, top_n: int = 10, incluir_outros: bool = False, db_path=None) -> list[dict]:
    conn = get_conn(db_path)
    fim = data_fim or data
    params: list = [data, fim]
    query = "SELECT * FROM pautas WHERE date(data_fato) BETWEEN ? AND ? AND status != 'rejeitado'"
    if municipio:
        query += " AND municipio = ?"
        params.append(municipio)
    if tema:
        query += " AND tema = ?"
        params.append(tema)
    elif not incluir_outros:
        query += " AND tema != 'outros'"
    query += " ORDER BY score DESC LIMIT ?"
    params.append(top_n)
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def buscar_pautas_recentes_por_municipio(municipio: str, horas: int = 48, db_path=None) -> list[dict]:
    conn = get_conn(db_path)
    rows = conn.execute(
        """SELECT id, titulo FROM pautas
           WHERE municipio = ? AND data_geracao >= datetime('now', ?)
           ORDER BY data_geracao DESC""",
        (municipio, f"-{horas} hours"),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def incrementar_cobertura(pauta_id: str, artigo_id: str, db_path=None):
    conn = get_conn(db_path)
    with conn:
        row = conn.execute(
            "SELECT artigos_secundarios_ids, cobertura_cruzada, score_breakdown, tier FROM pautas WHERE id = ?",
            (pauta_id,),
        ).fetchone()
        if not row:
            return
        secundarios = json.loads(row["artigos_secundarios_ids"])
        if artigo_id in secundarios:
            return
        secundarios.append(artigo_id)
        nova_cobertura = row["cobertura_cruzada"] + 1
        breakdown = json.loads(row["score_breakdown"] or "{}")
        novo_bonus = min((nova_cobertura - 1) * 2, 6)
        novo_score = round(
            (breakdown.get("tier_base", 0) + novo_bonus + breakdown.get("documento_bonus", 0)
             + breakdown.get("municipio_boost", 0))
            * breakdown.get("fator_recencia", 0.70)
            * breakdown.get("peso_tema", 1.0),
            2,
        )
        breakdown["cobertura_bonus"] = novo_bonus
        breakdown["score_final"] = novo_score
        conn.execute(
            """UPDATE pautas
               SET artigos_secundarios_ids = ?, cobertura_cruzada = ?, score = ?, score_breakdown = ?
               WHERE id = ?""",
            (json.dumps(secundarios), nova_cobertura, novo_score, json.dumps(breakdown), pauta_id),
        )
    conn.close()


def marcar_fonte_coletada(fonte_id: str, db_path=None):
    conn = get_conn(db_path)
    with conn:
        conn.execute(
            "UPDATE fontes SET ultima_coleta = ?, falhas_consecutivas = 0 WHERE id = ?",
            (datetime.utcnow().isoformat(), fonte_id),
        )
    conn.close()


def marcar_fonte_falha(fonte_id: str, db_path=None):
    conn = get_conn(db_path)
    with conn:
        conn.execute(
            "UPDATE fontes SET falhas_consecutivas = falhas_consecutivas + 1 WHERE id = ?",
            (fonte_id,),
        )
        row = conn.execute(
            "SELECT falhas_consecutivas FROM fontes WHERE id = ?", (fonte_id,)
        ).fetchone()
        if row and row["falhas_consecutivas"] >= 3:
            conn.execute("UPDATE fontes SET ativo = 0 WHERE id = ?", (fonte_id,))
            print(f"  [ALERTA] Fonte '{fonte_id}' desativada após 3 falhas consecutivas.")
    conn.close()
