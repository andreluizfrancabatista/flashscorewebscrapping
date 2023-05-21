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

# Instalando o Selenium
# !pip install selenium

# Atualizando o Ubuntu para executar corretamento o apt-install
# !apt-get update

# Instalando o ChromeDrive e Trazendo ele para a Pasta Local
# !apt install chromium-chromedriver

# !cp /usr/lib/chromium-browser/chromedriver /usr/bin
import time
start_time = time.time()

import sys
sys.path.insert(0,'/usr/lib/chromium-browser/chromedriver')



"""# Configuração do Web-Driver"""

# Utilizando o WebDriver do Selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
wd_Chrome = webdriver.Chrome('chromedriver',options=options)

"""# Importando as Bibliotecas"""

import pandas as pd
import time
from tqdm import tqdm
from selenium.webdriver.common.by import By

"""# Iniciando a Raspagem de Dados"""

# Com o WebDrive a gente consegue a pedir a página (URL)
wd_Chrome.get("https://www.flashscore.com/") 
time.sleep(2)

## Para jogos do dia seguinte / Comentar essa linha para os jogos agendados de hoje 
#wd_Chrome.find_element(By.CSS_SELECTOR,'button.calendar__navigation--tomorrow').click()
time.sleep(2)

# Pegando o ID dos Jogos
id_jogos = []
## Para jogos agendados (próximos)
jogos = wd_Chrome.find_elements(By.CSS_SELECTOR,'div.event__match--scheduled')

## Para jogos ao vivo (live)
# jogos = wd_Chrome.find_elements(By.CSS_SELECTOR,'div.event__match--live')

for i in jogos:
    id_jogos.append(i.get_attribute("id"))

# Exemplo de ID de um jogo: 'g_1_Gb7buXVt'    
id_jogos = [i[4:] for i in id_jogos]

# Exibir a quantidade de jogos coletados
print(f'Jogos: {len(id_jogos)}')

# for link in tqdm(id_jogos, total=len(id_jogos)):
for link in id_jogos:
    wd_Chrome.get(f'https://www.flashscore.com/match/{link}/#/match-summary/') # English
    try:
        Date = wd_Chrome.find_element(By.CSS_SELECTOR,'div.duelParticipant__startTime').text.split(' ')[0]
        Time = wd_Chrome.find_element(By.CSS_SELECTOR,'div.duelParticipant__startTime').text.split(' ')[1]
        Country = wd_Chrome.find_element(By.CSS_SELECTOR,'span.tournamentHeader__country').text.split(':')[0]
        League = wd_Chrome.find_element(By.CSS_SELECTOR,'span.tournamentHeader__country')
        League = League.find_element(By.CSS_SELECTOR,'a').text
        Home = wd_Chrome.find_element(By.CSS_SELECTOR,'div.duelParticipant__home')
        LinkHome = Home.find_element(By.CSS_SELECTOR,'div.participant__participantName')
        LinkHome = LinkHome.find_element(By.TAG_NAME, 'a').get_attribute('href')
        Home = Home.find_element(By.CSS_SELECTOR,'div.participant__participantName').text
        Away = wd_Chrome.find_element(By.CSS_SELECTOR,'div.duelParticipant__away')
        LinkAway = Away.find_element(By.CSS_SELECTOR,'div.participant__participantName')
        LinkAway = LinkAway.find_element(By.TAG_NAME, 'a').get_attribute('href')
        Away = Away.find_element(By.CSS_SELECTOR,'div.participant__participantName').text
    except:
        pass
    print(f'{Date}, {Time}, {Country}, {League}\n{Home} x {Away}\n') 

print(f'% --- {time.time() - start_time} seconds --- %')