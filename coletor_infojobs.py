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


def montar_url_alvo(termo, page):
    slug = quote(termo.lower(), safe="").replace("%20", "+")
    return f"https://www.infojobs.com.br/vagas-de-emprego-{slug}.aspx?page={page}"

def limpar_texto(texto):
    if not texto:
        return ""
    return " ".join(texto.split())

def extrair_vagas(html):
    soup = BeautifulSoup(html, "html.parser")
    resultados = []
    for card in soup.select("div.grid-row.js_rowCard"):
        interior = card.select_one("div.js_cardLink")
        vaga_id = interior.get("data-id") if interior else None

        titulo_tag = card.select_one("h2.js_vacancyTitle")
        titulo = limpar_texto(titulo_tag.get_text()) if titulo_tag else None

        if vaga_id:
            resultados.append({"id": vaga_id, "name": titulo})
    return resultados


def coletar_termo(termo):
    alvo = montar_url_alvo(termo, 1)
    resposta = requests.get(BASE, params={"url": alvo}, headers=HEADERS, timeout=15)
    resposta.raise_for_status()
    corpo = resposta.json()
    return extrair_vagas(corpo["listFragmentHTML"])
    return []

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
    df = df.drop_duplicates(subset="id")
    print("Depois:", len(df))

    df.to_csv("vagas_infojobs.csv", index=False, encoding="utf-8-sig")
    print("Salvo em vagas_infojobs.csv")










