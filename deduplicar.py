
from pathlib import Path
import pandas as pd
import re
import unicodedata


PASTA_DADOS = Path(__file__).resolve().parent / "dados"





if __name__ == "__main__":
    identificar_duplicatas()
