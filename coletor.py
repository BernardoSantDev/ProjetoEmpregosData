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

#def coletar_termo(termo)
    

if __name__ == "__main__":
    todas = []
    for termo in TERMOS:
        vagas_termo = coletar_termo(termo)
        for v in vagas_termo:
            v["termo_busca"] = termo
        todas.extend(vagas_termo)
        time.sleep(1)



