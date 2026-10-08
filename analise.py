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








