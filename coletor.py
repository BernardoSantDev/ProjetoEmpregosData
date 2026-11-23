
import time
from pathlib import Path

import requests
import pandas as pd


URL = "https://portal.gupy.io/api/job-search/jobs"

HEADERS = {
    "User-Agent": "ObservatorioEstagios/1.0 (projeto academico)"
}


def coletar_termo(termo, limite=12, max_paginas=2):
    vagas = []

    for pagina in range(max_paginas):
        offset = pagina * limite

        parametros = {
            "jobName": termo,
            "limit": limite,
            "offset": offset
        }

        resposta = requests.get(
            URL,
            params=parametros,
            headers=HEADERS,
            timeout=20
        )

        resposta.raise_for_status()
        dados = resposta.json()

        resultados = dados.get("data")

        if not isinstance(resultados, list):
            raise ValueError("Formato inesperado na resposta da Gupy.")

        if not resultados:
            break

        vagas.extend(resultados)

        if len(resultados) < limite:
            break

        time.sleep(1)

    return vagas


def coletar_gupy(termos):
    todas_vagas = []
    ids_encontrados = set()

    for termo in termos:
        print(f"\nPesquisando: {termo}")

        vagas = coletar_termo(termo)

        for vaga in vagas:
            id_vaga = vaga.get("id")
            tipo = vaga.get("type")

            if tipo != "vacancy_type_internship":
                continue

            if id_vaga is None:
                continue

            if id_vaga in ids_encontrados:
                continue

            ids_encontrados.add(id_vaga)

            vaga["termo_busca"] = termo
            todas_vagas.append(vaga)

        print(f"Total acumulado: {len(todas_vagas)}")

        time.sleep(1)

    colunas = [
        "id", "name", "careerPageName",
        "description", "type", "city", "state",
        "workplaceType", "publishedDate",
        "applicationDeadline", "jobUrl", "termo_busca"
    ]

    df = pd.DataFrame(todas_vagas).reindex(columns=colunas)

    pasta = Path("dados")
    pasta.mkdir(exist_ok=True)

    caminho = pasta / "vagas_gupy.csv"

    df.to_csv(caminho, index=False, encoding="utf-8-sig")

    print(f"\nColeta finalizada: {len(df)} vagas únicas.")
    print(f"Arquivo salvo em: {caminho}")

    return df
