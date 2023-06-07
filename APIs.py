import requests, time
import urllib.parse
from typing import List
from PIL import Image 
import urllib.request
import io, os, random, base64
from bs4 import BeautifulSoup
import csv, re
from difflib import get_close_matches

from dotenv import load_dotenv

load_dotenv()

def getContact(number:str) -> str:
    numberbook_url = 'https://rdod.live/contacts_api/api.php'
    url = numberbook_url+"?getName=true&phone="+number
    try:
        response = requests.get(url)
        data = response.json()
        names = []
        if data['response'] == 'success':
           for elem in data['data']:
               names.append(elem['name'])
           names = set(names)
           return '\n'.join(names)
        else:
            return 'could not find any record for this number'
    except:
        return 'sorry, something went wrong.'


def lookUp(word:str):
    try:
        userAgentList = ['Mozilla/5.0', 'Safari/537.36', 'Chrome/67.0.3396.99',] # 'iexplore/11.0.9600.19080', 'Trident/7.0', 'SeaMonkey/2.40', 'Wyzo/3.6.4.1', 'OPR/54.0.2952.64'
        user_agent = random.choice(userAgentList)

        url = 'https://www.almaany.com/ar/dict/ar-ar/{}/'.format(urllib.parse.quote_plus(word))
        headers = {'User-Agent': user_agent}

        request = urllib.request.Request(url, headers=headers)
        handle = urllib.request.urlopen(request)

        html = handle.read().decode(handle.headers.get_content_charset())
        soup = BeautifulSoup(html, 'html.parser')

        result = soup.find_all(class_='meaning-results')
        if result is None:
            try:
                result = soup.select('html > body > section > div > div:nth-of-type(2) > div:nth-of-type(1) > div:nth-of-type(1) > p')
                return result[0].text
            except:
                return 'مدري'

        myList = []
        elems = result[-1].find_all('li')
        for elem in elems:
            defin = {}
            word = elem.find('span')
            meaning = elem.find('ul')
            dictionary = elem.find('p')
            if not all([word, meaning, dictionary]):
                continue
            defin['word'] = word.text.replace('\n', '')
            defin['meaning'] = meaning.text.replace('\n', '')
            defin['dictionary'] = dictionary.text.replace('\n', '')
            myList.append(defin)

        return myList

    except:
        return 'مدري'

def get_access_token(credentials):
    url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': 'Basic ' + credentials,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'client_credentials'
    }
    try:
        response = requests.post(url, headers=headers, data=data)
        response_data = response.json()
        return response_data['access_token']
    except:
        return ''

def get_available_genre_seeds(access_token):
    url = 'https://api.spotify.com/v1/recommendations/available-genre-seeds'
    headers = {
        'Authorization': 'Bearer ' + access_token
    }
    response = requests.get(url, headers=headers)
    return response.json()

def get_recommendations(access_token, seed_genres, limit):
    url = 'https://api.spotify.com/v1/recommendations'
    headers = {
        'Authorization': 'Bearer ' + access_token
    }
    params = {
        'seed_genres': seed_genres,
        'limit': limit
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        return response.json()
    except:
        return ''

def prettify(songs, genres):
    songList = []
    for track in songs.get('tracks'):
        song = {}
        song['name'] = track['name']
        song['url'] = track['external_urls'].get('spotify', 'None')
        song['artists'] = []
        for artist in track['artists']:
            song['artists'].append(artist['name'])
        response = "NAME:\n" + song['name'] + '\n'
        response = response + 'GENRE: ' + ', '.join(genres) + '\n'
        response = response + 'URL:\n' + song['url'] + '\n'
        response = response + 'ARTISTS:\n' + ', '.join(song['artists'])
        songList.append(response)
    return songList

def getRandomSong():
    spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID')
    spotify_secret_key = os.getenv('SPOTIFY_SECRET_KEY')

    credentials = base64.b64encode(
        (spotify_client_id + ':' + spotify_secret_key).encode('utf-8')
    ).decode('utf-8')

    try:
        access_token = get_access_token(credentials)
        genre_seeds = get_available_genre_seeds(access_token)
        random_genre = random.choice(genre_seeds['genres'])
        recommendations = get_recommendations(access_token, random_genre, 1)
        formatted_recommendations = prettify(recommendations, [random_genre])
        return '\n\n'.join(formatted_recommendations)
    except:
        return 'an error occurred'

    
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

def latestChapter(response):
    chapters = [(chapter['id'], 
                 float(chapter['attributes']['chapter']), 
                 chapter['attributes']['externalUrl']) 
                 for chapter in response.json()['data'] if chapter['attributes']['translatedLanguage'] == 'en']
    return max(chapters, key = lambda x : x[1])

def getChapter(MangaName:str) -> dict: 
    mangadex = "https://api.mangadex.org"
    try:
        response = requests.get(
            f"{mangadex}/manga",
            params={"title": MangaName}
        )
        if not response.ok:
            raise Exception('No manga found :(')

        def find_closest_title(MangaName, names):
            closest_string = None
            closest_distance = float('inf')

            for name in names:
                distance = levenshtein_distance(MangaName, name[1])
                if distance < closest_distance:
                    closest_distance = distance
                    closest_string = name

            return closest_string
        
        mangas = [(manga["id"], manga["attributes"]["title"]["en"]) for manga in response.json()["data"]]
        ID, TITLE = find_closest_title(MangaName, mangas)

        if not len(ID):
            raise Exception('No manga found :(')
        
        
        response = requests.get(f"{mangadex}/manga/{ID}/feed")

        if not response.ok:
            raise Exception('No manga found :(')
        
        latest = latestChapter(response)
        if not len(latest):
            raise Exception('No chapter found :(')
        
        
        response = requests.get(f"{mangadex}/at-home/server/{latest[0]}")
        if not response.ok:
            if latest[2] != '':
                raise Exception(f"could not find chapter, try reading it online: {latest[2]}")
            else:
                raise Exception('No chapter found :(')
        
        chapter = response.json()
        chapter_data = chapter['chapter']['data']

        imgs = []
        for chapter_pic in chapter_data:
            URL = f"https://uploads.mangadex.org/data/{chapter['chapter']['hash']}/{chapter_pic}"
            with urllib.request.urlopen(URL) as url:
                try:
                    f = io.BytesIO(url.read())
                    imgs.append(Image.open(f).convert('RGB'))
                except:
                    continue
            
        filename = f"{TITLE} ch.{str(int(latest[1]))}.pdf"
        pdf_data = io.BytesIO()

        imgs[0].save(
            pdf_data, "PDF", resolution=100.0, save_all=True, append_images=imgs[1:]
        )

        pdf_data.seek(0)

        return {'success':True, 'file':pdf_data, 'filename':filename, 'url': latest[2] if latest[2] else ':p'}
    
    except Exception as error:
        return {'success':False, 'Exception':str(error)}

def levenshtein_distance(source, target):
    m = len(source)
    n = len(target)

    if m == 0:
        return n
    if n == 0:
        return m

    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i

    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if source[i - 1] == target[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 2,
                dp[i][j - 1] + 2,
                dp[i - 1][j - 1] + cost
            )

    return dp[m][n]

def load_dictionary(dictionary_path='vocab_updated.csv'):
    arabic_dictionary = {}
    word_set = set()

    with open(dictionary_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            word = row['Word']
            count = int(row['Count'])
            arabic_dictionary.setdefault(len(word), {})[word] = count
            word_set.add(word)

    return arabic_dictionary, word_set

def get_word_suggestions(word, arabic_dictionary):
    suggestions = []
    max_count = -float('inf')
    min_distance = float('inf')
    word_length = len(word)

    for length in range(word_length - 1, word_length + 2):
        for dict_word, count in arabic_dictionary.get(length, {}).items():
            distance = levenshtein_distance(word, dict_word)
            if distance < min_distance:
                suggestions = [dict_word]
                min_distance = distance
                max_count = count
            elif distance == min_distance:
                if count > max_count:
                    suggestions = [dict_word]
                    max_count = count
                elif count == max_count:
                    suggestions.append(dict_word)

    return suggestions

def preprocess_text(text):
    arabic_text = re.sub(r'[^\u0600-\u06FF\s]', '', text)
    
    tashkeel_mapping = {
    '\u064B': '',
    '\u064C': '',
    '\u064D': '',
    '\u064E': '',
    '\u064F': '',
    '\u0650': '',
    '\u0651': '',
    '\u0652': '',
    '\u0653': '',
    '\u061F': '',
    '\u0640': '',
    }

    discretized_text = ''.join(tashkeel_mapping.get(char, char) for char in arabic_text)
    discretized_text = re.sub(r'\s+', ' ', discretized_text)

    return discretized_text


def correct_spelling(text):
    arabic_dictionary, word_set = load_dictionary()

    text = preprocess_text(text)
    if len(text) < 2:
        return 'كيف الحال'
    
    words = text.split()
    corrected_text = []

    for word in words:
        if word not in word_set:
            suggestions = get_word_suggestions(word, arabic_dictionary)
            if suggestions:
                # selected_word = min(suggestions, key=lambda x: (arabic_dictionary[len(word)][x], levenshtein_distance(word, x)))
                corrected_text.append(suggestions[0])
            else:
                corrected_text.append(word)
        else:
            corrected_text.append(word)

    return ' '.join(corrected_text)

