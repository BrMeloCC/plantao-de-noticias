import sys
sys.path.insert(0, ".")
from coletores import jornalatual

fonte = {"id": "jornalatual", "nome": "Jornal Atual", "tier": "B", "tipo_acesso": "web", "municipios_cobertos": ["itaguai", "seropedica"]}
artigos = jornalatual.coletar(fonte, paginas=1)
print(f"OK: {len(artigos)} artigos")
for a in artigos[:5]:
    print(f"  [{a['data_publicacao'][:10]}] {a['titulo'][:70]}")
    print(f"    {a['corpo_texto'][:80]}")
