import requests
import urllib.parse
import json
import os
import time
from typing import List
from PIL import Image 
import urllib.request
import io

from selenium import webdriver
from selenium.webdriver.common.by import By
from dotenv import load_dotenv

load_dotenv()

def getContact(number:str) -> str:
    numberbook_url = 'https://rdod.live/contacts_api/api.php'
    url = numberbook_url+"?getName=true&phone="+number
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


    
def get_animes_current_season() -> List[str]:
    jikan_url = "https://api.jikan.moe/v4/seasons/now?page={page_number}"
    response = requests.get(jikan_url.format(page_number=1))
    if response.status_code != 200:
        return "Please try again later"
    
    all_current_season_anime = response.json()
    if all_current_season_anime["pagination"]["items"]["count"] <= 0:
        return "No animes this season"

    total_animes_current_season = all_current_season_anime['pagination']['items']['total']
    telegram_message = f"There is {total_animes_current_season} this season: \n"
    telegram_messages = []
    anime_number = 1
    while True:
        for anime in all_current_season_anime["data"]:
            title = anime["title"] if anime["title"] else "مدري"
            score = anime["score"] if anime["score"] else "مدري"
            number_of_episodes = anime["episodes"] if anime["episodes"] else "مدري"
            status = anime["status"] if anime["status"] else "مدري"
            broadcast_info = anime["broadcast"] if anime["broadcast"] else None
            broadcast_day = "مدري"
            if broadcast_info is not None:
                broadcast_day = broadcast_info["day"] if broadcast_info["day"] else "مدري"
            all_generes = anime["genres"] + anime["themes"] + anime["demographics"]
            all_generes = ", ".join([genre["name"] for genre in all_generes])
            trailer_info =  anime["trailer"] if anime["trailer"] else None
            trailer = "مدري"
            if trailer_info is not None:
                trailer = trailer_info["url"] if trailer_info["url"] else "مدري"

            telegram_message = telegram_message + f"{anime_number}- Title: {title}\n\t Number of episodes: {number_of_episodes}\n\t Rating: {score}\n\t Status: {status}\n\t Broadcast day: {broadcast_day}\n\t Genres: {all_generes}\n\t Trailer: {trailer}\n\n"
            if anime_number % 10 == 0 or anime_number == total_animes_current_season:
                telegram_messages.append(telegram_message)
                telegram_message = ""
            anime_number = anime_number + 1

        if not all_current_season_anime["pagination"]["has_next_page"]:
            break

        response = requests.get(jikan_url.format(page_number=all_current_season_anime["pagination"]["current_page"] + 1))
        all_current_season_anime = []
        if response.status_code == 200:
            all_current_season_anime = response.json()

        time.sleep(3)

    return telegram_messages

# def getChaptersIDs(MangaName:str) -> tuple[int, List[str]]:
#     mangadex = "https://api.mangadex.org"
#     try:
#         response = requests.get(
#             f"{mangadex}/manga",
#             params={"title": MangaName}
#         )
#         if not response.ok:
#             raise Exception('Manga not found')

#         IDs = [manga["id"] for manga in response.json()["data"]]
#         response = requests.get(f"{mangadex}/manga/{IDs[0]}/feed")

#         if not response.ok:
#             raise Exception('Manga not found')
        
#         ChaptersIDs = [chapter["id"] for chapter in response.json()["data"]]
#         return len(ChaptersIDs), ChaptersIDs
#     except Exception as error:
#         return 0, [repr(error)]

def getChapter(MangaName:str) -> dict: 
    mangadex = "https://api.mangadex.org"
    try:
        response = requests.get(
            f"{mangadex}/manga",
            params={"title": MangaName}
        )
        if not response.ok:
            raise Exception('Manga not found')

        IDs = [manga["id"] for manga in response.json()["data"]]
        response = requests.get(f"{mangadex}/manga/{IDs[0]}/feed")

        if not response.ok:
            raise Exception('Manga not found')
        
        # ChaptersIDs = [chapter["id"] for chapter in response.json()["data"]]
        latest = response.json()['data'][-1]['id'] 
        response = requests.get(f"{mangadex}/at-home/server/{latest}")
        if not response.ok:
            raise Exception('Chapter not found')
        
        chapter = response.json()
        chapter_data = chapter['chapter']['data']

        imgs = []
        for chapter_pic in chapter_data:
            URL = f"https://uploads.mangadex.org/data/{chapter['chapter']['hash']}/{chapter_pic}"
            with urllib.request.urlopen(URL) as url:
                try:
                    f = io.BytesIO(url.read())
                    imgs.append(Image.open(f))
                except:
                    continue
            
        imgs[0].save(
            f"{MangaName}.pdf", "PDF" ,resolution=100.0, save_all=True, append_images=imgs[1:]
        )
        return {'success':True, 'file':f"{MangaName}.pdf"}
    except Exception as error:
        return {'success':False, 'Exception':repr(error)}
