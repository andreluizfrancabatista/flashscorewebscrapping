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

# Dict com os dias da semana e as siglas
week = {
    "SU": "Sunday",
    "MO": "Monday",
    "TU": "Tuesday",
    "WE": "Wednesday",
    "TH": "Thrusday",
    "FR": "Friday",
    "SA": "Saturday"
}

"""# Iniciando a Raspagem de Dados"""

# Com o WebDrive a gente consegue a pedir a página (URL)
wd_Chrome.get("https://www.flashscore.com/") 
time.sleep(2)

## Para jogos do dia seguinte / Comentar essa linha para os jogos agendados de hoje 
# wd_Chrome.find_element(By.CSS_SELECTOR,'button.calendar__navigation--tomorrow').click()
# time.sleep(2)

next_day = wd_Chrome.find_elements(By.CSS_SELECTOR,'button.calendar__navigation--tomorrow')
for button in next_day:
    wd_Chrome.execute_script("arguments[0].click();", button)
time.sleep(2)

# Identificar o dia dos jogos
Date = wd_Chrome.find_element(By.CSS_SELECTOR, 'button#calendarMenu').text
print(f'Jogos do dia {Date[0:5]} {week[Date[6:]]}')

# Abrir os jogos fechados
display_matches = wd_Chrome.find_elements(By.CSS_SELECTOR, 'div.event__info')
for button in display_matches:
    wd_Chrome.execute_script("arguments[0].click();", button)

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

#Procurar somente por gols marcados
jogo = {
    'Date':[],'Time':[],'Country':[],'League':[],'Home':[],'Away':[],
    'golsHome':[], 'jogosHome':[], 'AvgHome':[], 
    'golsAway':[], 'jogosAway':[], 'AvgAway':[],
    'avgSum':[]
}

for link in tqdm(id_jogos, total=len(id_jogos)):
# for i, link in enumerate(id_jogos):
#     if(i>4):
#         break
    wd_Chrome.get(f'https://www.flashscore.com/match/{link}/#/standings/live') # English
    # time.sleep(2)
    try:
        element = WebDriverWait(wd_Chrome, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.table__row--selected'))
        )
    except:
        continue

    gols, total, avg = 0, 0, 0
    # Pegando as Informacoes Básicas do Jogo
    try:
        Date = wd_Chrome.find_element(By.CSS_SELECTOR,'div.duelParticipant__startTime').text.split(' ')[0]
        Time = wd_Chrome.find_element(By.CSS_SELECTOR,'div.duelParticipant__startTime').text.split(' ')[1]
        Country = wd_Chrome.find_element(By.CSS_SELECTOR,'span.tournamentHeader__country').text.split(':')[0]
        League = wd_Chrome.find_element(By.CSS_SELECTOR,'span.tournamentHeader__country')
        League = League.find_element(By.CSS_SELECTOR,'a').text
        Home = wd_Chrome.find_element(By.CSS_SELECTOR,'div.duelParticipant__home')
        Home = Home.find_element(By.CSS_SELECTOR,'div.participant__participantName').text
        Away = wd_Chrome.find_element(By.CSS_SELECTOR,'div.duelParticipant__away')
        Away = Away.find_element(By.CSS_SELECTOR,'div.participant__participantName').text

        gols, total, avg = 0, 0, 0
        
        # Pegar os gols marcados do time da casa e visitante
        # info[0] é o time melhor classificado na tabela
        # info[1] é o time pior classificado na tabela

        infodict = {}
        infodict[Home] = {}
        infodict[Away] = {}

        infos = wd_Chrome.find_elements(By.CSS_SELECTOR, 'div.table__row--selected') # Pegar as duas div.table__row--selected
        for info in infos:
            name = info.find_element(By.CSS_SELECTOR, 'a.tableCellParticipant__name').text # Pegar o nome do time 
            gols = info.find_element(By.CSS_SELECTOR, 'span.table__cell--score').text # Pegar os gols marcardos X:Y (X=marcados, Y=sofridos)
            gols = int(gols.split(":")[0]) # [0] são os gols marcados, [1] são os gols sofridos
            total = info.find_element(By.CSS_SELECTOR, 'span.table__cell--value').text # Pegar o total de partidas div.table_cell--value [0]
            total = int(total)
            if (total > 0):
                avg = gols/total # Cálculo da média de gols marcados por partida
            infodict[name]['gols'] = gols
            infodict[name]['total'] = total
            infodict[name]['avg'] = avg
       
    except:
        print(f'\nExcept: {Home} x {Away} - {link}')
        pass

    # print(Date,Time,Country,League,Home,Away,golsHome,totalHome,AvgHome, golsAway, totalAway, AvgAway) 
    # print(f'{Date}, {Time}, {Country}, {League}\n{Home} {pHome*100:.2f} x {pAway*100:.2f} {Away}\n') 

    # Colocar tudo dentro do df pra salvar no csv
    try:
        jogo['Date'].append(Date.replace(".", "/"))
        jogo['Time'].append(Time)
        jogo['Country'].append(Country.replace(";", "-"))
        jogo['League'].append(League.replace(";", "-"))
        jogo['Home'].append(Home.replace(";", "-"))
        jogo['Away'].append(Away.replace(";", "-"))
        jogo['golsHome'].append(infodict[Home]['gols'])
        jogo['jogosHome'].append(infodict[Home]['total'])
        jogo['AvgHome'].append(str(round(infodict[Home]['avg'], 4)).replace(".", ","))
        jogo['golsAway'].append(infodict[Away]['gols'])
        jogo['jogosAway'].append(infodict[Away]['total'])
        jogo['AvgAway'].append(str(round(infodict[Away]['avg'], 4)).replace(".", ","))
        jogo['avgSum'].append(
            str(round((round(infodict[Home]['avg'], 4) + round(infodict[Away]['avg'], 4)), 4)).replace(".", ",")
            )
    except:
        print(f'\nErro no append: {Home} x {Away} - {link}')
        pass
    
df = pd.DataFrame(jogo)
df = df.sort_values(by=['avgSum'], ascending=False)
df.reset_index(inplace=True, drop=True)
df.index = df.index.set_names(['Nº'])
df = df.rename(index=lambda x: x + 1)
# print(df)
filename = "lista_de_jogos/jogos_do_dia_"+Date.replace(".", "_")+"_golsFT_2.csv"
df.to_csv(filename, sep=";")