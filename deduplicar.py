
from pathlib import Path
import pandas as pd
import re
import unicodedata


PASTA_DADOS = Path(__file__).resolve().parent / "dados"


def normalizar_texto(valor):
    if pd.isna(valor):
        return ""

    texto = unicodedata.normalize(
        "NFKD", str(valor).casefold()
    )

    texto = "".join(
        letra for letra in texto
        if not unicodedata.combining(letra)
    )

    texto = re.sub(r"[^\w]+", " ", texto)

    return " ".join(texto.split())


def identificar_duplicatas():
    arquivo = PASTA_DADOS / "vagas_padronizadas.csv"

    df = pd.read_csv(
        arquivo,
        encoding="utf-8-sig",
        dtype={"id_fonte": "string", "id_unico": "string"}
    )

    if df.empty:
        print("Nenhuma vaga disponível.")
        return

    colunas = ["titulo", "cidade", "estado", "descricao"]

    for coluna in colunas:
        df[f"{coluna}_normalizado"] = df[coluna].map(
            normalizar_texto
        )

    campos = [
        f"{coluna}_normalizado"
        for coluna in colunas
    ]

    mascara = (
        df["descricao_normalizado"].ne("")
        & df.duplicated(subset=campos, keep=False)
    )

    candidatos = df.loc[mascara].sort_values(campos)

    print("\nANÁLISE DE DUPLICATAS")
    print(f"Total de registros: {len(df)}")
    print(f"Registros semelhantes: {len(candidatos)}")

    if not candidatos.empty:
        print(
            candidatos[
                ["id_unico", "titulo", "cidade", "estado"]
            ].to_string(index=False)
        )

    return candidatos


if __name__ == "__main__":
    identificar_duplicatas()
