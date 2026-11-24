from pathlib import Path
import pandas as pd
import re
from bs4 import BeautifulSoup
import unicodedata

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
        "type": "tipo_vaga",
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
    "tipo_vaga",
    "classificacao_estagio",
    "compatibilidade_area",
    "motivo_compatibilidade",
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
    "escolaridade",
    "experiencia",
    "termo_busca",
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
        "escolaridade",
        "experiencia",
        "termo_busca",
        "url"
    ]

    for coluna in colunas_texto:
        df[coluna] = df[coluna].map(tratar_ausente)

    campos_essenciais = [
        "id_fonte",
        "titulo",
        "url"
    ]

    df["revisao_necessaria"] = (
        df[campos_essenciais].isna().any(axis=1)
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

    return df


def classificar_estagio(linha):
    tipo = linha["tipo_vaga"]
    titulo = linha["titulo"]

    if pd.notna(tipo):
        if str(tipo).strip() == "vacancy_type_internship":
            return "Estágio identificado"

    if pd.isna(titulo):
        return "Revisar"

    titulo = str(titulo).casefold()

    titulo = unicodedata.normalize(
        "NFKD",
        titulo
    )

    titulo = "".join(
        letra for letra in titulo
        if not unicodedata.combining(letra)
    )

    if re.search(
        r"\b(?:supervisor|supervisora|coordenador|coordenadora|professor|professora|preceptor|preceptora)\s+(?:de\s+)?estagio\b",
        titulo
    ):
        return "Revisar"


    padrao = r"\b(?:estagio|estagiari[oa]s?)\b"

    if re.search(padrao, titulo):
        return "Estágio identificado"

    return "Revisar"


def normalizar_busca(valor):
    if pd.isna(valor):
        return ""

    texto = str(valor).casefold()

    texto = unicodedata.normalize(
        "NFKD", texto
    )

    texto = "".join(
        letra for letra in texto
        if not unicodedata.combining(letra)
    )

    texto = re.sub(r"[^\w]+", " ", texto)

    return " ".join(texto.split())


def contem_area(texto, termos):
    texto = normalizar_busca(texto)

    for termo in termos:
        termo = normalizar_busca(termo)

        if not termo:
            continue

        padrao = r"\b" + re.escape(termo) + r"\b"

        if re.search(padrao, texto):
            return True

    return False


def classificar_compatibilidade(linha, area):
    sinonimos = {
        "ti": [
            "ti",
            "t i",
            "tecnologia da informacao",
            "informatica"
        ],
        "dados": [
            "dados",
            "ciencia de dados",
            "analise de dados",
            "data science",
            "data analytics"
        ],
        "administracao": [
            "administracao",
            "administrativo"
        ]
    }

    area_normalizada = normalizar_busca(area)

    termos = sinonimos.get(
        area_normalizada,
        [area_normalizada]
    )

    titulo = linha["titulo"]
    cursos = linha["cursos"]
    descricao = linha["descricao"]

    if contem_area(titulo, termos):
        return (
            "Exata",
            "Área identificada no título"
        )

    if contem_area(cursos, termos):
        return (
            "Relacionada",
            "Área incluída nos cursos aceitos"
        )

    if contem_area(descricao, termos):
        return (
            "Revisar",
            "Área mencionada apenas na descrição"
        )

    return (
        "Revisar",
        "Compatibilidade não confirmada"
    )


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
        "salario_texto",
        "escolaridade",
        "experiencia",
        "termo_busca"
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


    df_final["modalidade"] = df_final["modalidade"].map(
        normalizar_modalidade
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


    df_final = verificar_qualidade(df_final)
    df_final = padronizar_datas(df_final)


    df_final["classificacao_estagio"] = df_final.apply(
        classificar_estagio,
        axis=1
    )

    resultados_area = df_final.apply(
        lambda linha: classificar_compatibilidade(
            linha, area
        ),
        axis=1
    )

    df_final["compatibilidade_area"] = (
        resultados_area.str[0]
    )

    df_final["motivo_compatibilidade"] = (
        resultados_area.str[1]
    )

    df_final["revisao_necessaria"] = (
        df_final["revisao_necessaria"]
        | df_final["classificacao_estagio"].eq("Revisar")
        | df_final["compatibilidade_area"].eq("Revisar")
    )

    arquivo_saida = PASTA_DADOS / "vagas_padronizadas.csv"

    df_final.to_csv(
        arquivo_saida,
        index=False,
        encoding="utf-8-sig"
    )

    print("\nCONSOLIDAÇÃO FINALIZADA")
    print(f"Total de registros: {len(df_final)}")
    print(f"IDs duplicados: {df_final['id_unico'].dropna().duplicated().sum()}")
    print(f"Vagas para revisão: {int(df_final['revisao_necessaria'].sum())}")
    print(f"Arquivo salvo em: {arquivo_saida}")

    return df_final


if __name__ == "__main__":
    area = input("Área pesquisada: ").strip()

    if area:
        consolidar_pesquisa(area)
    else:
        print("Informe uma área válida.")
