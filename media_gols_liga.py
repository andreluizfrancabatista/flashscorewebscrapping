# -*- coding: utf-8 -*-
"""WebScraping - FlashScore.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Qr3mASEik_iesvvoel-5v63csKk1feuj

Criado por:
*   Eduardo Lemos (@esniq1)
*   Leandro Filho (@futpythontrader)

# Instalando as Bibliotecas e as Dependências
"""
"""# Importando as Bibliotecas"""

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
from tqdm import tqdm
import pandas as pd
import time
import os
import numpy as np
import math
import sys
sys.path.insert(0, '/usr/lib/chromium-browser/chromedriver')

# Configuração do Web-Driver
# Utilizando o WebDriver do Selenium
# Instanciando o Objeto ChromeOptions
options = webdriver.ChromeOptions()

# Passando algumas opções para esse ChromeOptions
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--start-maximized')
options.add_argument('--ignore-certificate-errors')
options.add_argument('--disable-crash-reporter')
options.add_argument('--log-level=3')

# Criação do WebDriver do Chrome
wd_Chrome = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Dict com os dias da semana e as siglas
# week = {
#     "SU": "Sunday",
#     "MO": "Monday",
#     "TU": "Tuesday",
#     "WE": "Wednesday",
#     "TH": "Thrusday",
#     "FR": "Friday",
#     "SA": "Saturday"
# }

# Distribuição Poisson
# def poisson(x, mean):
#     return ((math.exp(-mean) * (pow(mean, x)))/(math.factorial(x)) * 100)


# partidas = 30

"""# Iniciando a Raspagem de Dados"""

# Com o WebDrive a gente consegue a pedir a página (URL) da Liga
wd_Chrome.get("https://www.flashscore.com.br/futebol/argentina/liga-de-reservas/classificacao/#/Od3KLsPf/table/overall")
time.sleep(2)

# Informações
info = {
    "jogos":[],
    "mediaGols":[]
}

# Pegar todas as divs dos times participantes
teams = wd_Chrome.find_elements(By.CSS_SELECTOR, 'div.ui-table__row')

# Pega o nome do país e da Liga
league = wd_Chrome.find_element(By.CSS_SELECTOR, 'div.heading__name').text
print(f'Liga: {league}')
country = wd_Chrome.find_elements(By.CSS_SELECTOR, 'a.breadcrumb__link')[1].text
print(f'País: {country}')

# Percorre as divs procurando pelos gols
golsTotal = 0
partidasTotal = 0
for team in teams:
    gols = team.find_element(By.CSS_SELECTOR, 'span.table__cell--score')
    golsp = int(gols.text.split(':')[0])
    golsa = int(gols.text.split(':')[1])
    golsTotal += (golsp + golsa)
    partidas = team.find_element(By.CSS_SELECTOR, 'span.table__cell--value').text
    partidas = int(partidas)
    partidasTotal += partidas
    print(f'J: {partidas}. G: {golsp+golsa}')

mediaGols = golsTotal/partidasTotal
print(f'Média de gols: {mediaGols}')
