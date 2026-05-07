# Plantão de Notícias — Resumo do Projeto

## O que é

Sistema automatizado de monitoramento de notícias políticas municipais do Estado do Rio de Janeiro, com foco em accountability, que gera briefings diários para produção de vídeos curtos (Reels / Shorts).

---

## Objetivo central

Cobrir escândalos e irregularidades políticas em municípios do RJ — especialmente Baixada Fluminense e capital — com conteúdo diário para redes sociais, partindo de fontes primárias e jornalísticas.

---

## Temas monitorados

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

Keywords e pesos são configuráveis em `data/temas.json` sem alterar código.

---

## Escopo inicial

- **Regiões:** Baixada Fluminense + Rio de Janeiro (capital)
- **Municípios da Baixada (13 core):** Nova Iguaçu, Duque de Caxias, São João de Meriti, Belford Roxo, Nilópolis, Mesquita, Queimados, Japeri, Magé, Guapimirim, Seropédica, Itaguaí, Paracambi
- **Formato de saída:** Vídeos curtos — Instagram Reels e YouTube Shorts

---

## Fluxo de trabalho

```
Coleta de fontes
      ↓
Classificação por município, tema e data
      ↓
Geração de relatório de pautas
      ↓
Revisão por IA (qualidade, risco jurídico)
      ↓
Aprovação humana (roteirista)
      ↓
Produção do vídeo
```

---

## Produto intermediário: o Relatório de Pautas

O pipeline não gera roteiros diretamente — gera um **briefing diário** com as pautas encontradas. O roteirista decide o que virar vídeo e como abordar.

Cada pauta no relatório contém:
- Município e data
- Tema categorizado
- Resumo do fato (2-3 linhas)
- Link da fonte principal + fontes secundárias
- Link para documento oficial (quando existir)
- Score de qualidade da fonte
- Indicador de risco jurídico

---

## Qualidade de fonte — como é medida

Não usamos Google Trends (sinal fraco para conteúdo local). Usamos:

| Critério | Peso |
|---|---|
| Existe documento oficial (TCE, MPE, DOERJ) | Alto |
| Quantos portais cobriram a mesma história | Médio |
| Credibilidade do portal de origem | Médio |
| Recência da publicação | Baixo |

---

## Fontes principais mapeadas

**Primárias (maior confiabilidade):**
- TCE-RJ — auditorias e fiscalizações por município
- MPE-RJ — ações penais e inquéritos
- DOERJ — contratos, licitações, dispensas de licitação
- Portais de transparência das prefeituras
- TRE-RJ — financiamento eleitoral, cassações

**Secundárias (portais jornalísticos):**
- G1 Rio, Extra, O Dia, Agência Brasil (EBC) — Tier A
- Metrópoles, R7, CNN Brasil, BandNews — Tier B (nacionais)
- Portais regionais da Baixada: Jornal Destaque, Folha da Baixada, Brava Baixada, ZM Notícias e outros
- Lista completa e atualizada em [FONTES.md](FONTES.md)

---

## Parâmetros de acionamento

```powershell
# Interface interativa (recomendado)
python cli.py

# Linha de comando direta
python pipeline.py --data 2026-05-07 --municipio belford-roxo --tema crime-organizado --top 10
```

| Parâmetro | Descrição |
|-----------|-----------|
| `--data` | Data inicial da coleta (`YYYY-MM-DD`) |
| `--data-fim` | Data final — gera relatório de período |
| `--municipio` | Filtrar por município (slug) |
| `--tema` | Filtrar por tema (slug) |
| `--top` | Número máximo de pautas (padrão: 10) |

---

## Riscos principais

| Risco | Severidade | Mitigação |
|---|---|---|
| Ação judicial por difamação | Alta | Rastrear fonte por claim, indicar risco no relatório |
| Volume excessivo para revisão humana | Alta | Priorização por score, top N pautas por dia |
| Sites municipais desatualizados | Média | Monitorar data da última atualização por fonte |
| Scraping quebrar com redesign de sites | Média | Priorizar fontes com RSS ou API |
| Cobertura zero em municípios pequenos | Baixa | Lógica de "sem pauta hoje" em vez de forçar conteúdo |
