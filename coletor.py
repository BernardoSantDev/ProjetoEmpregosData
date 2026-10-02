import time
import requests
import pandas as pd

URL = "https://portal.gupy.io/api/job-search/jobs"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (projeto academico - analise de vagas)"
}
FORMAS = ["Estágio", "Estagiário"]
AREAS = ["TI", "Tecnologia", "Dados", "Sistemas", "Desenvolvimento",
         "Software", "Suporte", "Infraestrutura", "BI", "Automação"]
TERMOS = [f"{forma} {area}" for forma in FORMAS for area in AREAS]

def coletar_termo(termo, limit=12, max_vagas=600):
    vagas = []
    offset = 0
    while True:
        resposta = requests.get(URL, params={"jobName": termo, "limit": limit, "offset": offset}, headers=HEADERS, timeout=15)
        resposta.raise_for_status()
        corpo = resposta.json()
        pagina = corpo["data"]
        vagas.extend(pagina)
        offset += limit
        if len(pagina) < limit or len(vagas) >= max_vagas:
            break
        time.sleep(1)
    print(f"{termo}: {len(vagas)} vagas coletadas")
    return vagas

if __name__ == "__main__":
    todas = []
    for termo in TERMOS:
        vagas_termo = coletar_termo(termo)
        for v in vagas_termo:
            v["termo_busca"] = termo
        todas.extend(vagas_termo)
        time.sleep(1)


    df = pd.DataFrame(todas)
    print("\nAntes de remover duplicatas:", len(df))
    df.drop_duplicates(subset="id")
    print("Depois de remover duplicatas:", len(df))

    df = df[df["type"] == "vacancy_type_internship"]
    print("Só estágios:", len(df))

    # LIMPAR CVS
    colunas_uteis = {
        "name": "titulo",
        "careerPageName": "empresa",
        "city": "cidade",
        "state": "estado",
        "workplaceType": "modalidade",
        "publishedDate": "data_publicacao",
        "applicationDeadline": "prazo_inscricao",
        "jobUrl": "link",
        "termo_busca": "termo_busca"
    }

    df_enxuto = df[list(colunas_uteis.keys())].rename(columns=colunas_uteis)
    df_enxuto["data_publicacao"] = pd.to_datetime(df_enxuto["data_publicacao"]).dt.date
    df_enxuto["prazo_inscricao"] = pd.to_datetime(df_enxuto["prazo_inscricao"]).dt.date

    df_enxuto.to_csv("vagas_brutas.csv", index=False, encoding="utf-8-sig")
    print("Salvo em vagas_brutas.csv")

