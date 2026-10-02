import re
import pandas as pd
from bs4 import BeautifulSoup

df = pd.read_csv("vagas_brutas.csv")
print("Vagas no CSV:", len(df))

