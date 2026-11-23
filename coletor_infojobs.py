
import re
import time
import unicodedata
from pathlib import Path
from urllib.parse import quote, urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup


BASE = "https://www.infojobs.com.br"

URL = (
    "https://www.infojobs.com.br/"
    "mf-publicarea/VacancyList/GetVacancyListFragment"
)

HEADERS = {
    "User-Agent": "ObservatorioEstagios/1.0",
    "Accept": "application/json"
}

COLUNAS = [
    "id",
    "url",
    "name",
    "careerPageName",
    "location",
    "salario_texto",
    "escolaridade",
    "experiencia",
    "workplaceType",
    "description",
    "termo_busca",
    "fonte",
    "area_pesquisada"
]


def normalizar_texto(texto):
    if not isinstance(texto, str):
        return ""

    texto = texto.lower().strip()

    texto = unicodedata.normalize("NFKD", texto)

    texto = "".join(
        letra for letra in texto
        if not unicodedata.combining(letra)
    )

    return " ".join(texto.split())


def limpar_texto(texto):
    if not texto:
        return ""

    return " ".join(str(texto).split())


def gerar_termos(area):
    return [
        f"estágio {area}",
        f"estágio em {area}",
        f"estagiário {area}",
        f"estagiária {area}"
    ]


def eh_estagio_da_area(vaga, area):
    titulo = normalizar_texto(vaga.get("name"))

    descricao = normalizar_texto(
        vaga.get("description")
    )

    area = normalizar_texto(area)

    sinonimos = {
        "ti": [
            "ti",
            "t.i.",
            "tecnologia da informacao",
            "informatica",
            "desenvolvimento de sistemas"
        ],
        "dados": [
            "dados",
            "data science",
            "data analytics",
            "business intelligence",
            "bi"
        ],
        "administracao": [
            "administracao",
            "administrativo"
        ]
    }

    areas_validas = sinonimos.get(area, [area])

    padrao_estagio = (
        r"\b(?:estagio|estagiari[oa]s?)\b"
    )

    eh_estagio = bool(
        re.search(padrao_estagio, titulo)
    )

    texto_completo = titulo + " " + descricao

    eh_area = any(
        re.search(
            r"\b" + re.escape(termo) + r"\b",
            texto_completo
        )
        for termo in areas_validas
    )

    return eh_estagio and eh_area


def montar_url_alvo(termo, pagina):
    slug = quote(
        termo.lower(),
        safe=""
    ).replace("%20", "+")

    return (
        f"{BASE}/vagas-de-emprego-"
        f"{slug}.aspx?page={pagina}"
    )


def extrair_vagas(html):
    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    cards = soup.select(
        "div.grid-row.js_rowCard"
    )

    resultados = []

    for card in cards:
        interior = card.select_one(
            "div.js_cardLink"
        )

        if interior is None:
            continue

        vaga_id = interior.get("data-id")
        href = interior.get("data-href")

        titulo_tag = card.select_one(
            "h2.js_vacancyTitle"
        )

        titulo = (
            limpar_texto(titulo_tag.get_text(" "))
            if titulo_tag else None
        )

        empresa_tag = card.select_one(
            "div.text-body a"
        )

        empresa = (
            limpar_texto(empresa_tag.get_text(" "))
            if empresa_tag else None
        )

        localizacao = None

        for div in card.find_all(
            "div",
            class_="mb-8"
        ):
            if "d-inline-flex" not in div.get("class", []):
                oculto = div.select_one("span[hidden]")

                if oculto:
                    oculto.decompose()

                localizacao = limpar_texto(
                    div.get_text(" ")
                )

                break

        def texto_icone(classe):
            icone = card.select_one(
                f"svg.{classe}"
            )

            if icone and icone.parent:
                return limpar_texto(
                    icone.parent.get_text(" ")
                )

            return None

        salario = texto_icone("icon-money")

        escolaridade = texto_icone(
            "icon-graduate-hat"
        )

        experiencia = texto_icone(
            "icon-suitcase"
        )

        modalidade = (
            texto_icone("icon-buildings")
            or texto_icone("icon-house-and-building")
            or texto_icone("icon-user-home")
        )

        descricao_tag = card.select_one(
            "div.text-medium"
        )

        descricao = (
            limpar_texto(descricao_tag.get_text(" "))
            if descricao_tag else None
        )

        if not vaga_id or not titulo:
            continue

        resultados.append({
            "id": str(vaga_id),
            "url": urljoin(BASE, href) if href else None,
            "name": titulo,
            "careerPageName": empresa,
            "location": localizacao,
            "salario_texto": salario,
            "escolaridade": escolaridade,
            "experiencia": experiencia,
            "workplaceType": modalidade,
            "description": descricao
        })

    return resultados


def coletar_termo(sessao, termo, max_paginas=2):
    vagas = []

    for pagina in range(1, max_paginas + 1):
        alvo = montar_url_alvo(termo, pagina)

        resposta = sessao.get(
            URL,
            params={"url": alvo},
            timeout=20
        )

        if resposta.status_code in (403, 429):
            raise PermissionError(
                f"Acesso indisponível ou limitado: "
                f"HTTP {resposta.status_code}"
            )

        resposta.raise_for_status()

        corpo = resposta.json()

        html = corpo.get("listFragmentHTML")

        if not isinstance(html, str):
            raise ValueError(
                "Formato inesperado na resposta do InfoJobs."
            )

        pagina_vagas = extrair_vagas(html)

        if not pagina_vagas:
            break

        vagas.extend(pagina_vagas)

        if corpo.get("eof"):
            break

        if pagina < max_paginas:
            time.sleep(2)

    return vagas


def coletar_infojobs(area, max_paginas=2):
    area = area.strip()

    if not area:
        raise ValueError("Informe uma área válida.")

    termos = gerar_termos(area)

    vagas_unicas = {}

    with requests.Session() as sessao:
        sessao.headers.update(HEADERS)

        for termo in termos:
            print(f"\nPesquisando: {termo}")

            encontradas = coletar_termo(
                sessao,
                termo,
                max_paginas=max_paginas
            )

            print(
                f"Anúncios recebidos: {len(encontradas)}"
            )

            for vaga in encontradas:
                if not eh_estagio_da_area(vaga, area):
                    continue

                vaga_id = vaga["id"]

                if vaga_id in vagas_unicas:
                    continue

                vaga["termo_busca"] = termo
                vaga["fonte"] = "InfoJobs"
                vaga["area_pesquisada"] = area

                vagas_unicas[vaga_id] = vaga

            print(
                f"Vagas únicas acumuladas: "
                f"{len(vagas_unicas)}"
            )

            time.sleep(2)

    df = pd.DataFrame(
        vagas_unicas.values(),
        columns=COLUNAS
    )

    df = df.drop_duplicates(
        subset="id",
        keep="last"
    )

    pasta = Path(__file__).resolve().parent / "dados"

    pasta.mkdir(exist_ok=True)

    arquivo = pasta / "vagas_infojobs_atual.csv"

    df.to_csv(
        arquivo,
        index=False,
        encoding="utf-8-sig"
    )

    print("\nColeta finalizada!")
    print(f"Área pesquisada: {area}")
    print(f"Total de vagas únicas: {len(df)}")
    print(f"Arquivo salvo em: {arquivo}")

    return df


if __name__ == "__main__":
    area = input(
        "Qual área de estágio deseja pesquisar? "
    ).strip()

    try:
        coletar_infojobs(area)

    except (
        requests.RequestException,
        ValueError,
        PermissionError
    ) as erro:
        print(f"\nErro durante a coleta: {erro}")
