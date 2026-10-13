import re
import time
from urllib.parse import quote

import requests
import pandas as pd
from bs4 import BeautifulSoup

INCLUIR = (
    r"(?:\bti\b|\bt\.i\b|tecnologia da informa|\bdados\b|\bsistemas?\b|\bsoftware\b|\bsw\b"
    r"|programa[cç][aã]o|desenvolvimento (?:de )?(?:sw|software|sistemas|android|fullstack|integra|ia)"
    r"|front.?end|full.?stack|low.?code|help ?desk"
    r"|suporte (?:t[eé]cnico|de ti|ti|de sistemas|e manuten)"
    r"|infraestrutura de ti|banco de dados|ci[eê]ncia de dados|engenharia de dados"
    r"|intelig[eê]ncia artificial|\bia\b|est[aá]gio em tecnologia|estagi[aá]rio em tecnologia"
    r"|governan[cç]a de ti|qualidade de software|testes de software|seguran[cç]a da informa)"
)
EXCLUIR = (
    r"(?:neg[oó]cios|humano|organizacional|fornecedores|treinamento|pesquisa e desenvolvimento"
    r"|arquitetura|engenharia civil|ferramentais|suporte ao cliente|suporte comercial"
    r"|suporte jur|suporte acad|suporte de benef|suporte cl[ií]nico|log[ií]stica|compras"
    r"|concreto|contabilidade|tesouraria|\| rh|controle de dados|desenvolvimento de produto"
    r"|desenvolvimento t[eé]cnico|sistema de gest[aã]o|sistemas de opera|sistema de monitora"
    r"|matem[aá]tica|telecom|eletroeletr|instrumenta|industrial|opera[cç][oõ]es"
    r"|departamento pessoal|coordenador|acad[eê]mico|enfermagem|redes sociais|backoffice)"
)


def eh_vaga_de_ti(titulo):
    t = titulo.lower()
    return bool(re.search(INCLUIR, t)) and not re.search(EXCLUIR, t)


HEADERS = {"User-Agent": "Mozilla/5.0 (projeto academico - analise de vagas de estagio)"}
BASE = "https://www.infojobs.com.br/mf-publicarea/VacancyList/GetVacancyListFragment"

FORMAS = ["estágio", "estagiário"]
ASSUNTOS = ["ti", "dados", "desenvolvimento de sistemas", "suporte técnico ti",
            "python", "sql", "banco de dados", "infraestrutura ti"]
TERMOS = [f"{forma} {assunto}" for forma in FORMAS for assunto in ASSUNTOS]


def limpar_texto(texto):
    if not texto:
        return ""
    return " ".join(texto.split())


def montar_url_alvo(termo, page):
    slug = quote(termo.lower(), safe="").replace("%20", "+")
    return f"https://www.infojobs.com.br/vagas-de-emprego-{slug}.aspx?page={page}"


def extrair_vagas(html):
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("div.grid-row.js_rowCard")
    resultados = []
    for card in cards:
        interior = card.select_one("div.js_cardLink")
        vaga_id = interior.get("data-id") if interior else None
        href = interior.get("data-href") if interior else None

        titulo_tag = card.select_one("h2.js_vacancyTitle")
        titulo = limpar_texto(titulo_tag.get_text()) if titulo_tag else None

        empresa_tag = card.select_one("div.text-body a")
        empresa = limpar_texto(empresa_tag.get_text(" ")) if empresa_tag else None

        local_div = None
        for d in card.find_all("div", class_="mb-8"):
            if "d-inline-flex" not in d.get("class", []):
                local_div = d
                break
        localizacao = None
        if local_div:
            oculto = local_div.select_one("span[hidden]")
            if oculto:
                oculto.decompose()
            localizacao = limpar_texto(local_div.get_text())

        def texto_do_icone(classe_icone):
            svg = card.select_one(f"svg.{classe_icone}")
            return limpar_texto(svg.parent.get_text()) if svg else None

        salario = texto_do_icone("icon-money")
        escolaridade = texto_do_icone("icon-graduate-hat")
        experiencia = texto_do_icone("icon-suitcase")
        modalidade = (texto_do_icone("icon-buildings")
                      or texto_do_icone("icon-house-and-building")
                      or texto_do_icone("icon-user-home"))

        descricao = None
        for d in card.find_all("div"):
            if d.get("class") == ["text-medium"]:
                descricao = limpar_texto(d.get_text())
                break

        if vaga_id:
            resultados.append({
                "id": vaga_id,
                "url": "https://www.infojobs.com.br" + href if href else None,
                "name": titulo, "careerPageName": empresa, "location": localizacao,
                "salario_texto": salario, "escolaridade": escolaridade,
                "experiencia": experiencia, "workplaceType": modalidade,
                "description": descricao,
            })
    return resultados


def coletar_termo(termo, max_paginas=25):
    vagas = []
    for page in range(1, max_paginas + 1):
        alvo = montar_url_alvo(termo, page)
        resposta = requests.get(BASE, params={"url": alvo}, headers=HEADERS, timeout=15)
        resposta.raise_for_status()
        corpo = resposta.json()

        pagina_bruta = extrair_vagas(corpo["listFragmentHTML"])
        if not pagina_bruta:
            break

        pagina_ti = [v for v in pagina_bruta if v["name"] and eh_vaga_de_ti(v["name"])]
        vagas.extend(pagina_ti)

        if corpo.get("eof"):
            break
        time.sleep(1)

    print(f"{termo}: {len(vagas)} vagas de TI")
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
    df = df.drop_duplicates(subset="id")
    print("Depois:", len(df))

    df.to_csv("vagas_infojobs.csv", index=False, encoding="utf-8-sig")
    print("Salvo em vagas_infojobs.csv")