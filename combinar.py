import pandas as pd
from bs4 import BeautifulSoup
import re

def eh_vaga_de_ti(titulo, exigir_estagio=False):
    t = str(titulo).lower()
    ok = bool(re.search(INCLUIR, t)) and not re.search(EXCLUIR, t)
    if exigir_estagio:
        ok = ok and bool(re.search(r"est[aá]gi", t))
    return ok

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
    r"|departamento pessoal|coordenador|acad[eê]mico|enfermagem|redes sociais|backoffice"
    r"|doc[eê]ncia|horista|especialista de ensino|cftv|seguran[cç]a eletr[oô]nica|jovem aprendiz)"
)

def limpar_texto(texto):
    if not isinstance(texto, str):
        return ""
    puro = BeautifulSoup(texto, "html.parser").get_text(" ")
    return " ".join(puro.split())

def preparar_gupy():
    gupy = pd.read_csv("vagas_brutas.csv")
    gupy["descricao_limpa"] = gupy["description"].apply(limpar_texto)

    gupy = gupy[gupy["name"].apply(eh_vaga_de_ti)].copy()

    gupy["chave"] = (
    gupy["careerPageName"].fillna("")
    + "|" + gupy["name"].str.lower().str[:30]
    + "|" + gupy["descricao_limpa"].str[:250]
    )
    gupy = gupy.drop_duplicates(subset="chave")


    return pd.DataFrame({
    "fonte": "Gupy",
    "id": "gupy_" + gupy["id"].astype(str),
    "titulo": gupy["name"],
    "empresa": gupy["careerPageName"],
    "cidade": gupy["city"],
    "estado": gupy["state"],
    "modalidade": gupy["workplaceType"],
    "descricao": gupy["descricao_limpa"],
    "salario_min": pd.NA,
    "salario_max": pd.NA,
    "url": gupy["jobUrl"],
    })

def separar_local(loc):
    if not isinstance(loc, str) or loc.strip() in ("", "Todo Brasil", "Localização não informada"):
        return pd.Series([None, None])
    partes = loc.rsplit(" - ", 1)
    if len(partes) == 2:
        return pd.Series([partes[0].strip(), partes[1].strip()])
    return pd.Series([loc.strip(), None])

def parse_salario(texto):
    if not isinstance(texto, str) or "combinar" in texto.lower():
        return pd.Series([pd.NA, pd.NA])
    numeros = re.findall(r"R\$\s?([\d\.]+,\d{2}|\d+,\d{2})", texto)
    valores = [float(n.replace(".", "").replace(",", ".")) for n in numeros]
    if not valores:
        return pd.Series([pd.NA, pd.NA])
    if len(valores) == 1:
        return pd.Series([valores[0], valores[0]])
    return pd.Series([min(valores), max(valores)])

def preparar_infojobs():
    ij = pd.read_csv("vagas_infojobs.csv")
    ij = ij[ij["name"].apply(lambda t: eh_vaga_de_ti(t, exigir_estagio=True))].copy()
    ij["descricao_limpa"] = ij["description"].apply(limpar_texto)

    ij["chave"] = (
        ij["careerPageName"].fillna("")
        + "|" + ij["name"].str.lower().str[:30]
        + "|" + ij["descricao_limpa"].str[:250]
    )
    ij = ij.drop_duplicates(subset="chave")

    ij[["cidade", "estado_sigla"]] = ij["location"].apply(separar_local)
    ij["estado"] = ij["estado_sigla"].map(UF_NOME)

    ij[["salario_min", "salario_max"]] = ij["salario_texto"].apply(parse_salario)

    suspeito = (ij["salario_max"] > ij["salario_min"] * 3) & ij["salario_min"].notna()
    ij.loc[suspeito, ["salario_min", "salario_max"]] = pd.NA


    return pd.DataFrame({
    "fonte": "InfoJobs",
    "id": "ij_" + ij["id"].astype(str),
    "titulo": ij["name"],
    "empresa": ij["careerPageName"],
    "cidade": ij["cidade"],
    "estado": ij["estado"],
    "modalidade": ij["workplaceType"],
    "descricao": ij["descricao_limpa"],
    "salario_min": ij["salario_min"],
    "salario_max": ij["salario_max"],
    "url": ij["url"],
    })

if __name__ == "__main__":
    gupy = preparar_gupy()
    infojobs = preparar_infojobs()
    todas = pd.concat([gupy, infojobs], ignore_index=True)
    print("TOTAL:", len(todas))







