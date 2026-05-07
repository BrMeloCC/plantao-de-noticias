# Plantão de Notícias — Contexto Completo

## Visão geral

O Plantão de Notícias é um sistema de jornalismo político automatizado voltado para municípios do Estado do Rio de Janeiro. O objetivo é monitorar continuamente fontes públicas e jornalísticas para identificar pautas relevantes sobre irregularidades, escândalos e má gestão municipal, transformando essas pautas em briefings estruturados que alimentam a produção de vídeos curtos para Instagram e YouTube.

O sistema não substitui o jornalista — ele elimina o trabalho manual de garimpagem de fontes e entrega uma fila de pautas qualificadas para que o roteirista decida o que produzir e como abordar cada história.

---

## Problema que resolve

Cobrir 92 municípios do RJ diariamente é humanamente impossível de forma manual. Fontes primárias de alto valor jornalístico — como auditorias do TCE-RJ, ações do MPE-RJ e contratos publicados no Diário Oficial — raramente são monitoradas por canais de redes sociais. Ao mesmo tempo, portais jornalísticos regionais da Baixada e do interior publicam histórias relevantes que não chegam à mídia estadual.

O sistema existe para cobrir esse gap com consistência e escala.

---

## Escopo do projeto

### Fase inicial
- **Regiões:** Baixada Fluminense + Município do Rio de Janeiro
- **Municípios da Baixada Fluminense (core):**
  - Nova Iguaçu, Duque de Caxias, São João de Meriti, Belford Roxo, Nilópolis, Mesquita, Queimados, Japeri, Paracambi, Seropédica, Itaguaí, Magé, Guapimirim

### Expansão futura
- Restante do Estado do Rio de Janeiro (92 municípios total)
- Parametrização por microrregião (Serrana, Lagos, Norte Fluminense, etc.)

---

## Temas monitorados

O sistema filtra conteúdo por relevância com base em categorias configuráveis em `data/temas.json`:

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

Keywords de cada tema são editáveis sem tocar no código Python.

---

## Arquitetura do pipeline

```
┌─────────────────────────────────────────────────────┐
│                    FONTES                           │
│  Primárias: TCE-RJ, MPE-RJ, DOERJ, Transparência  │
│  Secundárias: Portais jornalísticos regionais       │
└────────────────────────┬────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│                   COLETOR                           │
│  Parser por fonte (RSS, HTML, PDF, API)             │
│  Frequência: diária (padrão) ou sob demanda         │
│  Parâmetros: município, região, data, período       │
└────────────────────────┬────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│              PROCESSAMENTO                          │
│  Deduplicação semântica (mesma história, N fontes)  │
│  Classificação: município + tema + data             │
│  Score de qualidade da fonte                        │
│  Detecção de risco jurídico                         │
└────────────────────────┬────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│            BANCO DE PAUTAS                          │
│  Armazenamento estruturado por município/data/tema  │
│  Histórico para evitar reprocessamento              │
└────────────────────────┬────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│          GERAÇÃO DO RELATÓRIO                       │
│  Top N pautas do dia por relevância                 │
│  Formato estruturado para revisão humana            │
└────────────────────────┬────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│         REVISÃO IA → REVISÃO HUMANA                 │
│  IA: checagem de claims, qualidade, risco           │
│  Humano (roteirista): aprovação final               │
└────────────────────────┬────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────┐
│              PRODUÇÃO DO VÍDEO                      │
│  Roteiro para Reels / Shorts (vídeos curtos)        │
│  Perfis: Instagram + YouTube (já existentes)        │
└─────────────────────────────────────────────────────┘
```

---

## Formato do relatório de pautas

Cada entrada no relatório diário segue essa estrutura:

```
PAUTA #[ID] — [MUNICÍPIO] — [DATA]
═══════════════════════════════════════

Tema:         [categoria]
Qualidade:    [A / B / C] — [descrição do score]
Risco jurídico: [Baixo / Médio / Alto]

Resumo:
[2-3 linhas descrevendo o fato central]

Por que publicar:
[1 linha com o ângulo editorial]

Fonte principal:
[nome do veículo/órgão] — [link]

Fontes secundárias:
- [link 1]
- [link 2]

Documento oficial:
[link para TCE/MPE/DOERJ ou "não encontrado"]
```

---

## Sistema de qualidade de fontes

### Tiers de confiabilidade

| Tier | Critérios | Ação recomendada |
|---|---|---|
| **A** | Documento oficial (TCE, MPE, DOERJ) + cobertura jornalística | Publicar com confiança |
| **B** | Múltiplos portais cobriram + declaração oficial citada | Publicar com ressalva padrão |
| **C** | Portal único estabelecido, sem documento oficial | Publicar indicando fonte única |
| **D** | Portal não verificado ou redes sociais apenas | Não publicar / investigar antes |

### Por que não usar Google Trends

Google Trends mede interesse de busca em escala nacional/regional. Escândalos municipais na Baixada raramente aparecem no Trends, mesmo sendo de alto valor jornalístico para a audiência local. O indicador de qualidade mais confiável para conteúdo local é a **cobertura cruzada** — quantos portais independentes publicaram a mesma história.

---

## Fontes mapeadas

> **Fonte autoritativa:** [FONTES.md](FONTES.md) contém o inventário completo e atualizado de todas as fontes, com URLs verificadas, status de RSS, tiers de qualidade e gaps de cobertura por município. A seção abaixo é um resumo estrutural — consulte FONTES.md para detalhes operacionais.

### Fontes primárias (documentos oficiais)

| Fonte | Tipo de conteúdo | Acesso |
|---|---|---|
| TCE-RJ | Auditorias, obras paralisadas, contratos, licitações | API REST aberta (9 endpoints) |
| MPE-RJ | Ações penais, inquéritos, improbidade, milícias | Scraping — sem RSS |
| MPF/PR-RJ | Crimes federais, desvio de verbas federais | RSS — URL atual retorna 404, desativado |
| DOERJ | Contratos estaduais, licitações, dispensas | PDF diário + JusBrasil |
| TCM-RJ | Contratos da Prefeitura do Rio (capital) | Site público |
| TRE-RJ | Cassações, ações eleitorais, financiamento de campanha | Site público |
| Portais de transparência municipais | Gastos, empenhos, contratos por prefeitura | Varia — 11 municípios mapeados |

### Fontes secundárias (portais jornalísticos)

11 feeds RSS confirmados + 4 fontes via scraping — ver [FONTES.md](FONTES.md) para lista completa com URLs e tiers. Municípios com cobertura fraca (Magé, Mesquita, Nilópolis, Queimados) dependem principalmente do Brava Baixada.
- Preferência por portais com RSS

---

## Parâmetros de execução

O sistema aceita os seguintes parâmetros ao ser acionado:

```powershell
# Interface interativa (menus de seleção)
python cli.py

# Linha de comando
python pipeline.py [--data YYYY-MM-DD] [--data-fim YYYY-MM-DD]
                   [--municipio slug] [--tema slug]
                   [--top N] [--db caminho.db]
```

| Parâmetro | Descrição |
|-----------|-----------|
| `--data` | Data inicial da coleta (padrão: hoje) |
| `--data-fim` | Data final — gera relatório de período |
| `--municipio` | Filtrar por município (slug) |
| `--tema` | Filtrar por tema (slug) |
| `--top` | Número máximo de pautas (padrão: 10) |
| `--paginas` | Páginas por fonte (padrão: 1 — rápida; 10+ para backfill histórico) |
| `--incluir-outros` | Inclui pautas sem tema classificado no relatório (excluídas por padrão) |

Sem parâmetros, executa o modo padrão: todas as fontes ativas, data atual, top 10 pautas, sem "outros".

---

## Riscos e mitigações

### Risco jurídico
**Problema:** Os temas cobertos (milícia, compra de voto, improbidade) são os que mais geram ações de calúnia e difamação no Brasil. Políticos com ligação ao crime organizado no RJ têm histórico de uso judicial como instrumento de silenciamento.

**Mitigação:**
- Todo claim no relatório tem link para fonte rastreável
- Campo de risco jurídico no relatório alerta o roteirista
- Tier D de qualidade bloqueia publicação automática
- Roteirista (humano) tem aprovação final obrigatória

### Volume de revisão humana
**Problema:** Com cobertura diária de 13+ municípios, o volume pode superar a capacidade de revisão de uma pessoa.

**Mitigação:**
- Score de relevância prioriza automaticamente
- Relatório diário limitado ao top N configurável
- Pautas de menor score ficam em fila secundária para dias mais calmos

### Manutenção dos coletores
**Problema:** Sites mudam estrutura, removem RSS, alteram URLs. Cada mudança quebra um coletor.

**Mitigação:**
- Priorizar fontes com RSS ou API oficial
- Fontes primárias (TCE, DOERJ) têm estrutura mais estável
- Monitorar falhas de coleta com alertas

### Municípios sem cobertura
**Problema:** Municípios pequenos podem passar dias sem nenhuma publicação relevante.

**Mitigação:**
- Lógica explícita de "sem pauta hoje" para não forçar conteúdo vazio
- Relatório indica explicitamente quando não há pautas novas por município

---

## Decisões de produto tomadas

| Decisão | Escolha | Motivo |
|---|---|---|
| Formato de vídeo | Vídeos curtos (Reels / Shorts) | Perfis já existem; maior alcance orgânico |
| Produto do pipeline | Relatório de pautas (não roteiro direto) | Preserva julgamento editorial humano |
| Validação | IA + humano obrigatório | Uma fonte é aceitável, mas qualidade precisa ser informada |
| Qualidade de fonte | Score por tier, não Google Trends | Trends é irrelevante para conteúdo municipal local |
| Escopo inicial | Baixada + Rio | Maior densidade de cobertura e audiência |

---

## Estado atual

**Repositório:** https://github.com/BrMeloCC/plantao-de-noticias

O pipeline está funcional para coleta RSS e scraping de fontes primárias. O que está feito:

- Coleta RSS de 18 fontes configuradas
- Scrapers web para MPRJ, TCE-RJ e ALERJ (`coletores/mprj.py`, `tcerj.py`, `alerj.py`)
- Detecção de município em 4 camadas
- Classificação de tema por keywords expandidas em JSON (11 temas, cobertura ~72% → ~30% em "outros")
- Score com tier, cobertura cruzada, recência, boost de município e peso de tema
- Deduplicação semântica por Jaccard de bigramas (janela de 48h)
- Geração de relatório Markdown com filtros por data (`data_fato`), município, tema e profundidade
- "Outros / Geral" excluído do relatório por padrão; ativável via `--incluir-outros`
- Interface interativa (`cli.py`) e atalhos PowerShell (`run.ps1`)

## Próximos passos

**Coletores pendentes:**
- Portais regionais via scraping: Notícias da Baixada, Jornal Baixada em Foco, Jornal Atual
- API TCE-RJ (endpoints REST): obras paralisadas, contratos, licitações por município

**Qualidade das pautas:**
- Busca automática de documento oficial → preenchimento de `documento_oficial_url`
- Melhorar resumo da pauta: hoje usa os primeiros 280 chars do corpo; ideal seria extração do parágrafo-lide

**Revisão e automação:**
- Revisão por IA (checagem de claims, sugestão de ângulo editorial) antes da revisão humana
- Automação via cron / GitHub Actions para coleta diária sem intervenção manual

**Cobertura geográfica:**
- Expandir municípios além da Baixada + Rio (demais 78 municípios do estado)
