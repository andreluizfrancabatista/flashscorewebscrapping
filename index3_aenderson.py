import time
tempo_inicial = time.time()

import sys
sys.path.insert(0,'/usr/lib/chromium-browser/chromedriver')
import os
import numpy as np
import json

# Utilizando o WebDriver do Selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

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

"""# Importando as Bibliotecas"""
import concurrent.futures
from functools import reduce
import pandas as pd
import time
from tqdm import tqdm
from selenium.webdriver.common.by import By

def scrapping(links):    

    wd_Chrome.get("https://www.flashscore.com/") 
    time.sleep(2)
    for link in enumerate(tqdm(links, total=len(links))):
        wd_Chrome.get(link[1])
        Team = wd_Chrome.find_element(By.CSS_SELECTOR, 'div.heading')
        Team = Team.find_element(By.CSS_SELECTOR, 'div.heading__title')
        Team = Team.find_element(By.CSS_SELECTOR, 'div.heading__name').text
        jogos_fora = 0
        jogos_casa = 0
        gols_total = 0
        total_jogos = 0    
        gols_casa_total = 0
        gols_fora_total = 0
    
        try:
            wd_Chrome.get(link)
            Country = wd_Chrome.find_element(By.CSS_SELECTOR,'div.container__heading')
            Country = wd_Chrome.find_element(By.CSS_SELECTOR,'h2.breadcrumb').text.split('\n')[1]
            Team = wd_Chrome.find_element(By.CSS_SELECTOR, 'div.heading')
            Team = Team.find_element(By.CSS_SELECTOR, 'div.heading__title')
            Team = Team.find_element(By.CSS_SELECTOR, 'div.heading__name').text

            jogos = wd_Chrome.find_elements(By.CSS_SELECTOR,'div.event__match--static')
            
            for jogo in jogos:
                gols_casa = 0
                gols_fora = 0
                try:
                    home = jogo.find_element(By.CSS_SELECTOR, 'div.event__participant--home').text.split('(')[0]
                    home = "".join(home.split())
                    away = jogo.find_element(By.CSS_SELECTOR, 'div.event__participant--away').text.split('(')[0]
                    away = "".join(away.split())
                    total_jogos += 1
                    
                    if Team == home:
                        golsft_home = jogo.find_element(By.CSS_SELECTOR, 'div.event__score--home').text
                        golsft_home = int(golsft_home)
                        golsft_away = jogo.find_element(By.CSS_SELECTOR, 'div.event__score--away').text
                        golsft_away = int(golsft_away)
                        gols_casa = golsft_home + golsft_away
                        jogos_casa += 1
                        gols_casa_total += gols_casa
                        
                    else:
                        golsft_home = jogo.find_element(By.CSS_SELECTOR, 'div.event__score--home').text
                        golsft_home = int(golsft_home)
                        golsft_away = jogo.find_element(By.CSS_SELECTOR, 'div.event__score--away').text
                        golsft_away = int(golsft_away)
                        gols_fora = golsft_home + golsft_away
                        jogos_fora += 1
                        gols_fora_total += gols_fora
                    
                    gols_total = gols_casa_total + gols_fora_total
                    if(total_jogos>=30):
                        break        
                except:
                    pass
            
            avg_casa = gols_casa_total/jogos_casa
            avg_fora = gols_fora_total/jogos_fora
            avg_geral = gols_total/total_jogos

            tabela['Time'].append(Team)
            tabela['País'].append(Country)
            tabela['Jogos'].append(total_jogos)
            tabela['Gols'].append(gols_total)
            tabela['Média geral'].append(str(round(avg_geral, 4)).replace(".", ","))
            tabela['Média em casa'].append(str(round(avg_casa, 4)).replace(".", ","))
            tabela['Média fora'].append(str(round(avg_fora, 4)).replace(".", ","))
            print(Team)
        except:
            pass

if __name__ == '__main__':
    
    tabela = {
        'Time':[],'País':[],'Gols':[],'Jogos':[], 'Média em casa':[],
        'Média fora':[], 'Média geral':[]
    }       
    
    # Lendo arquivo json e colando na variável dados
    with open('links.json', 'r') as arquivo:
        dados = json.load(arquivo)

    links = list(dados.values())[0]

    with concurrent.futures.ProcessPoolExecutor() as executor:
        metade = int(len(links) / 2)
        mapped = executor.map(scrapping, [links[:metade], links[metade:]])
    
    df = pd.DataFrame(tabela)
    df.to_csv('TrabalhoPPD.csv', sep=";")
    tempo_final = time.time()

    tempo_decorrido = tempo_final - tempo_inicial 

    # Calcula horas, minutos e segundos
    horas = int(tempo_decorrido // 3600)
    minutos = int((tempo_decorrido % 3600) // 60)
    segundos = int(tempo_decorrido % 60)

    print(f'Programa gastou {horas} horas, {minutos} minutos e {segundos} segundos')