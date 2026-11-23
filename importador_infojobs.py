
import re
import unicodedata
from pathlib import Path

import pandas as pd




def importar_infojobs(area, arquivo="vagas_infojobs.csv"):
    caminho = Path(arquivo)

    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {arquivo}"
        )

    df = pd.read_csv(caminho, dtype={"id": str})

    colunas = {"id", "name", "url"}

    if not colunas.issubset(df.columns):
        raise ValueError("O CSV não possui as colunas necessárias.")

    titulos = df["name"].apply(normalizar_texto)

    area_normalizada = normalizar_texto(area)

    padrao_area = r"\b" + re.escape(area_normalizada) + r"\b"

    padrao_estagio = r"\b(?:estagio|estagiari[oa]s?)\b"

    filtro_area = titulos.str.contains(
        padrao_area, regex=True, na=False
    )

    filtro_estagio = titulos.str.contains(
        padrao_estagio, regex=True, na=False
    )

    df = df[filtro_area & filtro_estagio].copy()

    df = df.drop_duplicates(subset="id")

    df["fonte"] = "InfoJobs"
    df["area_pesquisada"] = area
    df["situacao"] = "Histórico - não verificada"

    pasta = Path("dados")
    pasta.mkdir(exist_ok=True)

    destino = pasta / "vagas_infojobs_filtradas.csv"

    df.to_csv(destino, index=False, encoding="utf-8-sig")

    print(f"\nInfoJobs: {len(df)} vagas encontradas no histórico.")
    print(f"Arquivo salvo em: {destino}")

    return df
