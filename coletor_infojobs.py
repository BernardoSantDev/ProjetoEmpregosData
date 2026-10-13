import re
import time
from urllib.parse import quote

import requests
import pandas as pd
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (projeto academico - analise de vagas de estagio)"}
BASE = "https://www.infojobs.com.br/mf-publicarea/VacancyList/GetVacancyListFragment"

FORMAS = ["estágio", "estagiário"]
ASSUNTOS = ["ti", "dados", "desenvolvimento de sistemas", "suporte técnico ti",
            "python", "sql", "banco de dados", "infraestrutura ti"]
TERMOS = [f"{forma} {assunto}" for forma in FORMAS for assunto in ASSUNTOS]














