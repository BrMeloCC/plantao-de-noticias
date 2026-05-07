# Plantão de Notícias — Schema de Dados

> Versão: 1.0 — 2026-05-06
> Este documento define os modelos de dados do pipeline, o algoritmo de score e a estratégia de detecção de município.
> É a referência técnica que precede a implementação dos coletores.

---

## Visão geral dos modelos

```
Fonte ──────────────────────────────────────────────────┐
  (configuração de cada origem)                         │
                                                        │
Artigo ─────── pertence a ──────────────────────────► Fonte
  (item bruto coletado de uma fonte)                    │
       │                                                │
       └──── agrupado em ──────────────────────────► Pauta
                                                        │
Pauta ──── passará por ──► Revisão IA ──► Revisão Humana
  (briefing editorial pronto para o roteirista)
```

---

## Modelo: Fonte

Configuração estática de cada origem monitorada. Não muda a cada coleta.

| Campo | Tipo | Descrição |
|---|---|---|
| `id` | string (slug) | Identificador único. Ex: `"brava-baixada"`, `"tce-rj-api"` |
| `nome` | string | Nome legível. Ex: `"Brava Baixada"` |
| `url_base` | string | URL principal do portal/órgão |
| `tipo_acesso` | enum | `rss` · `api_rest` · `scraping` · `pdf` |
| `url_feed` | string \| null | URL do RSS ou endpoint base da API |
| `tier` | enum | `A` · `B` · `C` · `D` (ver tabela de tiers em FONTES.md) |
| `municipios_cobertos` | string[] | Lista de slugs de município. Ex: `["duque-de-caxias"]`. `["*"]` = todos |
| `ativo` | bool | Se falso, o coletor pula esta fonte |
| `ultima_coleta` | datetime \| null | Timestamp da última execução bem-sucedida |
| `falhas_consecutivas` | int | Contador de falhas — se ≥ 3, desativar e alertar |

**Exemplo:**
```json
{
  "id": "noticiasdesaojoaodemeriti",
  "nome": "Notícias de São João de Meriti",
  "url_base": "https://www.noticiasdesaojoaodemeriti.com",
  "tipo_acesso": "rss",
  "url_feed": "https://www.noticiasdesaojoaodemeriti.com/feeds/posts/default",
  "tier": "B",
  "municipios_cobertos": ["sao-joao-de-meriti"],
  "ativo": true,
  "ultima_coleta": null,
  "falhas_consecutivas": 0
}
```

---

## Modelo: Artigo

Item bruto coletado de uma fonte. Representa uma publicação individual — post, nota, ato oficial.

| Campo | Tipo | Descrição |
|---|---|---|
| `id` | string | SHA-256 da URL (evita duplicatas por URL) |
| `url` | string | URL canônica do artigo (unique) |
| `titulo` | string | Título extraído |
| `corpo_texto` | string | Texto limpo, sem HTML |
| `html_raw` | string \| null | HTML original (para re-parsing se necessário) |
| `data_publicacao` | datetime | Data/hora de publicação original |
| `data_coleta` | datetime | Timestamp de quando o coletor encontrou o item |
| `fonte_id` | string | FK → Fonte.id |
| `municipios_detectados` | string[] | Slugs dos municípios detectados no conteúdo |
| `confianca_municipio` | float[] | Score 0–1 por município detectado (mesma ordem) |
| `status` | enum | `novo` · `em_processamento` · `processado` · `duplicata` · `ignorado` |
| `duplicata_de` | string \| null | FK → Artigo.id (se `status = duplicata`) |

**Observação sobre `id`:**
Usar SHA-256 da URL normalizada (lowercase, sem parâmetros de tracking `utm_*`) permite detectar duplicatas de URL sem consultar o banco — basta calcular o hash antes de inserir.

---

## Modelo: Pauta

Produto processado do pipeline. É o que o roteirista verá no relatório diário.

### Campos editoriais

| Campo | Tipo | Descrição |
|---|---|---|
| `id` | UUID | Identificador único gerado no processamento |
| `titulo_pauta` | string | Título editorial (pode diferir do artigo de origem) |
| `municipio` | string | Slug do município principal. Ex: `"belford-roxo"` |
| `tema` | enum | Ver lista abaixo |
| `resumo` | string | 2–3 linhas descrevendo o fato central |
| `por_que_publicar` | string | 1 linha com o ângulo editorial |
| `data_fato` | date | Data do fato noticiado (não da coleta) |

**Temas disponíveis (`tema`):**
```
crime-organizado
compra-de-voto
improbidade-administrativa
licitacao-suspeita
obras-inacabadas
gasto-irregular
saude-publica
educacao
seguranca-publica
eleicoes
greve
```
Keywords e pesos de cada tema são configuráveis em `data/temas.json`.

### Campos de fonte e rastreabilidade

| Campo | Tipo | Descrição |
|---|---|---|
| `artigo_principal_id` | string | FK → Artigo.id (fonte de maior tier) |
| `artigos_secundarios_ids` | string[] | FK[] → Artigo.id (fontes adicionais) |
| `documento_oficial_url` | string \| null | Link direto para TCE/MPE/DOERJ. `null` se não encontrado |
| `documento_oficial_tipo` | string \| null | Ex: `"TCE-RJ"`, `"MPRJ"`, `"DOERJ"` |

### Campos de qualidade e risco

| Campo | Tipo | Descrição |
|---|---|---|
| `tier` | enum | `A` · `B` · `C` · `D` — tier da fonte principal |
| `score` | float | Score calculado — ver algoritmo abaixo |
| `score_breakdown` | object | Detalhamento do cálculo (para auditoria) |
| `cobertura_cruzada` | int | Quantas fontes independentes cobriram a mesma história |
| `risco_juridico` | enum | `baixo` · `medio` · `alto` — ver critérios abaixo |

### Campos de fluxo de revisão

| Campo | Tipo | Descrição |
|---|---|---|
| `status` | enum | Ver estados abaixo |
| `data_geracao` | datetime | Quando a pauta foi gerada |
| `revisao_ia_notas` | string \| null | Notas da revisão automatizada |
| `revisao_ia_em` | datetime \| null | Timestamp da revisão IA |
| `revisao_humana_notas` | string \| null | Notas do roteirista |
| `revisao_humana_em` | datetime \| null | Timestamp da aprovação/rejeição humana |
| `revisado_por` | string \| null | Identificador do roteirista |

**Estados de `status`:**
```
pendente_ia        → gerada, aguardando revisão automatizada
pendente_humano    → passou pela IA, aguardando roteirista
aprovado           → roteirista aprovou — pronto para produção
rejeitado          → descartado (IA ou humano)
irrelevante        → filtrada automaticamente por conteúdo fora do escopo (ver data/exclusoes.json)
publicado          → vídeo produzido e postado
```

Pautas `irrelevante` permanecem no banco para auditoria mas nunca aparecem nos relatórios.

**Critérios de `risco_juridico`:**

| Risco | Quando aplicar |
|---|---|
| `alto` | Alegação de crime (milícia, desvio) sem documento oficial · Pessoa física acusada sem processo aberto · Tema: crime organizado |
| `medio` | Acusação com documento oficial mas sem condenação · Denúncia de portal único (Tier C) sobre improbidade |
| `baixo` | Fato documentado em acórdão/sentença já publicados · Dado quantitativo de portal de transparência sem atribuição de culpa |

---

## Algoritmo de Score

O score determina a ordem das pautas no relatório diário.

### Fórmula

```
score = (tier_base + cobertura_bonus + documento_bonus + municipio_boost) × fator_recencia × peso_tema
```

### Componentes

**`tier_base`** — peso da fonte principal:
```
A → 10
B →  7
C →  4
D →  0
```

**`cobertura_bonus`** — fontes independentes adicionais (máx. +6):
```
+0  → apenas 1 fonte
+2  → 2 fontes
+4  → 3 fontes
+6  → 4+ fontes
```

**`documento_bonus`** — existência de documento oficial vinculado:
```
+5  → documento oficial confirmado (TCE, MPE, DOERJ, TRE)
+0  → sem documento
```

**`municipio_boost`** — prioridade editorial por município:
```
+2  → Nova Iguaçu, Duque de Caxias, Belford Roxo
+1  → São João de Meriti, Nilópolis, Rio de Janeiro
+0  → demais municípios
```

**`fator_recencia`** — decaimento por idade do fato:
```
hoje        → 1,00
ontem       → 0,85
2 dias      → 0,70
3–5 dias    → 0,55
6–14 dias   → 0,40
15+ dias    → 0,25
```

**`peso_tema`** — multiplicador por relevância editorial do tema (configurável em `temas.json`):
```
crime-organizado     → 1,2
licitacao-suspeita   → 1,1
compra-de-voto       → 1,1
demais               → 1,0
seguranca-publica    → 0,9
eleicoes             → 0,9
greve                → 0,9
```

### Exemplos de score

| Cenário | Cálculo | Score |
|---|---|---|
| TCE-RJ (Tier A) + 3 portais + hoje + crime-organizado em Duque de Caxias | (10 + 4 + 5 + 2) × 1,0 × 1,2 | **25,2** |
| Portal B + doc MPE + 1 fonte + hoje + improbidade | (7 + 0 + 5 + 0) × 1,0 × 1,0 | **12,0** |
| Portal B, sem documento, 2 fontes, ontem | (7 + 2 + 0 + 0) × 0,85 × 1,0 | **7,65** |
| Portal C, sem documento, 1 fonte, 3 dias | (4 + 0 + 0 + 0) × 0,55 × 1,0 | **2,20** |

### Bloqueio por risco jurídico

Pautas com `risco_juridico = alto` e `tier = D` são automaticamente marcadas como `rejeitado`.

---

## Detecção de Município

O coletor precisa identificar automaticamente qual município uma notícia cobre. A detecção é feita em camadas, da mais confiável à menos.

### Camada 1 — Fonte exclusiva de município (confiança: 0,20–1,0)

Se `Fonte.municipios_cobertos` contém exatamente um município e não `["*"]`, a fonte indica o município mas o conteúdo é validado:

| Condição | Confiança |
|---|---|
| Artigo menciona explicitamente a cidade (`termos_exatos` ou `termos_contextuais`) | 1,0 |
| Artigo contém keyword política local (prefeito, obra, desvio…) sem citar a cidade | 0,80 |
| Nenhuma das condições acima (ex.: notícia nacional/internacional repostada) | 0,20 → ignorado |

Isso impede que fontes municipais que repostem notícias nacionais (ex.: Trump, Epstein) sejam atribuídas incorretamente ao município da fonte.

Exemplos: Duquecaxiense TV, Notícias de São João de Meriti, ZM Notícias (Nova Iguaçu).

### Camada 2 — Slug do município na URL do artigo (confiança: 0,95)

Verificar se a URL contém o nome/slug do município:
```
bravabaixada.com.br/municipios/mage/         → magé
bravabaixada.com.br/municipios/nilópolis/    → nilópolis
```

### Camada 3 — Nome do município no título (confiança: 0,85)

Buscar variações do nome no título (case-insensitive, acentuação normalizada):
```
"Nova Iguaçu", "nova iguacu", "NI" (contexto + keyword) → nova-iguacu
"Duque de Caxias", "Caxias" (com keyword política/prefeitura) → duque-de-caxias
```

### Camada 4 — Nome do município no corpo + keyword de contexto (confiança: 0,65)

Nome do município no corpo do texto **e** pelo menos uma keyword de contexto político:
```
keywords: prefeito, prefeitura, câmara, vereador, secretaria, licitação, contrato, TCE, MPE, obra, servidor
```

Se o nome aparecer sem keyword de contexto, não atribuir (risco de falso positivo).

### Camada 5 — Bairros e logradouros conhecidos (confiança: 0,60)

Lista curada de bairros exclusivos de cada município. Exemplos:
```
"Capivari" → magé
"Engenho da Rainha" → rio-de-janeiro (Zona Norte)
"Chatuba" → mesquita ou nova-iguacu → resolver por contexto
```

Esta lista será mantida em `data/bairros.json` e cresce incrementalmente.

### Empate e múltiplos municípios

- Se a detecção identificar **1 município com confiança ≥ 0,65**: atribuir como município principal.
- Se identificar **2+ municípios** (notícia regional): criar uma pauta por município OU marcar como `regiao = baixada` sem município específico. Decisão configurável por parâmetro.
- Se confiança < 0,50 em todos: marcar `municipio = "indeterminado"` e não incluir no relatório diário (fila separada para revisão manual).

### Slugs canônicos dos municípios

```json
{
  "nova-iguacu":        "Nova Iguaçu",
  "duque-de-caxias":   "Duque de Caxias",
  "sao-joao-de-meriti": "São João de Meriti",
  "belford-roxo":       "Belford Roxo",
  "nilopolis":          "Nilópolis",
  "mesquita":           "Mesquita",
  "queimados":          "Queimados",
  "japeri":             "Japeri",
  "mage":               "Magé",
  "guapimirim":         "Guapimirim",
  "seropedica":         "Seropédica",
  "itaguai":            "Itaguaí",
  "paracambi":          "Paracambi",
  "rio-de-janeiro":     "Rio de Janeiro",
  "estado-rio":         "Estado do Rio"
}
```

`estado-rio` captura notícias do governo estadual (ALERJ, governador, secretarias de estado). No relatório diário, aparece em seção separada ("Estado do Rio — Destaques") após as pautas municipais.

---

## Deduplicação

Duas camadas de deduplicação:

### Camada 1 — Hash de URL (exata)

Ao coletar, calcular `SHA-256(url_normalizada)`. Se já existe no banco → `status = duplicata`. Custo zero.

**Normalização de URL:**
1. Lowercase
2. Remover parâmetros UTM (`utm_source`, `utm_medium`, etc.)
3. Remover `#fragment`
4. Remover trailing slash

### Camada 2 — Similaridade semântica (mesma história, fontes diferentes)

Comparar títulos de artigos coletados no mesmo dia para o mesmo município usando similaridade de strings (Jaccard ou TF-IDF simples). Se similaridade ≥ 0,75 e mesmo município: agrupar como cobertura cruzada da mesma pauta, não criar pauta duplicada.

Esta camada aumenta o `cobertura_cruzada` da pauta em vez de criar duas pautas separadas.

**Implementação mínima viável:** Jaccard de bigramas nos títulos — eficiente, sem dependência de modelo de linguagem.

---

## Estrutura de arquivos

```
plantao_de_noticias/
├── cli.py                       # Interface interativa (TUI)
├── pipeline.py                  # Orquestrador principal
├── db.py                        # Acesso ao SQLite
├── requirements.txt
├── run.ps1
├── data/
│   ├── fontes.json              # instâncias do modelo Fonte (~31 fontes ativas)
│   ├── municipios.json          # slugs, nomes, boost e termos por município (inclui prefeitos)
│   ├── temas.json               # temas, keywords e peso (editável)
│   └── exclusoes.json           # grupos de palavras-chave para filtro editorial
├── db/
│   └── plantao.db               # SQLite
├── coletores/
│   ├── rss.py                   # coletor genérico de RSS
│   ├── mprj.py                  # scraper MPRJ
│   ├── tcerj.py                 # scraper TCE-RJ
│   ├── alerj.py                 # scraper ALERJ
│   └── jornalatual.py           # scraper Jornal Atual
├── processamento/
│   ├── detector_municipio.py    # detecção de município em 4 camadas
│   ├── scorer.py                # score, tema, risco jurídico
│   ├── filtro_exclusao.py       # filtro editorial por keywords (exclusoes.json)
│   └── extrator_doc.py          # busca URL de documento oficial
├── relatorio/
│   └── gerador.py               # monta o relatório Markdown (seção municipal + Estado do Rio)
├── relatorios/                  # saída gerada
└── docs/                        # documentação interna
```

---

## O que ainda não foi implementado

- Coletores scraping: Notícias da Baixada, Jornal Baixada em Foco (MPRJ, TCE-RJ, ALERJ, Jornal Atual já implementados)
- Coletor da API TCE-RJ
- Revisão por IA antes da revisão humana
- Automação via cron / GitHub Actions para coleta diária
