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
