param(
    [string]$Task = "ajuda"
)

$hoje     = (Get-Date).ToString("yyyy-MM-dd")
$ontem    = (Get-Date).AddDays(-1).ToString("yyyy-MM-dd")
$semana   = (Get-Date).AddDays(-6).ToString("yyyy-MM-dd")

switch ($Task) {

    "hoje" {
        Write-Host "Coletando pautas de hoje ($hoje)..." -ForegroundColor Cyan
        python pipeline.py --data $hoje
    }

    "ontem" {
        Write-Host "Coletando pautas de ontem ($ontem)..." -ForegroundColor Cyan
        python pipeline.py --data $ontem
    }

    "semana" {
        Write-Host "Relatório da semana ($semana a $hoje)..." -ForegroundColor Cyan
        python pipeline.py --data $semana --data-fim $hoje --top 30
    }

    "municipios" {
        Write-Host "Municípios disponíveis:" -ForegroundColor Yellow
        @(
            "nova-iguacu", "duque-de-caxias", "sao-joao-de-meriti",
            "belford-roxo", "nilopolis", "mesquita",
            "queimados", "japeri", "mage",
            "guapimirim", "seropedica", "itaguai",
            "paracambi", "rio-de-janeiro"
        ) | ForEach-Object { Write-Host "  $_" }
    }

    "relatorio" {
        Write-Host "Gerando relatório de hoje sem coletar..." -ForegroundColor Cyan
        python -c "
from relatorio import gerador
import db
conteudo = gerador.gerar('$hoje', top_n=20)
caminho = gerador.salvar(conteudo, '$hoje')
print(f'Salvo em: {caminho}')
"
    }

    "teste" {
        Write-Host "Rodando em banco de teste isolado..." -ForegroundColor Yellow
        python pipeline.py --data $hoje --db testes/teste.db
    }

    "ajuda" {
        Write-Host ""
        Write-Host "Plantao de Noticias — Atalhos" -ForegroundColor Green
        Write-Host "------------------------------"
        Write-Host "  .\run.ps1 hoje        Coleta e relatorio de hoje"
        Write-Host "  .\run.ps1 ontem       Coleta e relatorio de ontem"
        Write-Host "  .\run.ps1 semana      Relatorio dos ultimos 7 dias"
        Write-Host "  .\run.ps1 relatorio   So gera o relatorio (sem coletar)"
        Write-Host "  .\run.ps1 municipios  Lista slugs de municipios"
        Write-Host "  .\run.ps1 teste       Roda em banco isolado (nao afeta o principal)"
        Write-Host ""
        Write-Host "Uso avancado direto:" -ForegroundColor Yellow
        Write-Host "  python pipeline.py --data 2026-05-06"
        Write-Host "  python pipeline.py --data 2026-05-01 --data-fim 2026-05-06"
        Write-Host "  python pipeline.py --municipio belford-roxo --top 5"
        Write-Host ""
    }

    default {
        Write-Host "Tarefa desconhecida: '$Task'. Use '.\run.ps1 ajuda' para ver os comandos." -ForegroundColor Red
    }
}
