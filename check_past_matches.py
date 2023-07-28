from tqdm import tqdm
import time
import pandas as pd
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
import sys
sys.path.insert(0, '/usr/lib/chromium-browser/chromedriver')

"""# Configuração do Web-Driver"""

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
wd_Chrome = webdriver.Chrome('chromedriver', options=options)

"""# Importando as Bibliotecas"""


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

# Para jogos do dia anterior / Comentar essa linha para os jogos finalizados de hoje
# wd_Chrome.find_element(By.CSS_SELECTOR,'button.calendar__navigation--yesterday').click()
# time.sleep(2)

# wd_Chrome.find_element(By.CSS_SELECTOR,'button.calendar__navigation--yesterday').click()
# time.sleep(2)

# Cria as stats
stats = {'Date': [],
         'Weekday': [],
         'Total': [],
         'GolsHT': [],
         'Porc': []
         }

# Quantidade de dias passados
dias = 3
while(dias > 0):
    # Pegar a data
    data = wd_Chrome.find_element(By.CSS_SELECTOR, 'button#calendarMenu').text

    # Para jogos encerrados
    jogos = wd_Chrome.find_elements(
        By.CSS_SELECTOR, 'div.event__match--twoLine:not(.event__match--live)')
    
    # Abrir os jogos fechados
    display_matches = wd_Chrome.find_elements(By.CSS_SELECTOR, 'div.event__info')
    for button in display_matches:
        wd_Chrome.execute_script("arguments[0].click();", button)

    total = 0
    golsht = 0

    for jogo in tqdm(jogos, total=len(jogos)):
        try:
            golsHome = jogo.find_element(
                By.CSS_SELECTOR, 'div.event__part--home').text
            golsHome = int(golsHome[1:2])
            golsAway = jogo.find_element(
                By.CSS_SELECTOR, 'div.event__part--away').text
            golsAway = int(golsAway[1:2])
            total += 1
            if((golsHome+golsAway) > 0):
                golsht += 1
        except:
            # print(f'?x? ', end="")
            pass
    # print(f'Data: {data[0:5]} - {week[data[6:]]}\nTotal: {total}\nJogos HT: {golsht}\nPorc.:{(golsht/total):.2f}\n\n')
    stats['Date'].append(data[0:5])
    stats['Weekday'].append(week[data[6:]])
    stats['Total'].append(total)
    stats['GolsHT'].append(golsht)
    try:
        stats['Porc'].append(str(round((golsht/total), 4)).replace(".", ","))
    except:
        pass
    try:
        # wd_Chrome.find_element(By.CSS_SELECTOR, 'button.calendar__navigation--yesterday').click()
        next_day = wd_Chrome.find_elements(By.CSS_SELECTOR, 'button.calendar__navigation--yesterday')
        for button in next_day:
            wd_Chrome.execute_script("arguments[0].click();", button)
        time.sleep(4)
    except:
        dias = 0
    dias -= 1

df = pd.DataFrame(stats)
df.reset_index(inplace=True, drop=True)
df.index = df.index.set_names(['Nº'])
df = df.rename(index=lambda x: x + 1)
print(df)
filename = "lista_de_jogos/stats.csv"
df.to_csv(filename, sep=";")
