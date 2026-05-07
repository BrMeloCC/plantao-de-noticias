# Plantão de Notícias — Mapeamento de Fontes

> Mapeado em: 2026-05-07
> Escopo: Baixada Fluminense + Rio de Janeiro (capital)
> Status: Verificado via acesso direto aos sites

---

## FONTES PRIMÁRIAS — Tier A

São documentos e dados oficiais. Têm maior peso no score de qualidade da pauta. Nenhum jornalista intermediou a informação — o fato está no documento original.

---

### 1. TCE-RJ — Tribunal de Contas do Estado

| Campo | Valor |
|---|---|
| Portal | https://www.tcerj.tc.br |
| API de Dados Abertos | https://dados.tcerj.tc.br/api |
| Cobertura | 91 municípios do RJ (exceto capital — coberta pelo TCM-RJ) |
| Acesso | API REST aberta, sem autenticação |
| RSS | Não — API REST |

**Endpoints disponíveis na API:**

| Endpoint | Relevância para o projeto |
|---|---|
| `Obras Paralisadas` | **ALTA** — obras inacabadas com pagamento realizado |
| `Contratos` | **ALTA** — contratos suspeitos, valores, partes |
| `Licitações` | **ALTA** — dispensas, irregularidades em processos |
| `Compras Diretas Geral` | **ALTA** — dispensas de licitação sem justificativa |
| `Gastos com Pessoal` | Média — cargos comissionados excessivos |
| `Prestação de Contas` | Média — balanço financeiro municipal |
| `Concessões Públicas` | Média — PPPs suspeitas |
| `Compras Diretas Covid` | Baixa — período específico |
| `Situação Funcional` | Baixa |

**Nota técnica:** Documentação completa em `/api/v1/docs`. Dados provêm de SIGFIS e e-TCERJ. Parâmetros de filtro por município a confirmar na documentação completa.

---

### 2. TCM-RJ — Tribunal de Contas do Município do Rio

| Campo | Valor |
|---|---|
| Portal | https://www.tcmrio.tc.br |
| Cobertura | Apenas município do Rio de Janeiro |
| Acesso | Site público |
| RSS | A verificar |

**Nota:** Fiscaliza especificamente o município do Rio. Para contratos da Prefeitura do Rio, esta é a instância correta, não o TCE-RJ.

---

### 3. MPRJ — Ministério Público do Estado do RJ

| Campo | Valor |
|---|---|
| Portal | https://www.mprj.mp.br |
| Notícias | https://www.mprj.mp.br/home/-/detalhe-noticia/todas |
| Cobertura | Estado inteiro — ações penais, improbidade, milícias |
| RSS | Não confirmado (não encontrado) |
| Acesso | Scraping da seção de notícias |

**Nota:** Principal fonte para ações contra políticos, inquéritos sobre milícias e improbidade administrativa. Sem RSS — necessita scraping ou monitoramento manual periódico.

---

### 4. MPF/PR-RJ — Procuradoria da República no RJ (Federal)

| Campo | Valor |
|---|---|
| Portal | https://www.mpf.mp.br/rj |
| RSS | https://www.mpf.mp.br/rj/sala-de-imprensa/noticias-rj/RSS |
| Cobertura | Crimes federais, corrupção em contratos federais |
| Status | **DESATIVADO — URL retorna 404** |

**Nota:** URL do RSS está quebrada. Fonte desativada no `fontes.json` até que o novo endpoint seja encontrado no site do MPF.

---

### 5. DOERJ — Diário Oficial do Estado do RJ

| Campo | Valor |
|---|---|
| Portal IOERJ | https://portal.ioerj.com.br |
| Busca no Jusbrasil | https://www.jusbrasil.com.br/diarios/DOERJ/ |
| Cobertura | Contratos estaduais, atos que envolvem municípios |
| Formato | PDF diário + busca textual |
| RSS | Não confirmado |
| Acesso via JusBrasil | Disponível com busca por termos |

---

### 6. Diário Oficial do Município do Rio de Janeiro

| Campo | Valor |
|---|---|
| Portal | https://doweb.rio.rj.gov.br |
| Cobertura | Contratos, licitações e atos da Prefeitura do Rio |
| Formato | PDF + busca |
| RSS | A verificar |

---

### 7. TRE-RJ — Tribunal Regional Eleitoral

| Campo | Valor |
|---|---|
| Portal | https://www.tre-rj.jus.br |
| Notícias | https://www.tre-rj.jus.br/comunicacao |
| Cobertura | Cassações, ações eleitorais, financiamento de campanha |
| RSS | Não confirmado (erro de conexão na verificação) |

**Nota:** Fundamental para pautas eleitorais — cassações de prefeitos e vereadores, condenações por compra de voto.

---

## PORTAIS DE TRANSPARÊNCIA MUNICIPAL

Cada prefeitura mantém portal próprio. Qualidade e atualização variam muito.

### Baixada Fluminense — Core (13 municípios)

| Município | Portal de Transparência | Status |
|---|---|---|
| **Nova Iguaçu** | https://www.novaiguacu.rj.gov.br (seção transparência) | Parcial |
| **Duque de Caxias** | https://transparencia.duquedecaxias.rj.gov.br | Ativo — licitações 2025/2026 |
| **São João de Meriti** | https://transparencia.meriti.rj.gov.br | Ativo |
| **Belford Roxo** | https://transparencia.prefeituradebelfordroxo.rj.gov.br | Ativo |
| **Nilópolis** | https://nilopolis.rj.gov.br/diario-oficial-extra-online | Diário Oficial online |
| **Mesquita** | https://transparencia.mesquita.rj.gov.br | Ativo |
| **Queimados** | https://transparencia.queimados.rj.gov.br | Ativo |
| **Japeri** | https://pmjaperi.geosiap.net.br/portal-transparencia | Ativo |
| **Paracambi** | https://paracambi.rj.gov.br/transparencia | Ativo |
| **Seropédica** | https://transparencia.seropedica.rj.gov.br | A confirmar |
| **Itaguaí** | https://transparencia.itaguai.rj.gov.br | A confirmar |
| **Magé** | https://transparencia.mage.rj.gov.br | Ativo |
| **Guapimirim** | https://guapimirim.rj.gov.br/transparencia | Ativo |

### Baixada Fluminense — Municípios limítrofes (frequentemente incluídos)

| Município | Portal de Transparência | Obs |
|---|---|---|
| **Cachoeiras de Macacu** | https://www.cachoeirasdemacacu.rj.leg.br (Câmara) | Prefeitura — a mapear |
| **Itaboraí** | A mapear | — |
| **Tanguá** | A mapear | — |

### Capital

| Município | Portal de Transparência | Status |
|---|---|---|
| **Rio de Janeiro** | https://prefeitura.rio | Ativo — portal completo |

**Câmaras Municipais — Transparência do Legislativo:**

| Câmara | Portal |
|---|---|
| Duque de Caxias | https://transparencia.cmdc.rj.gov.br |
| São João de Meriti | https://transparencia.saojoaodemeriti.rj.leg.br |
| Belford Roxo | https://transparencia.cmbr.rj.gov.br |
| Japeri | https://pmjaperi.geosiap.net.br/portal-transparencia/licitacoes/contratos |
| Mesquita | https://mesquita.rj.leg.br/portal-transparencia |
| Magé | https://cmmage-rj.portaltp.com.br |
| Rio de Janeiro | https://www.camara.rio |

---

## PRIORIDADE POR POPULAÇÃO — Baixada + Capital

Fonte: IBGE Censo 2022. Determina quantas fontes cada município precisa e peso no relatório diário.

| # | Município | Pop. (2022) | Fontes RSS | Fontes scraping | Gap |
|---|---|---|---|---|---|
| 1 | **Rio de Janeiro** | ~6,7M | 1 | 1 | Zona Norte/Oeste fraca |
| 2 | **Duque de Caxias** | 808.152 | 4 | 1 | Bem coberto |
| 3 | **Nova Iguaçu** | 785.882 | 4 | 1 | Bem coberto |
| 4 | **Belford Roxo** | ~480.000 | 2 | 2 | Aceitável |
| 5 | **São João de Meriti** | 440.962 | 3 | 1 | Aceitável |
| 6 | **Magé** | 228.127 | 3 | 0 | Aceitável (Câmara + Portal + Brava) |
| 7 | **Mesquita** | 167.128 | 2 | 1 | Aceitável |
| 8 | **Nilópolis** | ~155.000 | 1 | 1 | ⚠ Fraco — buscar portal independente |
| 9 | **Itaguaí** | ~120.000 | 2 | 1 | Aceitável |
| 10 | **Japeri** | 96.289 | 2 | 0 | Aceitável |
| 11 | **Seropédica** | 80.596 | 2 | 1 | Aceitável |
| 12 | **Guapimirim** | ~55.000 | 3 | 0 | Aceitável |
| 13 | **Queimados** | ~145.000 | 3 | 0 | Aceitável |
| 14 | **Paracambi** | 41.375 | 1 | 0 | Aceitável (prefeitura) |

---

## FONTES SECUNDÁRIAS — Portais Jornalísticos

### COM RSS CONFIRMADO

---

#### Jornal Destaque Baixada
| Campo | Valor |
|---|---|
| URL | https://www.jornaldestaquebaixada.com |
| RSS | **https://www.jornaldestaquebaixada.com/feeds/posts/default** |
| Municípios cobertos | Toda a Baixada Fluminense + capital |
| Atividade | Alta — 10 a 15 posts/dia |
| Antiguidade | +10 anos |
| Foco editorial | Política municipal, segurança, obras |
| Tier | **B** |
| Filtro por município | Sim — ex: `/search/label/São+João+de+Meriti` |

---

#### Folha da Baixada
| Campo | Valor |
|---|---|
| URL | https://folhadabaixada.com.br |
| RSS | **https://folhadabaixada.com.br/feed/** |
| Municípios cobertos | Duque de Caxias, Nova Iguaçu, outros |
| Atividade | Alta — múltiplos posts/dia |
| Foco editorial | Política municipal, governo estadual |
| Tier | **B** |

---

#### ZM Notícias
| Campo | Valor |
|---|---|
| URL | https://www.zmnoticias.com.br |
| RSS | **https://www.zmnoticias.com.br/feed/** |
| Municípios cobertos | Nova Iguaçu (principal) + Baixada |
| Atividade | Alta — múltiplos posts/dia |
| Foco editorial | Governo municipal, obras, segurança pública |
| Tier | **B** |

---

#### Duquecaxiense TV
| Campo | Valor |
|---|---|
| URL | https://duquecaxiensetv.com |
| RSS | **https://duquecaxiensetv.com/feed/** |
| Municípios cobertos | Duque de Caxias (exclusivo) |
| Atividade | Alta — múltiplos posts/dia |
| Foco editorial | Segurança, política municipal, eventos |
| Tier | **B** |
| Destaque | Único portal RSS exclusivo de Duque de Caxias |

---

#### Notícias de Duque de Caxias
| Campo | Valor |
|---|---|
| URL | https://www.noticiasdeduquedecaxias.com |
| RSS | **https://www.noticiasdeduquedecaxias.com/feeds/posts/default** |
| Municípios cobertos | Duque de Caxias (exclusivo) |
| Atividade | Ativa — múltiplos posts/dia |
| Foco editorial | Política, Câmara Municipal, crime, administração |
| Tier | **B** |

---

#### Notícias de São João de Meriti
| Campo | Valor |
|---|---|
| URL | https://www.noticiasdesaojoaodemeriti.com |
| RSS | **https://www.noticiasdesaojoaodemeriti.com/feeds/posts/default** |
| Municípios cobertos | São João de Meriti (exclusivo) |
| Atividade | Muito alta — 4.185 posts no arquivo |
| Foco editorial | Segurança, política, saúde, cultura, educação |
| Tier | **B** |
| Destaque | Maior arquivo de conteúdo exclusivo de SJM identificado |

---

#### Belford Roxo 24h
| Campo | Valor |
|---|---|
| URL | https://belfordroxo24h.com |
| RSS | **https://belfordroxo24h.com/feed/** |
| Municípios cobertos | Belford Roxo (principal) + nacional |
| Atividade | Alta — atualização contínua |
| Foco editorial | Política, segurança, economia — ~40-50% conteúdo local |
| Tier | **B** |
| Destaque | Cobriu bloqueio de R$ 428M em bens de Waguinho diretamente |

---

#### Nova Iguaçu 24h
| Campo | Valor |
|---|---|
| URL | https://novaiguacu24h.com.br |
| RSS | **https://novaiguacu24h.com.br/feed/** |
| Municípios cobertos | Nova Iguaçu (exclusivo) |
| Atividade | Moderada — publica resumos diários |
| Foco editorial | Resumos de notícias locais — FGTS, Câmara, Prefeitura |
| Tier | **C** |
| Observação | Último item em março 2026 — verificar se ainda ativo |

---

#### Tempo Real RJ
| Campo | Valor |
|---|---|
| URL | https://temporealrj.com |
| RSS | **https://temporealrj.com/feed/** |
| Municípios cobertos | Rio de Janeiro capital (principal) + estado |
| Atividade | Alta — atualização constante |
| Foco editorial | Política, milícias, corrupção, cassações, jogo do bicho |
| Tier | **B** |
| Destaque | Publicou sobre condenação de Waguinho por desvio do Fundeb |

---

#### Brava Baixada
| Campo | Valor |
|---|---|
| URL | https://bravabaixada.com.br |
| RSS | **https://bravabaixada.com.br/feed/** |
| Municípios cobertos | 13 municípios da Baixada — seção individual por município |
| Atividade | Muito alta — posts a cada minutos |
| Foco editorial | Notícias positivas, cultura, saúde, obras |
| Tier | **C** |
| Observação | Pouco investigativo — útil para contexto e para municípios sem outra cobertura (Magé, Guapimirim, Queimados) |

URLs por município: `bravabaixada.com.br/municipios/[nome]/noticias/`
Nova Iguaçu · Duque de Caxias · Belford Roxo · São João de Meriti · Nilópolis · Queimados · Magé · Guapimirim · Seropédica · Japeri

---

### SEM RSS — Acesso por scraping

---

#### Notícias da Baixada ⭐ PRIORITÁRIO
| Campo | Valor |
|---|---|
| URL | https://www.noticiasdabaixada.com |
| RSS | Não disponível — scraping necessário |
| Municípios cobertos | Belford Roxo, Nova Iguaçu, Mesquita, Duque de Caxias, Japeri |
| Atividade | Muito alta — 30+ categorias, múltiplos posts/dia |
| Foco editorial | **MPRJ, inquéritos, irregularidades, política, segurança** |
| Tier | **B+** |
| Destaque | "MPRJ aponta direcionamento de contratos na Saúde; Waguinho é réu" — conteúdo exato do projeto |

---

#### Notícias de Belford Roxo
| Campo | Valor |
|---|---|
| URL | https://www.noticiasdebelfordroxo.com |
| RSS | Blogger configurado mas feed vazio — scraping necessário |
| Municípios cobertos | Belford Roxo (exclusivo) |
| Atividade | Alta — 93 posts em abril 2026 |
| Foco editorial | Política municipal, atos oficiais, irregularidades |
| Arquivo desde | 2012 |
| Tier | **B** |
| Destaque | Cobriu: "Waguinho vira réu por fraude em licitação" e "Justiça bloqueia R$ 60M" |

---

#### Jornal Baixada em Foco
| Campo | Valor |
|---|---|
| URL | https://jornalbaixadaemfoco.com.br |
| RSS | Não confirmado — scraping necessário |
| Municípios cobertos | Baixada Fluminense geral |
| Atividade | Ativa — múltiplos posts/dia |
| Antiguidade | 18 anos |
| Foco editorial | Política municipal, governo estadual, denúncias |
| Tier | **B** |
| Destaque | Seção "Boca no Trombone" — canal de denúncias da comunidade |

---

#### Jornal Atual
| Campo | Valor |
|---|---|
| URL | https://jornalatual.com.br |
| RSS | Não disponível (erro 500) |
| Municípios cobertos | Itaguaí, Seropédica, Mangaratiba |
| Atividade | Ativa — múltiplos posts/dia |
| Antiguidade | 25 anos |
| Foco editorial | Governo municipal, obras, saúde, política local |
| Tier | **B** |
| Destaque | Única cobertura jornalística regular de Itaguaí e Seropédica |

---

#### A Voz da Serra
| Campo | Valor |
|---|---|
| URL | https://avozdaserra.com.br |
| RSS | A verificar |
| Municípios cobertos | Cachoeiras de Macacu + Região Serrana |
| Atividade | Ativa |
| Tier | **C** |

---

### DESCARTADOS (verificados — não atendem)

| Portal | Motivo do descarte |
|---|---|
| Jornal Nova Iguaçu (jornalnovaiguacu.com) | RSS ativo mas conteúdo de wire nacional, não local |
| Portal Nova Iguaçu (portalnovaiguacu.com.br) | RSS com apenas 2 posts de teste desde 2024 |
| Jornal do Rio (jornaldorj.com.br) | RSS de celebridade/entretenimento, sem cobertura municipal |
| Agenda do Poder (agendadopoder.com.br) | RSS nacional/estadual, não municipal |
| Correio Carioca (correiocarioca.com.br) | RSS desatualizado desde julho 2025 |
| Portal Guapimirim (portalguapimirim.com.br) | Foco em turismo, sem política municipal |
| A Voz dos Municípios (vozdosmunicipios.com.br) | Foco em avisos oficiais, sem RSS, sem investigação |

---

## RESUMO OPERACIONAL

### RSS ativos no pipeline

```
NACIONAIS / TIER A
  G1 Rio          →  https://g1.globo.com/rss/g1/rio-de-janeiro/
  Extra (Globo)   →  https://extra.globo.com/rss.xml           [verificar atividade]
  O Dia           →  https://odia.ig.com.br/rss.xml            [verificar URL]
  Agência Brasil  →  https://agenciabrasil.ebc.com.br/rss/ultimasnoticias/feed.xml

NACIONAIS / TIER B
  Metrópoles      →  https://www.metropoles.com/feed
  R7              →  https://noticias.r7.com/feed               [URL pendente verificação]
  CNN Brasil      →  https://www.cnnbrasil.com.br/feed          [URL pendente verificação]
  BandNews RJ     →  https://bandnewstv.band.uol.com.br/feed/   [URL pendente verificação]

BAIXADA GERAL / TIER B-C
  Tempo Real RJ   →  https://temporealrj.com/feed/
  Destaque        →  https://www.jornaldestaquebaixada.com/feeds/posts/default
  Folha da Baixada→  https://folhadabaixada.com.br/feed/
  Brava Baixada   →  https://bravabaixada.com.br/feed/

POR MUNICÍPIO
  Nova Iguaçu     →  https://www.zmnoticias.com.br/feed/
  Nova Iguaçu (*) →  https://novaiguacu24h.com.br/feed/         [confirmar atividade]
  Duque de Caxias →  https://duquecaxiensetv.com/feed/
  Duque de Caxias →  https://www.noticiasdeduquedecaxias.com/feeds/posts/default
  Belford Roxo    →  https://belfordroxo24h.com/feed/
  São João Meriti →  https://www.noticiasdesaojoaodemeriti.com/feeds/posts/default
  São João Meriti →  https://meriti.rj.gov.br/inicio/feed/       [Tier A — prefeitura]
  Mesquita        →  https://www.noticiasdemesquita.com/feeds/posts/default
  Queimados       →  https://queimados.rj.gov.br/feed/           [Tier A — prefeitura]
  Queimados       →  https://www.noticiasdequeimados.com/feeds/posts/default
  Magé            →  https://portal.camaramage.rj.gov.br/feed/   [Tier A — câmara]
  Magé            →  https://conexaomage.com.br/feed/
  Japeri          →  https://japeri.rj.gov.br/feed/              [Tier A — prefeitura]
  Guapimirim      →  https://guapimirim.rj.gov.br/novosite/feed/ [Tier A — prefeitura]
  Seropédica      →  https://www.seropedicaonline.com/feed/
  Itaguaí         →  https://www.itaguai.rj.leg.br/institucional/noticias/agregador/RSS  [Tier A — câmara]
  Itaguaí         →  https://www.noticiasdeitaguai.com/feeds/posts/default [atividade baixa]
  Paracambi       →  https://paracambi.rj.gov.br/feed/           [Tier A — prefeitura]

DESATIVADOS
  MPF/PR-RJ       →  URL retorna 404 — novo endpoint a confirmar
```

### API REST para integração imediata

```
TCE-RJ  →  https://dados.tcerj.tc.br/api
  Endpoints prioritários:
    /obras-paralisadas   — obras inacabadas
    /contratos           — contratos por município
    /licitacoes          — processos licitatórios
    /compras-diretas     — dispensas de licitação
```

### Fontes que necessitam scraping

```
Notícias da Baixada  →  https://www.noticiasdabaixada.com       [B+ — prioritário]
Notícias Belford Rxo →  https://www.noticiasdebelfordroxo.com   [B]
Baixada em Foco      →  https://jornalbaixadaemfoco.com.br       [B]
Jornal Atual         →  https://jornalatual.com.br               [B — Itaguaí/Seropédica]
MPRJ                 →  https://www.mprj.mp.br/home/-/detalhe-noticia/todas
DOERJ                →  https://portal.ioerj.com.br  (ou JusBrasil)
```

### Gaps de cobertura — próximas ações

```
MUNICÍPIO AINDA FRACO:
  Nilópolis  — apenas Brava Baixada; buscar portal local independente

CAPITAL:
  Zona Norte e Zona Oeste — sem fonte dedicada identificada
  Subúrbio carioca        — sem fonte dedicada identificada

FONTES PRIMÁRIAS A CONFIRMAR:
  TRE-RJ RSS (erro de conexão na verificação)
  TCM-RJ RSS
  Diário Oficial do Município do Rio de Janeiro RSS
```

---

## TIERS DE QUALIDADE — REFERÊNCIA

| Tier | Critério | Ação no relatório |
|---|---|---|
| **A** | Documento oficial (TCE, MPE, DOERJ, TRE) | Publicar com confiança |
| **B** | Múltiplos portais + declaração oficial citada | Publicar com ressalva padrão |
| **C** | Portal único estabelecido, sem documento oficial | Publicar indicando fonte única |
| **D** | Fonte não verificada ou somente redes sociais | Não publicar — investigar antes |
