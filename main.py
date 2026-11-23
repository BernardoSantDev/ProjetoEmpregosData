
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
    print("\nTermos que serão pesquisados:")

    for termo in termos:
        print(f"- {termo}")



if __name__ == "__main__":
    main()
