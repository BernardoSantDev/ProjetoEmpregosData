import pandas as pd

from bs4 import BeautifulSoup

def limpar_texto(texto):
    if not isinstance(texto, str):
        return ""
    puro = BeautifulSoup(texto, "html.parser").get_text(" ")
    return " ".join(puro.split())

def preparar_gupy():
    gupy = pd.read_csv("vagas_brutas.csv")
    gupy["descricao_limpa"] = gupy["description"].apply(limpar_texto)
    return gupy

def preparar_infojobs():
    return pd.DataFrame()

if __name__ == "__main__":
    gupy = preparar_gupy()
    infojobs = preparar_infojobs()
    todas = pd.concat([gupy, infojobs], ignore_index=True)
    print("TOTAL:", len(todas))







