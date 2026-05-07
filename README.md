# Plantão de Notícias

Monitor automatizado de pautas jornalísticas para municípios do Rio de Janeiro.
Coleta feeds RSS, detecta município, classifica tema e gera relatório diário em Markdown.

---

## Instalação

```powershell
pip install -r requirements.txt
```

---

## Uso rápido

```powershell
# Coleta e relatório de hoje
python pipeline.py

# Atalhos prontos (recomendado)
.\run.ps1 hoje
.\run.ps1 ontem
.\run.ps1 semana
```

---

## Interface interativa

```powershell
python cli.py
```

Abre menus de seleção para período, município, tema e número de pautas. Recomendado para uso cotidiano.

---

## Parâmetros completos

| Parâmetro | Padrão | Descrição |
|-----------|--------|-----------|
| `--data` | hoje | Data da coleta (`YYYY-MM-DD`) |
| `--data-fim` | igual a `--data` | Data final do relatório — gera range |
| `--municipio` | todos | Filtrar por município (slug) |
| `--tema` | todos | Filtrar por tema (slug) |
| `--top` | 10 | Número máximo de pautas no relatório |
| `--db` | `db/plantao.db` | Caminho alternativo para o banco SQLite |

---

## Exemplos

```powershell
# Dia específico
python pipeline.py --data 2026-05-06

# Relatório da semana (coleta hoje, relatório dos últimos 7 dias)
python pipeline.py --data-fim 2026-05-06 --data 2026-04-30

# Só um município, top 5
python pipeline.py --municipio belford-roxo --top 5

# Município + período
python pipeline.py --data 2026-05-01 --data-fim 2026-05-06 --municipio nova-iguacu

# Filtro por tema
python pipeline.py --tema crime-organizado

# Município + tema
python pipeline.py --municipio rio-de-janeiro --tema improbidade-administrativa

# Banco separado para teste (não afeta o banco principal)
python pipeline.py --db testes/teste.db
```

---

## Slugs de municípios

```
nova-iguacu        duque-de-caxias     sao-joao-de-meriti
belford-roxo       nilopolis           mesquita
queimados          japeri              mage
guapimirim         seropedica          itaguai
paracambi          rio-de-janeiro
```

---

## Temas detectados

| Slug | Nome | Peso |
|------|------|------|
| `crime-organizado` | Crime Organizado / Milícia | 1.2 |
| `licitacao-suspeita` | Licitação Suspeita | 1.1 |
| `compra-de-voto` | Compra de Voto | 1.1 |
| `improbidade-administrativa` | Improbidade Administrativa | 1.0 |
| `obras-inacabadas` | Obras Inacabadas / Superfaturadas | 1.0 |
| `gasto-irregular` | Gasto Irregular com Dinheiro Público | 1.0 |
| `saude-publica` | Saúde Pública | 1.0 |
| `educacao` | Educação | 1.0 |
| `seguranca-publica` | Segurança Pública | 0.9 |
| `eleicoes` | Eleições / Política Eleitoral | 0.9 |
| `greve` | Greve / Paralisação de Serviços Públicos | 0.9 |

---

## Score

```
score = (tier_base + cobertura_bonus + doc_bonus + municipio_boost) × recência × peso_tema
```

| Componente | Valor |
|-----------|-------|
| Tier A | 10 · Tier B: 7 · Tier C: 4 · Tier D: 0 |
| Cobertura cruzada | +2 por fonte extra (máx +6) |
| Documento oficial | +5 |
| Boost município | Nova Iguaçu / Duque de Caxias / Belford Roxo: +2 · SJM / Nilópolis / Rio: +1 |
| Recência | Hoje: ×1.0 · Ontem: ×0.85 · 2d: ×0.70 · 3–5d: ×0.55 · 6–14d: ×0.40 · 15+d: ×0.25 |

---

## Estrutura do projeto

```
plantao_de_noticias/
├── cli.py                       # Interface interativa (TUI com menus)
├── pipeline.py                  # Orquestrador principal
├── db.py                        # Acesso ao SQLite
├── requirements.txt
├── run.ps1                      # Atalhos de linha de comando
│
├── data/
│   ├── fontes.json              # Fontes RSS configuradas
│   ├── municipios.json          # Municípios + termos de detecção + boost
│   └── temas.json               # Temas + keywords + peso (editável sem tocar no código)
│
├── coletores/
│   └── rss.py                   # Coleta e parse de feeds RSS
│
├── processamento/
│   ├── detector_municipio.py    # Detecção de município por camadas
│   └── scorer.py                # Score, tema, risco jurídico
│
├── relatorio/
│   └── gerador.py               # Geração do relatório em Markdown
│
├── relatorios/                  # Relatórios gerados (YYYY-MM-DD[_filtros].md)
├── db/
│   └── plantao.db               # Banco SQLite
└── docs/                        # Documentação interna
    ├── CONTEXTO.md
    ├── FONTES.md
    ├── RESUMO.md
    └── SCHEMA.md
```

---

## Configuração das fontes

Edite `data/fontes.json` para adicionar ou desativar fontes:

```json
{
  "id": "minha-fonte",
  "nome": "Minha Fonte",
  "tier": "B",
  "tipo_acesso": "rss",
  "url_feed": "https://exemplo.com/feed",
  "municipios_cobertos": ["nova-iguacu"],
  "ativo": true
}
```

`municipios_cobertos`: use `["*"]` para fontes regionais ou o slug específico para fontes exclusivas de um município.

---

## Adicionando keywords a um tema

Edite `data/temas.json` diretamente — sem precisar tocar no código:

```json
"gasto-irregular": {
  "nome": "Gasto Irregular com Dinheiro Público",
  "keywords": ["show milionário", "cachê suspeito", "..."],
  "peso": 1.0
}
```
