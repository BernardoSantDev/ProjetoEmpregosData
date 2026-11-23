from coletor import coletar_gupy
from importador_infojobs import importar_infojobs

def escolher_area():
    print("===================================")
    print("     OBSERVATÓRIO DE ESTÁGIOS      ")
    print("===================================")

    while True:
        area = input("\nQual área de estágio deseja pesquisar? ").strip()

        if area:
            return area

        print("Erro: digite uma área válida!")


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
    print("1 - Gupy (coleta atual)")
    print("2 - InfoJobs (dados históricos)")
    print("3 - Ambas")

    while True:
        opcao = input("\nDigite uma opção: ").strip()

        if opcao in ("1", "2", "3"):
            return opcao

        print("Opção inválida!")


def main():
    area = escolher_area()
    opcao = escolher_fonte()

    print(f"\nÁrea selecionada: {area}")

    if opcao in ("1", "3"):
        termos = gerar_termos(area)

        try:
            df_gupy = coletar_gupy(termos)
            print(f"Gupy: {len(df_gupy)} vagas.")

        except Exception as erro:
            print(f"Erro na Gupy: {erro}")

    if opcao in ("2", "3"):
        try:
            df_infojobs = importar_infojobs(area)
            print(f"InfoJobs: {len(df_infojobs)} registros históricos.")

        except Exception as erro:
            print(f"Erro ao importar InfoJobs: {erro}")


if __name__ == "__main__":
    main()
