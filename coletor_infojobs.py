import re
import time
from urllib.parse import quote

import requests
import pandas as pd
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (projeto academico - analise de vagas de estagio)"}
BASE = "https://www.infojobs.com.br/mf-publicarea/VacancyList/GetVacancyListFragment"

FORMAS = ["estágio", "estagiário"]
ASSUNTOS = ["ti", "dados", "desenvolvimento de sistemas", "suporte técnico ti",
            "python", "sql", "banco de dados", "infraestrutura ti"]
TERMOS = [f"{forma} {assunto}" for forma in FORMAS for assunto in ASSUNTOS]

def coletar_termo(termo):
    alvo = montar_url_alvo(termo, 1)
    resposta = requests.get(BASE, params={"url": alvo}, headers=HEADERS, timeout=15)
    resposta.raise_for_status()
    corpo = resposta.json()
    print(termo, "->", len(corpo["listFragmentHTML"]), "caracteres de HTML")
    return []

if __name__ == "__main__":
    todas = []
    for termo in TERMOS:
        vagas_termo = coletar_termo(termo)
        for v in vagas_termo:
            v["termo_busca"] = termo
        todas.extend(vagas_termo)
        time.sleep(1)

    print("Total coletado:", len(todas))










