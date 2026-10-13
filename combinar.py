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

    return gupy

def preparar_infojobs():
    return pd.DataFrame()

if __name__ == "__main__":
    gupy = preparar_gupy()
    infojobs = preparar_infojobs()
    todas = pd.concat([gupy, infojobs], ignore_index=True)
    print("TOTAL:", len(todas))







