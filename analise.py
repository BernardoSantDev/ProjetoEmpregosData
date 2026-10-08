import re
import pandas as pd
from bs4 import BeautifulSoup

df = pd.read_csv("vagas_brutas.csv")
print("Vagas no CSV:", len(df))


def limpar_texto(texto):
    if not isinstance(texto, str):
        return ""

    puro = BeautifulSoup(texto, 'html.parser').get_text(" ")
    return " ".join(puro.split())

df["descricao_limpa"] = df["description"].apply(limpar_texto)

INCLUIR = (
    r"(?:\bti\b|\bt\.i\b|tecnologia da informa|\bdados\b|\bsistemas?\b|\bsoftware\b|\bsw\b"
    r"|programa[cç][aã]o|desenvolvimento (?:de )?(?:sw|software|sistemas|android|fullstack|integra|ia|projetos \(bd\))"
    r"|front.?end|full.?stack|low.?code|help ?desk"
    r"|suporte (?:t[eé]cnico|de ti|ti|de sistemas|e manuten)"
    r"|infraestrutura de ti|banco de dados|ci[eê]ncia de dados|engenharia de dados"
    r"|intelig[eê]ncia artificial|\bia\b|est[aá]gio em tecnologia|estagi[aá]rio em tecnologia"
    r"|governan[cç]a de ti|qualidade de software|testes de software)"
)

EXCLUIR = (
    r"(?:neg[oó]cios|humano|organizacional|fornecedores|treinamento|pesquisa e desenvolvimento"
    r"|arquitetura|engenharia civil|ferramentais|suporte ao cliente|suporte comercial"
    r"|suporte jur|suporte acad|suporte de benef|suporte cl[ií]nico|log[ií]stica|compras"
    r"|concreto|contabilidade|tesouraria|\| rh|controle de dados|desenvolvimento de produto"
    r"|desenvolvimento t[eé]cnico|sistema de gest[aã]o|sistemas de opera|sistema de monitora"
    r"|matem[aá]tica|telecom|eletroeletr|instrumenta|industrial|opera[cç][oõ]es)"
)


titulo = df['name'].str.lower()
eh_ti = titulo.str.contains(INCLUIR, regex=True) & ~titulo.str.contains(EXCLUIR, regex=True)
df = df[eh_ti].copy()
print("Vagas de TI (antes de remover repetidas):", len(df))





