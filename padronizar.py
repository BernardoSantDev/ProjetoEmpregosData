from pathlib import Path
import pandas as pd
import re
from bs4 import BeautifulSoup


PASTA_DADOS = Path(__file__).resolve().parent / "dados"

ARQUIVOS = {
    "Gupy": "vagas_gupy.csv",
    "InfoJobs": "vagas_infojobs_atual.csv",
    "Super Estágios": "vagas_superestagios.csv"
}


MAPEAMENTOS = {
    "Gupy": {
        "id": "id_fonte",
        "name": "titulo",
        "careerPageName": "empresa",
        "city": "cidade",
        "state": "estado",
        "description": "descricao",
        "workplaceType": "modalidade",
        "publishedDate": "data_publicacao",
        "applicationDeadline": "prazo_inscricao",
        "jobUrl": "url"
    },

    "InfoJobs": {
        "id": "id_fonte",
        "name": "titulo",
        "careerPageName": "empresa",
        "location": "localizacao",
        "workplaceType": "modalidade",
        "description": "descricao"
    },

    "Super Estágios": {
        "id": "id_fonte",
        "atividades": "descricao",
        "bolsa": "salario_texto"
    }
}


COLUNAS_PADRAO = [
    "fonte",
    "id_fonte",
    "titulo",
    "empresa",
    "cidade",
    "estado",
    "localizacao",
    "modalidade",
    "descricao",
    "salario_texto",
    "bolsa_valor",
    "data_publicacao",
    "prazo_inscricao",
    "cursos",
    "url",
    "area_pesquisada"
]


def limpar_texto(valor):
    if pd.isna(valor):
        return pd.NA

    texto = BeautifulSoup(
        str(valor),
        "html.parser"
    ).get_text(" ", strip=True)

    texto = re.sub(r"\s+", " ", texto).strip()

    if not texto:
        return pd.NA

    return texto



def normalizar_estado(valor):
    if pd.isna(valor):
        return pd.NA

    texto = str(valor).strip()

    estados = {
        "acre": "AC",
        "alagoas": "AL",
        "amapá": "AP",
        "amazonas": "AM",
        "bahia": "BA",
        "ceará": "CE",
        "distrito federal": "DF",
        "espírito santo": "ES",
        "goiás": "GO",
        "maranhão": "MA",
        "mato grosso": "MT",
        "mato grosso do sul": "MS",
        "minas gerais": "MG",
        "pará": "PA",
        "paraíba": "PB",
        "paraná": "PR",
        "pernambuco": "PE",
        "piauí": "PI",
        "rio de janeiro": "RJ",
        "rio grande do norte": "RN",
        "rio grande do sul": "RS",
        "rondônia": "RO",
        "roraima": "RR",
        "santa catarina": "SC",
        "são paulo": "SP",
        "sergipe": "SE",
        "tocantins": "TO"
    }

    siglas = set(estados.values())

    if texto.upper() in siglas:
        return texto.upper()

    return estados.get(texto.casefold(), pd.NA)



def preparar_fontes(area):
    tabelas = {}

    for fonte, arquivo in ARQUIVOS.items():
        caminho = PASTA_DADOS / arquivo

        if not caminho.exists():
            print(f"Arquivo não encontrado: {arquivo}")
            continue

        df = pd.read_csv(
            caminho,
            encoding="utf-8-sig",
            dtype={"id": "string"}
        )

        df = df.rename(columns=MAPEAMENTOS[fonte])

        df["fonte"] = fonte
        df["area_pesquisada"] = area

        df = df.reindex(columns=COLUNAS_PADRAO)

        tabelas[fonte] = df

        print(f"\n{fonte}: {len(df)} vagas")
        print(df[["id_fonte", "titulo", "empresa"]].head(2))

    return tabelas



def consolidar_pesquisa(area):
    tabelas = preparar_fontes(area)

    if not tabelas:
        print("Nenhuma tabela disponível.")
        return None

    df_final = pd.concat(
        tabelas.values(),
        ignore_index=True
    )


    colunas_texto = [
        "titulo",
        "empresa",
        "descricao",
        "cursos",
        "localizacao",
        "cidade",
        "estado",
        "salario_texto"
    ]

    for coluna in colunas_texto:
        df_final[coluna] = df_final[coluna].map(limpar_texto)

    mascara_datas = (
        df_final["fonte"].eq("InfoJobs")
        & df_final["descricao"].fillna("").str.fullmatch(
            r"\d{1,2}\s+(?:jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez)",
            case=False
        )
    )

    print(
        f"Descrições inválidas do InfoJobs: {mascara_datas.sum()}"
    )

    df_final.loc[mascara_datas, "descricao"] = pd.NA


    mascara_infojobs = df_final["fonte"].eq("InfoJobs")

    localizacoes = df_final.loc[
        mascara_infojobs, "localizacao"
    ].str.extract(
        r"^\s*(.*?)\s+-\s+([A-Za-z]{2})\s*$"
    )

    df_final.loc[
        mascara_infojobs, "cidade"
    ] = localizacoes[0]

    df_final.loc[
        mascara_infojobs, "estado"
    ] = localizacoes[1]

    df_final["cidade"] = df_final["cidade"].map(
        limpar_texto
    )

    df_final["estado"] = df_final["estado"].map(
        normalizar_estado
    )

    print("\nPADRONIZAÇÃO DE LOCALIZAÇÃO")

    print(
        "Cidades identificadas:",
        df_final["cidade"].notna().sum()
    )

    print(
        "Estados identificados:",
        df_final["estado"].notna().sum()
    )

    print(
        df_final[
            ["fonte", "cidade", "estado"]
        ].groupby("fonte", sort=False).head(2).to_string(index=False)
    )

    arquivo_saida = PASTA_DADOS / "vagas_padronizadas.csv"

    df_final.to_csv(
        arquivo_saida,
        index=False,
        encoding="utf-8-sig"
    )

    print("\nCONSOLIDAÇÃO FINALIZADA")
    print(f"Total de registros: {len(df_final)}")
    print(f"Arquivo salvo em: {arquivo_saida}")

    return df_final




if __name__ == "__main__":
    area = input("Área pesquisada: ").strip()

    if area:
        consolidar_pesquisa(area)
    else:
        print("Informe uma área válida.")
