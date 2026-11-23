from coletor import coletar_gupy

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





def main():
    area = escolher_area()
    termos = gerar_termos(area)

    print(f"\nÁrea selecionada: {area}")

    print("\nIniciando coleta na Gupy...")

    try:
        df = coletar_gupy(termos)

    except (ValueError, Exception) as erro:
        print(f"\nErro durante a coleta: {erro}")
        return

    print("\nResumo da pesquisa:")
    print(f"Área pesquisada: {area}")
    print(f"Vagas coletadas: {len(df)}")






if __name__ == "__main__":
    main()
