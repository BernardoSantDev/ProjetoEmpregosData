
def escolher_area():
    print("===================================")
    print("     OBSERVATÓRIO DE ESTÁGIOS      ")
    print("===================================")

    while True:
        area = input("\nQual área de estágio deseja pesquisar? ").strip()

        if area:
            return area

        print("Erro: digite uma área válida!")


def main():
    area = escolher_area()

    print(f"\nÁrea selecionada: {area}")


if __name__ == "__main__":
    main()
