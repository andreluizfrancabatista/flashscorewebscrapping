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
wd_Chrome = webdriver.Chrome(service=Service(
    ChromeDriverManager().install()), options=options)

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

# Distribuição Poisson
def poisson(x, mean):
  return ((math.exp(-mean) * (pow(mean, x)))/(math.factorial(x)) *100)

partidas = 30

"""# Iniciando a Raspagem de Dados"""

# Com o WebDrive a gente consegue a pedir a página (URL)
wd_Chrome.get("https://www.flashscore.com/")
time.sleep(2)

# Para jogos do dia seguinte / Comentar essa linha para os jogos agendados de hoje
# wd_Chrome.find_element(By.CSS_SELECTOR,'button.calendar__navigation--tomorrow').click()
# time.sleep(2)

# next_day = wd_Chrome.find_elements(By.CSS_SELECTOR, 'button.calendar__navigation--tomorrow')
# for button in next_day:
#     wd_Chrome.execute_script("arguments[0].click();", button)
# time.sleep(2)

# Identificar o dia dos jogos
Date = wd_Chrome.find_element(By.CSS_SELECTOR, 'button#calendarMenu').text
print(f'Jogos do dia {Date[0:5]} {week[Date[6:]]}')

# Abrir os jogos fechados
display_matches = wd_Chrome.find_elements(By.CSS_SELECTOR, 'div.event__info')
for button in display_matches:
    wd_Chrome.execute_script("arguments[0].click();", button)
time.sleep(2)

# Pegando o ID dos Jogos
id_jogos = []
# Para jogos agendados (próximos)
jogos = wd_Chrome.find_elements(By.CSS_SELECTOR, 'div.event__match--scheduled') #scheduled

# Para jogos ao vivo (live)
# jogos = wd_Chrome.find_elements(By.CSS_SELECTOR,'div.event__match--live')

for i in jogos:
    id_jogos.append(i.get_attribute("id"))

# Exemplo de ID de um jogo: 'g_1_Gb7buXVt'
id_jogos = [i[4:] for i in id_jogos]

jogo = {
    'Date': [], 'Time': [], 'Country': [], 'League': [], 'Home': [], 'Away': [],
    'golsHome': [], 'jogosHome': [], 'golsAway': [], 'jogosAway': [],
    'avgHome': [], 'avgAway': [], 'avgAvg': [],
    '0x0': [], '1x0': [], '2x0': [], '1x1': [], '0x1': [], '0x2': [], 'U25': [], 'O25': []
}

# Lista de países vetados
Countries = ["RUSSIA", "BELARUS", "UKRAINE"]

for x, link in enumerate(tqdm(id_jogos, total=len(id_jogos))):
    # if(x>11):
    #     break
    wd_Chrome.get(f'https://www.flashscore.com/match/{link}/#/match-summary/')  # English

    # Checar se o país está na lista de vetados
    Country = wd_Chrome.find_element(By.CSS_SELECTOR, 'span.tournamentHeader__country').text.split(':')[0]
    if Country in Countries: # not in ["BRAZIL"]:
        continue

    # Pegando as Informacoes Básicas do Jogo
    try:
        Date = wd_Chrome.find_element(By.CSS_SELECTOR, 'div.duelParticipant__startTime').text.split(' ')[0]
        Time = wd_Chrome.find_element(By.CSS_SELECTOR, 'div.duelParticipant__startTime').text.split(' ')[1]
        Country = wd_Chrome.find_element(By.CSS_SELECTOR, 'span.tournamentHeader__country').text.split(':')[0]
        League = wd_Chrome.find_element(By.CSS_SELECTOR, 'span.tournamentHeader__country')
        League = League.find_element(By.CSS_SELECTOR, 'a').text
        Home = wd_Chrome.find_element(By.CSS_SELECTOR, 'div.duelParticipant__home')
        LinkHome = Home.find_element(By.CSS_SELECTOR, 'div.participant__participantName')
        LinkHome = LinkHome.find_element(By.TAG_NAME, 'a').get_attribute('href')
        Home = Home.find_element(By.CSS_SELECTOR, 'div.participant__participantName').text
        Away = wd_Chrome.find_element(By.CSS_SELECTOR, 'div.duelParticipant__away')
        LinkAway = Away.find_element(By.CSS_SELECTOR, 'div.participant__participantName')
        LinkAway = LinkAway.find_element(By.TAG_NAME, 'a').get_attribute('href')
        Away = Away.find_element(By.CSS_SELECTOR, 'div.participant__participantName').text
        
        # Verificar se o nome do time tem (xxx) no final e remover
        if ")" in Home:
            pos = Home.find('(')
            Home = Home[:pos-1]
        if ")" in Away:
            pos = Away.find('(')
            Away = Away[:pos-1]

        # Acessar a página de /results/ de cada time (Home e Away)
        ### HOME ###
        # Inicializando variáveis de contagem
        gols = 0
        total = 0
        golsArrayHome = []
        golsSofridosArray = []
        wd_Chrome.get(f'{LinkHome}results/')  # English
        # OR 'div.event__match--last'
        jogos = wd_Chrome.find_elements(By.CSS_SELECTOR, 'div.event__match--static')
        for i in jogos:
            try:
                resultHome = i.find_element(By.CSS_SELECTOR, 'div.event__participant--home').text
                # Verificar se o nome do time tem (xxx) no final e remover
                if ")" in resultHome:
                    pos = resultHome.find('(')
                    resultHome = resultHome[:pos-1]
                if (Home == resultHome):
                    golsHome = i.find_element(By.CSS_SELECTOR, 'div.event__score--home').text
                    golsSofridos = i.find_element(By.CSS_SELECTOR, 'div.event__score--away').text
                    if(golsHome != "-"):
                        # gols marcardos em casa
                        golsHome = int(golsHome)
                        gols += golsHome
                        total += 1  # total de jogos que o time Home fez em casa dentro da lista de 30 jogos
                        golsArrayHome.append(golsHome)
                        # gols sofridos em casa
                        golsSofridos = int(golsSofridos)
                        golsSofridosArray.append(golsSofridos)
                    if(total >= partidas):
                        break
            except Exception as error:
                print(f'\n{Home} x {LinkHome}: {error}')

        # Calcular o total de jogos, a média e desvio padrão
        golsHome = gols
        jogosHome = total
        mediaGolsHome = golsHome/jogosHome
        golsArrayHome = np.array(golsArrayHome)
        # sdHome = golsArrayHome.std()  # Calcular o SD de golsArrayHome
        # gols sofridos em casa
        golsSofridosArray = np.array(golsSofridosArray)
        mediaGolsSofridosHome = np.mean(golsSofridosArray)
        # sdGolsSofridosHome = golsSofridosArray.std()
        

        ### AWAY ###
        # Inicializando variáveis de contagem
        gols = 0
        total = 0
        golsArrayAway = []
        golsSofridosArray = []
        wd_Chrome.get(f'{LinkAway}results/')  # English
        # OR 'div.event__match--last'
        jogos = wd_Chrome.find_elements(
            By.CSS_SELECTOR, 'div.event__match--static')
        for i in jogos:
            try:
                resultAway = i.find_element(By.CSS_SELECTOR, 'div.event__participant--away').text
                # Verificar se o nome do time tem (xxx) no final e remover
                if ")" in resultAway:
                    pos = resultAway.find('(')
                    resultAway = resultAway[:pos-1]
                if (Away == resultAway):
                    golsAway = i.find_element(By.CSS_SELECTOR, 'div.event__score--away').text
                    golsSofridos = i.find_element(By.CSS_SELECTOR, 'div.event__score--home').text
                    if(golsAway != "-"):
                        # gols marcados visitante
                        golsAway = int(golsAway)
                        gols += golsAway
                        total += 1  # total de jogos que o time Away fez fora de casa dentro da lista de 30 jogos
                        golsArrayAway.append(golsAway)
                        # gols sofridos visitante
                        golsSofridos = int(golsSofridos)
                        golsSofridosArray.append(golsSofridos)
                    if(total >= partidas):
                        break
            except Exception as error:
                print(f'\n{Away} x {LinkAway}: {error}')

        # Calcular o total de jogos, a média e desvio padrão
        golsAway = gols
        jogosAway = total
        mediaGolsAway = golsAway/jogosAway
        golsArrayAway = np.array(golsArrayAway)
        # sdAway = golsArrayAway.std()  # Calcular o SD de golsArrayAway
        # gols sofridos visitante
        golsSofridosArray = np.array(golsSofridosArray) 
        mediaGolsSofridosFora = np.mean(golsSofridosArray)
        # sdGolsSofridosAway = golsSofridosArray.std()


        # Calcular as probabilidades pelo método de simulações de Monte Carlo
        mean1 = np.mean([mediaGolsHome, mediaGolsSofridosFora]) # média entre gols marcados home e gols sofridos do visitante
        mean2 = np.mean([mediaGolsAway, mediaGolsSofridosHome]) # média entre gols marcados fora e gols sofridos do home
        ngols = 6

        probs = {
            "Home":[],
            "Away":[]
        }

        probs["Home"] = [poisson(x, mean1) for x in range(ngols+1)]
        probs["Away"] = [poisson(x, mean2) for x in range(ngols+1)]

        g1 = np.arange(ngols+1)
        s1 = pd.Series(probs["Home"])
        s2 = pd.Series(probs["Away"])

        tuples1 = list(zip(g1, s1))
        tuples2 = list(zip(g1, s2))

        index1 = pd.MultiIndex.from_tuples(tuples1, names=["gols", "prob"])
        index2 = pd.MultiIndex.from_tuples(tuples2, names=["gols", "prob"])

        df = pd.DataFrame(1, index=index1, columns=index2)

        s1 = pd.Series(df.index.get_level_values(1))
        s2 = pd.Series(df.columns.get_level_values(1))
        df1 = pd.DataFrame(1, index=s1.index, columns=s2.index)
        new = round((df1.multiply(s1, axis='index') * s2 / 100),2)
        #
        # new[coluna][linha] - new[away][home]
        #
        r0x0 = new[0][0] # 0x0 
        r0x1 = new[1][0] # 0x1
        r0x2 = new[2][0] # 0x2
        r1x1 = new[1][1] # 1x1
        r1x0 = new[0][1] # 1x0
        r2x0 = new[0][2] # 2x0
        # rU25 = r0x0 + r0x1 + r0x2 + r1x1 + r1x0 + r2x0

        #
        # Calcular U25 e O25
        #
        lim = 2.5
        rU25 = 0
        rO25 = 0
        for h in range(0, ngols+1):
            for a in range(0, ngols+1):
                if(h + a < lim):
                    rU25 += new[a][h]
                else:
                    rO25 += new[a][h]
        

    except Exception as error:
        print(f'\n{error}\nExcept: {Home} x {Away} - {link}')
        pass

    # jogo = {
    #     'Date': [], 'Time': [], 'Country': [], 'League': [], 'Home': [], 'Away': [],
    #     'golsHome': [], 'jogosHome': [], 'golsAway': [], 'jogosAway': [],
    #     'avgHome': [], 'sdHome': [], 'avgAway': [], 'sdAway': [], 'avgSum': [],
    #     '0x0': [], '1x0': [], '2x0': [], '1x1': [], '0x1': [], '0x2': [], 'U25': [], 'O25: []
    # }

    # Colocar tudo dentro do df pra salvar no csv
    jogo['Date'].append(Date.replace(".", "/"))
    jogo['Time'].append(Time)
    jogo['Country'].append(Country.replace(";", "-"))
    jogo['League'].append(League.replace(";", "-"))
    jogo['Home'].append(Home.replace(";", "-"))
    jogo['Away'].append(Away.replace(";", "-"))
    jogo['golsHome'].append(golsHome)
    jogo['jogosHome'].append(jogosHome)
    jogo['golsAway'].append(golsAway)
    jogo['jogosAway'].append(jogosAway)
    
    jogo['0x0'].append(str(round(r0x0, 4)).replace(".", ","))
    jogo['0x1'].append(str(round(r0x1, 4)).replace(".", ","))
    jogo['0x2'].append(str(round(r0x2, 4)).replace(".", ","))
    jogo['1x1'].append(str(round(r1x1, 4)).replace(".", ","))
    jogo['1x0'].append(str(round(r1x0, 4)).replace(".", ","))
    jogo['2x0'].append(str(round(r2x0, 4)).replace(".", ","))
    jogo['U25'].append(str(round(rU25, 4)).replace(".", ","))
    jogo['O25'].append(str(round(rO25, 4)).replace(".", ","))
    
    jogo['avgHome'].append(str(round(mean1, 4)).replace(".", ","))
    # jogo['sdHome'].append(str(round(sdHome, 4)).replace(".", ","))
    jogo['avgAway'].append(str(round(mean2, 4)).replace(".", ","))
    # jogo['sdAway'].append(str(round(sdAway, 4)).replace(".", ","))
    jogo['avgAvg'].append(str(round((mean1 + mean2)/2, 4)).replace(".", ","))


# Para atualizar o CSV a cada 'n' interações.
# Colocar esse código abaixo dentro do loop acima (subir uma identação)
# Colocar uma condição para a cada 'n' interações do loop, realizar a escrita no arquivo
df = pd.DataFrame(jogo)

# Drop rows jogosHome < 15 or jogosAway < 15
filtered = df[(df['jogosHome'] < 15) | (df['jogosAway'] < 15)].index
df.drop(filtered, inplace=True)

df = df.sort_values(by=['U25'], ascending=False)
df.reset_index(inplace=True, drop=True)
df.index = df.index.set_names(['Nº'])
df = df.rename(index=lambda x: x + 1)
filename = "lista_de_jogos/jogos_do_dia_" + \
    Date.replace(".", "_")+"_last"+str(partidas) + \
    "_U25FT_com_SD_com_MonteCarlo.csv"
df.to_csv(filename, sep=";")
