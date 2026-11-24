from pathlib import Path
import pandas as pd


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

if __name__ == "__main__":
    area = input("Área pesquisada: ").strip()

    if area:
        preparar_fontes(area)
    else:
        print("Informe uma área válida.")
