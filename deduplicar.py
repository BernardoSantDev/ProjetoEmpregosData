
from pathlib import Path
import pandas as pd
import re
import unicodedata
from itertools import combinations
from difflib import SequenceMatcher


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



def comparar_entre_plataformas():
    arquivo = PASTA_DADOS / "vagas_padronizadas.csv"

    df = pd.read_csv(
        arquivo,
        encoding="utf-8-sig",
        dtype={"id_unico": "string"}
    )

    if df.empty:
        print("Nenhuma vaga para comparar.")
        return pd.DataFrame()

    print("\nDUPLICATAS ENTRE PLATAFORMAS")
    print("Fontes encontradas:", ", ".join(
        sorted(df["fonte"].dropna().unique())
    ))

    if df["fonte"].nunique() < 2:
        print("Comparação não realizada: apenas uma fonte.")
        return pd.DataFrame()

    campos = ["titulo", "empresa", "cidade", "estado"]

    for campo in campos:
        df[f"chave_{campo}"] = df[campo].map(
            normalizar_texto
        )

    empresas_genericas = {
        "",
        "confidencial",
        "empresa confidencial",
        "nao informado",
        "sigilosa"
    }

    validas = (
        ~df["chave_empresa"].isin(empresas_genericas)
        & df["chave_titulo"].ne("")
        & df["chave_cidade"].ne("")
        & df["chave_estado"].ne("")
    )

    chaves = [f"chave_{campo}" for campo in campos]
    pares = []

    for _, grupo in df.loc[validas].groupby(
        chaves, sort=False
    ):
        if grupo["fonte"].nunique() < 2:
            continue

        for vaga1, vaga2 in combinations(
            grupo.to_dict("records"), 2
        ):
            if vaga1["fonte"] == vaga2["fonte"]:
                continue

            pares.append({
                "id_1": vaga1["id_unico"],
                "fonte_1": vaga1["fonte"],
                "id_2": vaga2["id_unico"],
                "fonte_2": vaga2["fonte"],
                "titulo": vaga1["titulo"],
                "empresa": vaga1["empresa"],
                "cidade": vaga1["cidade"],
                "estado": vaga1["estado"],
                "url_1": vaga1["url"],
                "url_2": vaga2["url"]
            })

    candidatos = pd.DataFrame(pares)

    print("Pares candidatos:", len(candidatos))

    if not candidatos.empty:
        print(
            candidatos[
                ["id_1", "id_2", "titulo",
                 "empresa", "cidade", "estado"]
            ].to_string(index=False)
        )

    return candidatos


def comparar_similaridade():
    arquivo = PASTA_DADOS / "vagas_padronizadas.csv"

    df = pd.read_csv(
        arquivo,
        encoding="utf-8-sig",
        dtype={"id_unico": "string"}
    )

    campos = ["titulo", "cidade", "estado"]

    for campo in campos:
        df[f"chave_{campo}"] = df[campo].map(
            normalizar_texto
        )

    pares = []

    grupos = df.groupby([
        "chave_cidade",
        "chave_estado"
    ])

    for _, grupo in grupos:
        vagas = grupo.to_dict("records")

        for vaga1, vaga2 in combinations(vagas, 2):
            if vaga1["fonte"] == vaga2["fonte"]:
                continue

            similaridade = SequenceMatcher(
                None,
                vaga1["chave_titulo"],
                vaga2["chave_titulo"]
            ).ratio()

            if similaridade >= 0.70:
                pares.append({
                    "id_1": vaga1["id_unico"],
                    "id_2": vaga2["id_unico"],
                    "fonte_1": vaga1["fonte"],
                    "fonte_2": vaga2["fonte"],
                    "cidade": vaga1["cidade"],
                    "similaridade": round(
                        similaridade * 100, 1
                    )
                })

    candidatos = pd.DataFrame(pares)

    print("\nANÁLISE DE SIMILARIDADE")
    print(f"Pares candidatos: {len(candidatos)}")

    if not candidatos.empty:
        candidatos = candidatos.sort_values(
            "similaridade",
            ascending=False
        )

        print(candidatos.to_string(index=False))

    return candidatos



def avaliar_candidatos(candidatos):
    if candidatos.empty:
        print("\nNenhum candidato para avaliar.")
        return pd.DataFrame()

    arquivo = PASTA_DADOS / "vagas_padronizadas.csv"

    df = pd.read_csv(
        arquivo,
        encoding="utf-8-sig",
        dtype={"id_unico": "string"}
    )

    df = df.set_index("id_unico")

    empresas_genericas = {
        "",
        "confidencial",
        "empresa confidencial",
        "pagina de carreira",
        "nao informado",
        "sigilosa"
    }

    resultados = []

    for _, par in candidatos.iterrows():
        vaga1 = df.loc[par["id_1"]]
        vaga2 = df.loc[par["id_2"]]

        empresa1 = normalizar_texto(vaga1["empresa"])
        empresa2 = normalizar_texto(vaga2["empresa"])

        if (
            empresa1 in empresas_genericas
            or empresa2 in empresas_genericas
        ):
            situacao = "Empresa não confirmada"

        elif empresa1 != empresa2:
            situacao = "Empresas diferentes"

        else:
            situacao = "Empresa igual"

        resultados.append({
            "id_1": par["id_1"],
            "id_2": par["id_2"],
            "fonte_1": vaga1["fonte"],
            "fonte_2": vaga2["fonte"],
            "titulo_1": vaga1["titulo"],
            "titulo_2": vaga2["titulo"],
            "empresa_1": vaga1["empresa"],
            "empresa_2": vaga2["empresa"],
            "cidade": vaga1["cidade"],
            "estado": vaga1["estado"],
            "similaridade": par["similaridade"],
            "bolsa_1": vaga1["salario_texto"],
            "bolsa_2": vaga2["salario_texto"],
            "situacao": situacao,
            "url_1": vaga1["url"],
            "url_2": vaga2["url"]
        })

    revisao = pd.DataFrame(resultados)

    arquivo_saida = (
        PASTA_DADOS / "duplicatas_para_revisao.csv"
    )

    revisao.to_csv(
        arquivo_saida,
        index=False,
        encoding="utf-8-sig"
    )

    print("\nAVALIAÇÃO DOS CANDIDATOS")
    print(f"Pares analisados: {len(revisao)}")

    print(revisao["situacao"].value_counts())

    print(f"\nRelatório salvo: {arquivo_saida}")

    return revisao


if __name__ == "__main__":
    identificar_duplicatas()
    comparar_entre_plataformas()
    candidatos = comparar_similaridade()
    avaliar_candidatos(candidatos)
