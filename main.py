from pathlib import Path
from coletor import coletar_gupy
from importador_infojobs import importar_infojobs
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
    termos = [
        f"estágio {area}",
        f"estágio em {area}",
        f"estagiário {area}",
        f"estagiária {area}"
    ]

    return termos


def escolher_fonte():
    print("\nEscolha a fonte de dados:")
    print("1 - Gupy")
    print("2 - InfoJobs (histórico)")
    print("3 - Super Estágios")
    print("4 - Todas as fontes")

    while True:
        opcao = input("\nDigite uma opção: ").strip()

        if opcao in ("1", "2", "3", "4"):
            return opcao

        print("Opção inválida!")


def pesquisar_gupy(area):
    print("\nIniciando pesquisa na Gupy...")

    termos = gerar_termos(area)

    df = coletar_gupy(termos)

    print(f"Gupy: {len(df)} vagas coletadas.")

    return df


def pesquisar_infojobs(area):
    print("\nImportando dados históricos do InfoJobs...")

    df = importar_infojobs(area)

    print(f"InfoJobs: {len(df)} registros históricos.")

    return df

def pesquisar_superestagios(area):
    print("\nIniciando pesquisa no Super Estágios...")

    url_curso = encontrar_url_curso(area)

    if not url_curso:
        print("Curso não encontrado no catálogo.")
        return None

    df_links = listar_vagas(url_curso)

    print(f"Anúncios na listagem: {len(df_links)}")

    if df_links.empty:
        print("Nenhum anúncio encontrado.")
        return None

    print("\nPrimeiros anúncios encontrados:")

    print(
        df_links.head(10).to_string(index=False)
    )

    primeira = df_links.iloc[0]

    print("\nConsultando uma vaga para teste...")

    vaga = coletar_detalhes(primeira["url"])

    vaga["titulo"] = primeira["titulo"]
    vaga["area_pesquisada"] = area

    df = salvar_vaga(vaga)

    return df


def limpar_resultados():
    pasta = Path("dados")

    arquivos = [
        "vagas_gupy.csv",
        "vagas_superestagios.csv",
        "links_superestagios.csv",
        "vagas_infojobs_filtradas.csv"
    ]

    for nome in arquivos:
        caminho = pasta / nome

        if caminho.is_file():
            caminho.unlink()

    print("\nResultados da pesquisa anterior removidos.")



def main():

    while True:
        area = escolher_area()
        opcao = escolher_fonte()

        limpar_resultados()

        print(f"\nÁrea selecionada: {area}")

        if opcao in ("1", "4"):
            try:
                pesquisar_gupy(area)
            except Exception as erro:
                print(f"Erro na Gupy: {erro}")

        if opcao in ("2", "4"):
            try:
                pesquisar_infojobs(area)
            except Exception as erro:
                print(f"Erro no InfoJobs: {erro}")

        if opcao in ("3", "4"):
            try:
                pesquisar_superestagios(area)
            except Exception as erro:
                print(f"Erro no Super Estágios: {erro}")

        print("\nPesquisa finalizada!")

        continuar = input(
            "\nDeseja pesquisar outra área? (s/n): "
        ).strip().lower()

        if continuar not in ("s", "sim"):
            print("\nPrograma encerrado!")
            break


if __name__ == "__main__":
    main()
