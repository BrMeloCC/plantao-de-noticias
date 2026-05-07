#!/usr/bin/env python3
"""
Plantão de Notícias — Interface interativa.
Uso: python cli.py
"""
from datetime import date, timedelta

import questionary
from questionary import Style

import pipeline

_ESTILO = Style([
    ("qmark",        "fg:#00bfff bold"),
    ("question",     "bold"),
    ("answer",       "fg:#00ff99 bold"),
    ("pointer",      "fg:#00bfff bold"),
    ("highlighted",  "fg:#00bfff bold"),
    ("selected",     "fg:#00ff99"),
    ("separator",    "fg:#555555"),
    ("instruction",  "fg:#888888"),
])

_TEMAS = [
    ("Todos os temas",                          None),
    ("Crime Organizado / Milícia",              "crime-organizado"),
    ("Licitação Suspeita",                      "licitacao-suspeita"),
    ("Compra de Voto",                          "compra-de-voto"),
    ("Improbidade Administrativa",              "improbidade-administrativa"),
    ("Obras Inacabadas / Superfaturadas",       "obras-inacabadas"),
    ("Gasto Irregular com Dinheiro Público",    "gasto-irregular"),
    ("Saúde Pública",                           "saude-publica"),
    ("Educação",                                "educacao"),
    ("Segurança Pública",                       "seguranca-publica"),
    ("Eleições / Política Eleitoral",           "eleicoes"),
    ("Greve / Paralisação",                     "greve"),
]

_MUNICIPIOS = [
    ("Todos os municípios",    None),
    ("Nova Iguaçu",            "nova-iguacu"),
    ("Duque de Caxias",        "duque-de-caxias"),
    ("Belford Roxo",           "belford-roxo"),
    ("São João de Meriti",     "sao-joao-de-meriti"),
    ("Nilópolis",              "nilopolis"),
    ("Rio de Janeiro",         "rio-de-janeiro"),
    ("Mesquita",               "mesquita"),
    ("Queimados",              "queimados"),
    ("Japeri",                 "japeri"),
    ("Magé",                   "mage"),
    ("Guapimirim",             "guapimirim"),
    ("Seropédica",             "seropedica"),
    ("Itaguaí",                "itaguai"),
    ("Paracambi",              "paracambi"),
]

_DATAS = {
    "Hoje":                    (date.today().isoformat(), None),
    "Ontem":                   (str(date.today() - timedelta(days=1)), None),
    "Últimos 7 dias":          (str(date.today() - timedelta(days=6)), date.today().isoformat()),
    "Últimos 30 dias":         (str(date.today() - timedelta(days=29)), date.today().isoformat()),
    "Data personalizada":      None,
}


def _perguntar_data() -> tuple[str, str | None]:
    escolha = questionary.select(
        "Período:",
        choices=list(_DATAS.keys()),
        style=_ESTILO,
    ).ask()

    if escolha is None:
        raise SystemExit

    if escolha != "Data personalizada":
        return _DATAS[escolha]

    data_ini = questionary.text(
        "Data inicial (YYYY-MM-DD):",
        default=date.today().isoformat(),
        style=_ESTILO,
        validate=lambda v: len(v) == 10 and v[4] == "-" and v[7] == "-" or "Formato inválido",
    ).ask()

    if data_ini is None:
        raise SystemExit

    usar_fim = questionary.confirm(
        "Definir data final diferente?",
        default=False,
        style=_ESTILO,
    ).ask()

    if not usar_fim:
        return data_ini, None

    data_fim = questionary.text(
        "Data final (YYYY-MM-DD):",
        default=data_ini,
        style=_ESTILO,
        validate=lambda v: len(v) == 10 and v[4] == "-" and v[7] == "-" or "Formato inválido",
    ).ask()

    return data_ini, data_fim


def _perguntar_municipio() -> str | None:
    escolha = questionary.select(
        "Município:",
        choices=[questionary.Choice(nome, value=slug) for nome, slug in _MUNICIPIOS],
        style=_ESTILO,
    ).ask()
    return escolha


def _perguntar_tema() -> str | None:
    escolha = questionary.select(
        "Tema:",
        choices=[questionary.Choice(nome, value=slug) for nome, slug in _TEMAS],
        style=_ESTILO,
    ).ask()
    return escolha


def _perguntar_top() -> int:
    escolha = questionary.select(
        "Número de pautas no relatório:",
        choices=["10", "20", "30", "50"],
        default="10",
        style=_ESTILO,
    ).ask()
    return int(escolha)


def main():
    print()
    print("  Plantão de Notícias")
    print("  -------------------")
    print()

    data_ini, data_fim = _perguntar_data()
    municipio = _perguntar_municipio()
    tema = _perguntar_tema()
    top_n = _perguntar_top()

    periodo = f"{data_ini} a {data_fim}" if data_fim else data_ini
    print()
    print(f"  Período   : {periodo}")
    print(f"  Município : {municipio or 'todos'}")
    print(f"  Tema      : {tema or 'todos'}")
    print(f"  Top N     : {top_n}")
    print()

    confirmar = questionary.confirm("Executar agora?", default=True, style=_ESTILO).ask()
    if not confirmar:
        print("Cancelado.")
        return

    print()
    pipeline.run(
        data_str=data_ini,
        data_fim=data_fim,
        municipio=municipio,
        tema=tema,
        top_n=top_n,
    )


if __name__ == "__main__":
    main()
