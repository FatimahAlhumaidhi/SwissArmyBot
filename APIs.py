import requests
import json
from selenium import webdriver
import urllib.parse
import os
import time
from selenium.webdriver.common.by import By


def getContact(number:str) -> str:
    with open("config.json", encoding='utf-8') as f:
            config = json.load(f)
    url = config['NUMBERBOOK_URL']+"?getName=true&phone="+number
    try:
        response = requests.get(url)
        payload = json.dumps(response.json()) 
        data = json.loads(payload)
        names = []
        if data['response'] == 'success':
           for elem in data['data']:
               names.append(elem['name'])
           names = set(names)
           return str(names)
        else:
            return 'could not find any record for this number'
    except:
        return 'sorry, something went wrong.'


def lookUp(word:str) -> str:
    executable_path = os.path.join('chromedriver_win32', 'chromedriver.exe')
    try:
        driver = webdriver.Chrome(executable_path=executable_path)
        url = 'https://www.almaany.com/ar/dict/ar-ar/{}/'.format(urllib.parse.quote_plus(word))

        driver.get(url)
        html = driver.page_source
        time.sleep(2)

        result = driver.find_elements(By.CLASS_NAME, 'meaning-results')
        if len(result) < 2:
            try:
                result = driver.find_elements(By.XPATH, '/html/body/section/div/div[2]/div[1]/div[1]/p')
                return result[0].text
            except:
                return 'عذراً لم يفلح بحثك بالعثور على أي نتائج'
        elems = result[1].find_elements(By.TAG_NAME, 'li')

        List = []
        for elem in elems:
            defin = {}
            get = elem.find_elements(By.TAG_NAME, 'span')
            defin['word'] = get[0].text.replace('\n', '') if len(get)> 0 else None
            get = elem.find_elements(By.TAG_NAME, 'ul')
            defin['meaning'] = get[0].text.replace('\n', '') if len(get)> 0 else None
            get = elem.find_elements(By.TAG_NAME, 'p')
            defin['dictionary'] = get[0].text.replace('\n', '') if len(get)> 0 else None
            if not all([defin['word'], defin['meaning'], defin['dictionary']]):
                continue
            List.append(defin)
        return List
    except:
        return 'مدري'


    
