from pathlib import Path
import pandas as pd
import re
from bs4 import BeautifulSoup


PASTA_DADOS = Path(__file__).resolve().parent / "dados"

ARQUIVOS = {
    "Gupy": "vagas_gupy.csv",
    "InfoJobs": "vagas_infojobs_atual.csv",
    "Super Estágios": "vagas_superestagios.csv"
}


MAPEAMENTOS = {
    "Gupy": {
        "id": "id_fonte",
        "name": "titulo",
        "careerPageName": "empresa",
        "city": "cidade",
        "state": "estado",
        "description": "descricao",
        "workplaceType": "modalidade",
        "publishedDate": "data_publicacao",
        "applicationDeadline": "prazo_inscricao",
        "jobUrl": "url"
    },

    "InfoJobs": {
        "id": "id_fonte",
        "name": "titulo",
        "careerPageName": "empresa",
        "location": "localizacao",
        "workplaceType": "modalidade",
        "description": "descricao"
    },

    "Super Estágios": {
        "id": "id_fonte",
        "atividades": "descricao",
        "bolsa": "salario_texto"
    }
}


COLUNAS_PADRAO = [
    "fonte",
    "id_fonte",
    "id_unico",
    "titulo",
    "empresa",
    "cidade",
    "estado",
    "localizacao",
    "modalidade",
    "descricao",
    "salario_texto",
    "bolsa_valor",
    "bolsa_min",
    "bolsa_max",
    "data_publicacao",
    "prazo_inscricao",
    "cursos",
    "url",
    "area_pesquisada"
]


def limpar_texto(valor):
    if pd.isna(valor):
        return pd.NA

    texto = BeautifulSoup(
        str(valor),
        "html.parser"
    ).get_text(" ", strip=True)

    texto = re.sub(r"\s+", " ", texto).strip()

    if not texto:
        return pd.NA

    return texto



def normalizar_estado(valor):
    if pd.isna(valor):
        return pd.NA

    texto = str(valor).strip()

    estados = {
        "acre": "AC",
        "alagoas": "AL",
        "amapá": "AP",
        "amazonas": "AM",
        "bahia": "BA",
        "ceará": "CE",
        "distrito federal": "DF",
        "espírito santo": "ES",
        "goiás": "GO",
        "maranhão": "MA",
        "mato grosso": "MT",
        "mato grosso do sul": "MS",
        "minas gerais": "MG",
        "pará": "PA",
        "paraíba": "PB",
        "paraná": "PR",
        "pernambuco": "PE",
        "piauí": "PI",
        "rio de janeiro": "RJ",
        "rio grande do norte": "RN",
        "rio grande do sul": "RS",
        "rondônia": "RO",
        "roraima": "RR",
        "santa catarina": "SC",
        "são paulo": "SP",
        "sergipe": "SE",
        "tocantins": "TO"
    }

    siglas = set(estados.values())

    if texto.upper() in siglas:
        return texto.upper()

    return estados.get(texto.casefold(), pd.NA)



def normalizar_modalidade(valor):
    if pd.isna(valor):
        return pd.NA

    texto = str(valor).strip().casefold()

    modalidades = {
        "on-site": "Presencial",
        "onsite": "Presencial",
        "on site": "Presencial",
        "presencial": "Presencial",
        "in person": "Presencial",

        "remote": "Remoto",
        "remoto": "Remoto",
        "home office": "Remoto",
        "teletrabalho": "Remoto",

        "hybrid": "Híbrido",
        "híbrido": "Híbrido",
        "hibrido": "Híbrido"
    }

    return modalidades.get(texto, pd.NA)



def converter_reais(valor):
    valor = valor.replace(".", "")
    valor = valor.replace(",", ".")
    return float(valor)


def extrair_bolsa(texto):
    if pd.isna(texto):
        return (pd.NA, pd.NA, pd.NA)

    texto = str(texto).strip()

    padrao = r"R\$\s*([\d.]+,\d{2})"

    faixa = re.fullmatch(
        rf"{padrao}\s+a\s+{padrao}",
        texto,
        flags=re.IGNORECASE
    )

    if faixa:
        minimo = converter_reais(faixa.group(1))
        maximo = converter_reais(faixa.group(2))

        if minimo <= maximo:
            return (pd.NA, minimo, maximo)

        return (pd.NA, pd.NA, pd.NA)

    unico = re.fullmatch(
        padrao,
        texto,
        flags=re.IGNORECASE
    )

    if unico:
        valor = converter_reais(unico.group(1))
        return (valor, valor, valor)

    return (pd.NA, pd.NA, pd.NA)



def tratar_ausente(valor):
    if pd.isna(valor):
        return pd.NA

    if isinstance(valor, str):
        texto = valor.strip()

        valores_ausentes = {
            "",
            "nan",
            "none",
            "null",
            "n/a",
            "não informado",
            "nao informado"
        }

        if texto.casefold() in valores_ausentes:
            return pd.NA

        return texto

    return valor


def padronizar_datas(df):
    colunas_datas = [
        "data_publicacao",
        "prazo_inscricao"
    ]

    for coluna in colunas_datas:
        datas = pd.to_datetime(
            df[coluna],
            errors="coerce",
            utc=True
        )

        df[coluna] = (
            datas.dt.strftime("%Y-%m-%d")
            .astype("string")
        )

    print("\nPADRONIZAÇÃO DAS DATAS")

    print(
        "Datas de publicação:",
        df["data_publicacao"].notna().sum()
    )

    print(
        "Prazos de inscrição:",
        df["prazo_inscricao"].notna().sum()
    )

    print(
        "Sem data de publicação:",
        df["data_publicacao"].isna().sum()
    )

    return df


def verificar_qualidade(df):
    colunas_texto = [
        "id_fonte",
        "titulo",
        "empresa",
        "cidade",
        "estado",
        "localizacao",
        "modalidade",
        "descricao",
        "salario_texto",
        "cursos",
        "url"
    ]

    for coluna in colunas_texto:
        df[coluna] = df[coluna].map(tratar_ausente)

    colunas_verificacao = [
        "titulo",
        "empresa",
        "cidade",
        "estado",
        "modalidade",
        "descricao",
        "salario_texto",
        "bolsa_valor",
        "cursos",
        "url"
    ]

    faltantes = df[colunas_verificacao].isna().sum()

    relatorio = pd.DataFrame({
        "ausentes": faltantes,
        "percentual": (
            faltantes / len(df) * 100
        ).round(1) if len(df) else 0
    })

    print("\nRELATÓRIO DE QUALIDADE DOS DADOS")
    print(relatorio.to_string())

    campos_essenciais = [
        "id_fonte",
        "titulo",
        "url"
    ]

    df["revisao_necessaria"] = (
        df[campos_essenciais].isna().any(axis=1)
    )

    print(
        "\nRegistros para revisão:",
        df["revisao_necessaria"].sum()
    )

    return df


def criar_identificadores(df):
    prefixos = {
        "Gupy": "gupy",
        "InfoJobs": "infojobs",
        "Super Estágios": "superestagios"
    }

    ids = df["id_fonte"].astype("string").str.strip()

    ids = ids.mask(ids.eq(""))

    fontes = df["fonte"].map(prefixos).astype("string")

    df["id_unico"] = fontes + "_" + ids

    print("\nIDENTIFICADORES ÚNICOS")

    print(
        "IDs gerados:",
        df["id_unico"].notna().sum()
    )

    print(
        "IDs duplicados:",
        df["id_unico"].dropna().duplicated().sum()
    )

    print(
        "IDs ausentes:",
        df["id_unico"].isna().sum()
    )

    return df



def preparar_fontes(area):
    tabelas = {}

    for fonte, arquivo in ARQUIVOS.items():
        caminho = PASTA_DADOS / arquivo

        if not caminho.exists():
            print(f"Arquivo não encontrado: {arquivo}")
            continue

        df = pd.read_csv(
            caminho,
            encoding="utf-8-sig",
            dtype={"id": "string"}
        )

        df = df.rename(columns=MAPEAMENTOS[fonte])

        df["fonte"] = fonte
        df["area_pesquisada"] = area

        df = df.reindex(columns=COLUNAS_PADRAO)

        tabelas[fonte] = df

        print(f"\n{fonte}: {len(df)} vagas")
        print(df[["id_fonte", "titulo", "empresa"]].head(2))

    return tabelas



def consolidar_pesquisa(area):
    tabelas = preparar_fontes(area)

    if not tabelas:
        print("Nenhuma tabela disponível.")
        return None

    df_final = pd.concat(
        tabelas.values(),
        ignore_index=True
    )

    df_final = criar_identificadores(df_final)

    colunas_texto = [
        "titulo",
        "empresa",
        "descricao",
        "cursos",
        "localizacao",
        "cidade",
        "estado",
        "salario_texto"
    ]

    for coluna in colunas_texto:
        df_final[coluna] = df_final[coluna].map(limpar_texto)

    mascara_datas = (
        df_final["fonte"].eq("InfoJobs")
        & df_final["descricao"].fillna("").str.fullmatch(
            r"\d{1,2}\s+(?:jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez)",
            case=False
        )
    )

    print(
        f"Descrições inválidas do InfoJobs: {mascara_datas.sum()}"
    )

    df_final.loc[mascara_datas, "descricao"] = pd.NA


    mascara_infojobs = df_final["fonte"].eq("InfoJobs")

    localizacoes = df_final.loc[
        mascara_infojobs, "localizacao"
    ].str.extract(
        r"^\s*(.*?)\s+-\s+([A-Za-z]{2})\s*$"
    )

    df_final.loc[
        mascara_infojobs, "cidade"
    ] = localizacoes[0]

    df_final.loc[
        mascara_infojobs, "estado"
    ] = localizacoes[1]

    df_final["cidade"] = df_final["cidade"].map(
        limpar_texto
    )

    df_final["estado"] = df_final["estado"].map(
        normalizar_estado
    )

    print("\nPADRONIZAÇÃO DE LOCALIZAÇÃO")

    print(
        "Cidades identificadas:",
        df_final["cidade"].notna().sum()
    )

    print(
        "Estados identificados:",
        df_final["estado"].notna().sum()
    )

    print(
        df_final[
            ["fonte", "cidade", "estado"]
        ].groupby("fonte", sort=False).head(2).to_string(index=False)
    )



    df_final["modalidade"] = df_final["modalidade"].map(
        normalizar_modalidade
    )

    print("\nPADRONIZAÇÃO DAS MODALIDADES")

    print(
        df_final["modalidade"].value_counts(
            dropna=False
        )
    )



    colunas_bolsa = [
        "bolsa_valor",
        "bolsa_min",
        "bolsa_max"
    ]

    df_final[colunas_bolsa] = pd.DataFrame(
        df_final["salario_texto"].apply(
            extrair_bolsa
        ).tolist(),
        index=df_final.index,
        columns=colunas_bolsa
    )

    print("\nPADRONIZAÇÃO DAS BOLSAS")

    print(
        "Valores exatos:",
        df_final["bolsa_valor"].notna().sum()
    )

    faixas = (
        df_final["bolsa_min"].notna()
        & df_final["bolsa_valor"].isna()
    )

    print("Faixas de valores:", faixas.sum())

    print(
        "Sem valor numérico:",
        df_final["bolsa_min"].isna().sum()
    )


    df_final = verificar_qualidade(df_final)
    df_final = padronizar_datas(df_final)

    arquivo_saida = PASTA_DADOS / "vagas_padronizadas.csv"

    df_final.to_csv(
        arquivo_saida,
        index=False,
        encoding="utf-8-sig"
    )

    print("\nCONSOLIDAÇÃO FINALIZADA")
    print(f"Total de registros: {len(df_final)}")
    print(f"Arquivo salvo em: {arquivo_saida}")

    return df_final




if __name__ == "__main__":
    area = input("Área pesquisada: ").strip()

    if area:
        consolidar_pesquisa(area)
    else:
        print("Informe uma área válida.")
