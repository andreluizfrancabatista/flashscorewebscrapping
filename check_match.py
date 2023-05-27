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

# Receber o ID da partida
id_jogos = ["rJGYG4dD", "Ovkpf7qo", "4SgPLJxQ", "4jxCCFaC", "M7tiHwos"]
jogo = {'Date':[],'Time':[],'Country':[],'League':[],'Home':[],'Away':[],'golshtHome':[], 'totalHome':[], 'AvgHome':[], 'golshtAway':[], 'totalAway':[], 'AvgAway':[], 'pHome':[], 'pAway':[], 'Sum':[], 'Times':[]}

for link in tqdm(id_jogos, total=len(id_jogos)):
# for i, link in enumerate(id_jogos):
#     if(i>4):
#         break
    wd_Chrome.get(f'https://www.flashscore.com/match/{link}/#/match-summary/') # English
    
    total, golsht = 0, 0
    golsHome, golsAway = 0, 0
    golshtAway, golshtHome = 0, 0
    mediaGolsHTHome, mediaGolsHTAway = 0, 0
    totalHome, totalAway = 0, 0
    pHome, pAway = 0, 0
    # Pegando as Informacoes Básicas do Jogo
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
        
        total, golsht = 0, 0
        golsHome, golsAway = 0, 0
        golshtAway, golshtHome = 0, 0
        mediaGolsHTHome, mediaGolsHTAway = 0, 0
        totalHome, totalAway = 0, 0
        pHome, pAway = 0, 0
        # Calcular a porcentagem de over 0,5 no HT de cada time
        links = [LinkHome, LinkAway]
        for index, sublink in enumerate(links):
            wd_Chrome.get(f'{sublink}results/') # English
            jogos = wd_Chrome.find_elements(By.CSS_SELECTOR,'div.event__match--static') #OR 'div.event__match--last'
            total, golsht = 0, 0
            gols = 0
            # print(f'{index}: {sublink}results/') # English
            for i in jogos:
                try:
                    golsHome = i.find_element(By.CSS_SELECTOR, 'div.event__part--home').text
                    golsHome = int(golsHome[1:2])
                    gols += golsHome
                    golsAway = i.find_element(By.CSS_SELECTOR, 'div.event__part--away').text
                    golsAway = int(golsAway[1:2])
                    gols += golsAway
                    # print(f'{golsHome}x{golsAway} ', end="")
                    total += 1
                    if((golsHome+golsAway) > 0):
                        golsht += 1
                except:
                    # print(f'?x? ', end="")
                    pass
            # print()
            if(index==0):
                pHome = golsht/total
                totalHome = total
                golshtHome = golsht
                mediaGolsHTHome = gols/total
                # print(f'pHome:{pHome*100:.2f} jogos:{totalHome} jogosComGolHT:{golshtHome} média:{mediaGolsHTHome:.2f} gols:{gols}')
            if(index==1):
                pAway = golsht/total
                totalAway = total
                golshtAway = golsht
                mediaGolsHTAway = gols/total
                # print(f'pAway:{pAway*100:.2f} jogos:{totalAway} jogosComGolHT:{golshtAway} média:{mediaGolsHTAway:.2f} gols:{gols}')
            # print()       
    except:
        print(f'\nExcept: {link}')
        pass

    # print(Date,Time,Country,League,Home,Away,Odds_H,Odds_D,Odds_A) 
    print(f'{Date}, {Time}, {Country}, {League}\n{Home} {pHome*100:.2f} x {pAway*100:.2f} {Away}\n') 

    # Colocar tudo dentro do df pra salvar no csv
    jogo['Date'].append(Date.replace(".", "/"))
    jogo['Time'].append(Time)
    jogo['Country'].append(Country.replace(";", "-"))
    jogo['League'].append(League.replace(";", "-"))
    jogo['Home'].append(Home.replace(";", "-"))
    jogo['Away'].append(Away.replace(";", "-"))
    jogo['golshtHome'].append(golshtHome)
    jogo['totalHome'].append(totalHome)
    jogo['AvgHome'].append(str(round(mediaGolsHTHome, 4)).replace(".", ","))
    jogo['golshtAway'].append(golshtAway)
    jogo['totalAway'].append(totalAway)
    jogo['AvgAway'].append(str(round(mediaGolsHTAway, 4)).replace(".", ","))
    jogo['pHome'].append(str(round(pHome, 4)).replace(".", ","))
    jogo['pAway'].append(str(round(pAway, 4)).replace(".", ","))
    jogo['Sum'].append(
        str(round((round(pHome, 4) + round(pAway, 4)), 4)).replace(".", ",")
        )
    jogo['Times'].append(
        str(round((round(pHome, 4) * round(pAway, 4)), 4)).replace(".", ",")
        )
    

df = pd.DataFrame(jogo)
df.reset_index(inplace=True, drop=True)
df.index = df.index.set_names(['Nº'])
df = df.rename(index=lambda x: x + 1)
# print(df)
filename = "lista_de_jogos/jogos_especificos_"+Date.replace(".", "_")+".csv"
df.to_csv(filename, sep=";")

