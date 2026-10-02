import time
import requests
import pandas as pd

URL = "https://portal.gupy.io/api/job-search/jobs"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (projeto academico - analise de vagas)"
}
FORMAS = ["Estágio", "Estagiário"]
AREAS = ["TI", "Tecnologia", "Dados", "Sistemas", "Desenvolvimento",
         "Software", "Suporte", "Infraestrutura", "BI", "Automação"]
TERMOS = [f"{forma} {area}" for forma in FORMAS for area in AREAS]






