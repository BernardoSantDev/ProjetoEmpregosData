import re
import requests
import pandas as pd

from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urljoin, urlparse

BASE = "https://www.superestagios.com.br"
URL_LISTA = "https://www.superestagios.com.br/vagas/tecnologia-da-informacao"
LINK = "/vaga/329068"

HEADERS = {
    "User-Agent": "ObservatorioEstagios/1.0 (projeto academico)"
}


def extrair_campo(texto, inicio, fim):
    padrao = (
        rf"{re.escape(inicio)}\s*:\s*"
        rf"(.*?)\s*{re.escape(fim)}\s*:"
    )

    resultado = re.search(padrao, texto, flags=re.I | re.S)

    if resultado:
        return resultado.group(1).strip(" |")

    return None


def converter_bolsa(texto):
    if not texto:
        return None

    padrao = r"R\$\s*([\d.]+,\d{2})"

    resultado = re.search(padrao, texto)

    if not resultado:
        return None

    valor = resultado.group(1)

    valor = valor.replace(".", "").replace(",", ".")

    return float(valor)


def listar_vagas():
    resposta = requests.get(
        URL_LISTA,
        headers=HEADERS,
        timeout=20
    )

    resposta.raise_for_status()

    soup = BeautifulSoup(
        resposta.text,
        "html.parser"
    )

    titulos = soup.select("h3 a[href]")

    vagas = {}

    for titulo in titulos:
        nome = titulo.get_text(" ", strip=True)
        href = titulo.get("href", "")

        url = urljoin(BASE, href)

        caminho = urlparse(url).path

        resultado = re.fullmatch(
            r"/vaga/(\d+)/?",
            caminho
        )

        if not resultado:
            continue

        id_vaga = resultado.group(1)

        if id_vaga in vagas:
            continue

        vagas[id_vaga] = {
            "id": id_vaga,
            "titulo": nome,
            "url": url
        }

    df = pd.DataFrame(
        vagas.values(),
        columns=["id", "titulo", "url"]
    )

    pasta = Path("dados")
    pasta.mkdir(exist_ok=True)

    arquivo = pasta / "links_superestagios.csv"

    df.to_csv(
        arquivo,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"\nVagas distintas encontradas: {len(df)}")
    print(f"Links salvos em: {arquivo}")

    return df


def coletar_detalhes(link):
    url = urljoin(BASE, link)

    resposta = requests.get(
        url,
        headers=HEADERS,
        timeout=20
    )

    resposta.raise_for_status()

    soup = BeautifulSoup(resposta.text, "html.parser")

    texto = soup.get_text(" ", strip=True)

    vaga = {
        "id": extrair_campo(texto, "Número da vaga", "Empresa"),
        "empresa": extrair_campo(texto, "Empresa", "Nível"),
        "cursos": extrair_campo(texto, "Cursos", "Valor da bolsa"),
        "bolsa": extrair_campo(texto, "Valor da bolsa", "Valor do auxilio transporte"),
        "cidade": extrair_campo(texto, "Cidade", "Estado"),
        "estado": extrair_campo(texto, "Estado", "Requisito"),
        "atividades": extrair_campo(texto, "Atividades a serem desenvolvidas", "Benefícios"),
        "url": url
    }

    print("\nDADOS DA VAGA:")

    for campo, valor in vaga.items():
        print(f"{campo}: {valor}")

    return vaga


def salvar_vaga(vaga):
    pasta = Path("dados")
    pasta.mkdir(exist_ok=True)

    arquivo = pasta / "vagas_superestagios.csv"

    if not vaga.get("id"):
        print("Vaga sem ID. Registro não salvo.")
        return

    vaga["id"] = str(vaga["id"]).strip()

    vaga["bolsa_valor"] = converter_bolsa(
        vaga.get("bolsa")
    )

    vaga["fonte"] = "Super Estágios"

    df_novo = pd.DataFrame([vaga])

    if arquivo.exists():
        df_antigo = pd.read_csv(
            arquivo,
            dtype={"id": str}
        )

        df = pd.concat(
            [df_antigo, df_novo],
            ignore_index=True
        )

    else:
        df = df_novo

    df = df.drop_duplicates(
        subset="id",
        keep="last"
    )

    df.to_csv(
        arquivo,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"\nArquivo salvo em: {arquivo}")
    print(f"Total de vagas únicas: {len(df)}")

    return df




if __name__ == "__main__":
    try:
        df_links = listar_vagas()

        print("\nPrimeiras vagas encontradas:")

        print(df_links.head(10).to_string(index=False))

        if not df_links.empty:
            link = df_links.iloc[0]["url"]

            print("\nTestando a primeira vaga...")

            vaga = coletar_detalhes(link)

            salvar_vaga(vaga)

    except requests.RequestException as erro:
        print(f"Erro de conexão: {erro}")

