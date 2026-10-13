import pandas as pd

def preparar_gupy():
    return pd.DataFrame()

def preparar_infojobs():
    return pd.DataFrame()

if __name__ == "__main__":
    gupy = preparar_gupy()
    infojobs = preparar_infojobs()
    todas = pd.concat([gupy, infojobs], ignore_index=True)
    print("TOTAL:", len(todas))







