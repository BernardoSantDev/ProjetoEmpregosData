
import re
import requests
import pandas as pd
import unicodedata

from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urljoin, urlparse


BASE = "https://www.superestagios.com.br"

URL_CATALOGO = BASE + "/vagas/"

HEADERS = {
    "User-Agent": "ObservatorioEstagios/1.0 (projeto academico)"
}


def normalizar_texto(texto):
    if not isinstance(texto, str):
        return ""

    texto = texto.lower().strip()

    texto = unicodedata.normalize("NFKD", texto)

    texto = "".join(
        letra for letra in texto
        if not unicodedata.combining(letra)
    )

    return " ".join(texto.split())



def encontrar_url_curso(area):
    print(f"\nProcurando a área: {area}")

    resposta = requests.get(
        URL_CATALOGO,
        headers=HEADERS,
        timeout=20
    )

    resposta.raise_for_status()

    soup = BeautifulSoup(
        resposta.text,
        "html.parser"
    )

    apelidos = {
        "ti": "tecnologia da informacao",
        "t.i.": "tecnologia da informacao",
        "adm": "administracao",
        "ads": "analise e desenvolvimento de sistemas"
    }

    area_normalizada = normalizar_texto(area)

    area_busca = apelidos.get(
        area_normalizada,
        area_normalizada
    )

    links = soup.select("a[href]")

    for link in links:
        nome = normalizar_texto(
            link.get_text(" ", strip=True)
        )

        nome = re.sub(r"\s*\d+\s*$", "", nome)

        url = urljoin(BASE, link["href"])

        partes_url = urlparse(url)

        caminho = partes_url.path

        if partes_url.netloc != urlparse(BASE).netloc:
            continue

        if not re.fullmatch(
            r"/vagas/[a-z0-9-]+/?",
            caminho
        ):
            continue

        if nome == area_busca:
            print(f"Área encontrada: {area}")
            print(f"URL: {url}")

            return url

    print(f"Área não encontrada no catálogo: {area}")

    return None



def extrair_campo(texto, inicio, fim):
    padrao = (
        rf"{re.escape(inicio)}\s*:\s*"
        rf"(.*?)\s*{re.escape(fim)}\s*:"
    )

    resultado = re.search(
        padrao,
        texto,
        flags=re.I | re.S
    )

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


def listar_vagas(url_lista):
    resposta = requests.get(
        url_lista,
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

        partes_url = urlparse(url)

        if partes_url.netloc != urlparse(BASE).netloc:
            continue

        resultado = re.fullmatch(
            r"/vaga/(\d+)/?",
            partes_url.path
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

    partes_url = urlparse(url)

    if partes_url.netloc != urlparse(BASE).netloc:
        raise ValueError("Link fora do domínio permitido.")

    if not re.fullmatch(
        r"/vaga/\d+/?",
        partes_url.path
    ):
        raise ValueError("Link de vaga inválido.")

    resposta = requests.get(
        url,
        headers=HEADERS,
        timeout=20
    )

    resposta.raise_for_status()

    soup = BeautifulSoup(
        resposta.text,
        "html.parser"
    )

    texto = soup.get_text(" ", strip=True)

    vaga = {
        "id": extrair_campo(
            texto, "Número da vaga", "Empresa"
        ),

        "empresa": extrair_campo(
            texto, "Empresa", "Nível"
        ),

        "cursos": extrair_campo(
            texto, "Cursos", "Valor da bolsa"
        ),

        "bolsa": extrair_campo(
            texto, "Valor da bolsa",
            "Valor do auxilio transporte"
        ),

        "cidade": extrair_campo(
            texto, "Cidade", "Estado"
        ),

        "estado": extrair_campo(
            texto, "Estado", "Requisito"
        ),

        "atividades": extrair_campo(
            texto,
            "Atividades a serem desenvolvidas",
            "Benefícios"
        ),

        "url": url
    }

    return vaga


def salvar_vaga(vaga):
    if not vaga.get("id"):
        print("Vaga sem ID. Registro não salvo.")
        return None

    pasta = Path("dados")
    pasta.mkdir(exist_ok=True)

    arquivo = pasta / "vagas_superestagios.csv"

    vaga = vaga.copy()

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

    return df


def main():

    area = input(
        "\nQual área de estágio deseja pesquisar? "
    ).strip()

    if not area:
        print("Informe uma área válida.")
        return

    try:
        url_curso = encontrar_url_curso(area)

        if not url_curso:
            return

        df_links = listar_vagas(url_curso)

        if df_links.empty:
            print("Nenhuma vaga encontrada.")
            return

        print("\nPrimeiras vagas encontradas:")

        print(
            df_links.head(10).to_string(index=False)
        )

        primeira = df_links.iloc[0]

        print("\nTestando a primeira vaga...")

        vaga = coletar_detalhes(primeira["url"])

        vaga["titulo"] = primeira["titulo"]
        vaga["area_pesquisada"] = area

        salvar_vaga(vaga)

        print("\nPesquisa de teste finalizada!")

    except requests.RequestException as erro:
        print(f"\nErro de conexão: {erro}")

    except ValueError as erro:
        print(f"\nErro nos dados: {erro}")

    except (OSError, pd.errors.ParserError) as erro:
        print(f"\nErro ao acessar o CSV: {erro}")


if __name__ == "__main__":
    main()
