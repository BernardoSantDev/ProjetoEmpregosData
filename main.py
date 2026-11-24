
from pathlib import Path
import time
import requests
from coletor import coletar_gupy
from coletor_infojobs import coletar_infojobs
from padronizar import consolidar_pesquisa

from coletor_superestagios import (
    encontrar_url_curso,
    listar_vagas,
    coletar_detalhes,
    salvar_vaga
)


def escolher_area():
    print("===================================")
    print("     OBSERVATÓRIO DE ESTÁGIOS      ")
    print("===================================")

    while True:
        area = input(
            "\nQual área de estágio deseja pesquisar? "
        ).strip()

        if area:
            return area

        print("Digite uma área válida!")


def gerar_termos(area):
    return [
        f"estágio {area}",
        f"estágio em {area}",
        f"estagiário {area}",
        f"estagiária {area}"
    ]


def escolher_fonte():
    print("\nEscolha a fonte de dados:")
    print("1 - Gupy")
    print("2 - InfoJobs")
    print("3 - Super Estágios")
    print("4 - Todas as fontes")

    while True:
        opcao = input("\nDigite uma opção: ").strip()

        if opcao in ("1", "2", "3", "4"):
            return opcao

        print("Opção inválida!")


def pesquisar_gupy(area):
    print("\nIniciando coleta na Gupy...")

    termos = gerar_termos(area)

    df = coletar_gupy(termos)

    print(f"Gupy: {len(df)} vagas coletadas.")

    return df


def pesquisar_infojobs(area):
    print("\nIniciando coleta no InfoJobs...")

    df = coletar_infojobs(
        area,
        max_paginas=2
    )

    print(f"InfoJobs: {len(df)} vagas coletadas.")

    return df



def pesquisar_superestagios(area):
    print("\nIniciando pesquisa no Super Estágios...")

    url_curso = encontrar_url_curso(area)

    if not url_curso:
        print("Curso não encontrado no catálogo.")
        return None

    df_links = listar_vagas(url_curso)

    total = len(df_links)

    print(f"Anúncios encontrados: {total}")

    if df_links.empty:
        print("Nenhum anúncio encontrado.")
        return None

    df = None

    for indice, anuncio in df_links.iterrows():
        numero = indice + 1

        try:
            vaga = coletar_detalhes(anuncio["url"])

            vaga["titulo"] = anuncio["titulo"]
            vaga["area_pesquisada"] = area

            resultado = salvar_vaga(vaga)

            if resultado is not None:
                df = resultado

                print(
                    f"[{numero}/{total}] "
                    f"Vaga {anuncio['id']} salva."
                )

        except requests.HTTPError as erro:
            status = (
                erro.response.status_code
                if erro.response is not None
                else None
            )

            print(
                f"Erro HTTP na vaga {anuncio['id']}: {status}"
            )

            if status in (403, 429):
                print("Acesso limitado. Coleta interrompida.")
                break

        except (requests.RequestException, ValueError, OSError) as erro:
            print(f"Erro na vaga {anuncio['id']}: {erro}")

        if numero < total:
            time.sleep(2)

    return df




def limpar_resultados():
    pasta = Path(__file__).resolve().parent / "dados"

    arquivos = [
        "vagas_gupy.csv",
        "vagas_infojobs_atual.csv",
        "vagas_infojobs_filtradas.csv",
        "vagas_superestagios.csv",
        "links_superestagios.csv",
        "vagas_padronizadas.csv"
    ]

    for nome in arquivos:
        caminho = pasta / nome

        if caminho.is_file():
            caminho.unlink()

    print("\nResultados da pesquisa anterior removidos.")


def executar_pesquisa(area, opcao):
    fontes = {
        "1": [("Gupy", pesquisar_gupy)],
        "2": [("InfoJobs", pesquisar_infojobs)],
        "3": [("Super Estágios", pesquisar_superestagios)],
        "4": [
            ("Gupy", pesquisar_gupy),
            ("InfoJobs", pesquisar_infojobs),
            ("Super Estágios", pesquisar_superestagios)
        ]
    }

    resultados = {}

    for nome, funcao in fontes[opcao]:
        try:
            df = funcao(area)

            if df is not None:
                resultados[nome] = len(df)
            else:
                resultados[nome] = 0

        except Exception as erro:
            print(f"\nErro na fonte {nome}: {erro}")
            resultados[nome] = None

    return resultados


def mostrar_resumo(area, resultados):
    print("\n===================================")
    print("         RESUMO DA PESQUISA        ")
    print("===================================")

    print(f"Área pesquisada: {area}")

    for fonte, quantidade in resultados.items():
        if quantidade is None:
            print(f"{fonte}: Erro na coleta")

        elif fonte == "Super Estágios":
            print(
                f"{fonte}: {quantidade} registros "
                "no CSV de detalhes"
            )

        else:
            print(f"{fonte}: {quantidade} vagas")

    print("\nPesquisa finalizada!")
    print("Os resultados estão na pasta dados.")


def main():
    while True:
        area = escolher_area()

        opcao = escolher_fonte()

        limpar_resultados()

        print(f"\nÁrea selecionada: {area}")

        
        resultados = executar_pesquisa(area, opcao)

        mostrar_resumo(area, resultados)

        print("\nIniciando padronização...")

        try:
            df_padronizado = consolidar_pesquisa(area)

            if df_padronizado is None:
                print("Nenhum dado disponível para padronizar.")
            else:
                print(
                    f"Padronização concluída: "
                    f"{len(df_padronizado)} registros."
                )

        except Exception as erro:
            print(f"Erro durante a padronização: {erro}")


        while True:
            continuar = input(
                "\nDeseja pesquisar outra área? (s/n): "
            ).strip().lower()

            if continuar in ("s", "sim", "n", "nao", "não"):
                break

            print("Digite s ou n.")

        if continuar in ("n", "nao", "não"):
            print("\nPrograma encerrado!")
            break


if __name__ == "__main__":
    main()
