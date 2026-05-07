import sys
sys.path.insert(0, ".")
from coletores import rss

fonte = {
    "id": "noticiasdebelfordroxo",
    "nome": "Noticias de Belford Roxo",
    "tier": "B",
    "tipo_acesso": "rss",
    "url_feed": "https://www.noticiasdebelfordroxo.com/feeds/posts/default",
    "municipios_cobertos": '["belford-roxo"]',
}

try:
    artigos = rss.coletar(fonte, paginas=1)
    print(f"OK: {len(artigos)} artigos")
    for a in artigos[:5]:
        print(f"  [{a['data_publicacao'][:10] if a['data_publicacao'] else 'sem-data'}] {a['titulo'][:70]}")
except Exception as e:
    print(f"ERRO: {e}")
