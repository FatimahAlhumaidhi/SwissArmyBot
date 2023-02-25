import json, random, re, os

import tekore as tk
import numpy as np
from dotenv import load_dotenv

load_dotenv()

class spotify(object):
    def __init__(self):
        spotify_client_id = os.getenv("SPOTIFY_CLIENT_ID")
        spotify_secret_key = os.getenv("SPOTIFY_SECRET_KEY")
        
        token = tk.request_client_token(spotify_client_id, spotify_secret_key)
        self.spotify = tk.Spotify(token)
        self.genres = self.spotify.recommendation_genre_seeds()

    
    def recommend(self, genres, limit = 100):

        response = self.spotify.recommendations(genres = genres, limit = limit)
        recconmendations = json.loads(response.json())
        songList = self.prettify(recconmendations, genres)

        return songList


    def randomSong(self):
        genre = random.choice(self.genres)
        return self.recommend([genre], limit=1)[0]


    def prettify(self, songs, genres):
        songList = []
        for track in songs.get('tracks', []):
            song = {}
            song['name'] = track['name']
            song['url'] = track['external_urls'].get('spotify', 'None')
            song['artists'] = []
            for artist in track['artists']:
                song['artists'].append(artist['name'])
            respond = "NAME:\n" + song['name'] + '\n'
            respond = respond + 'GENRE:' + genres[0] + '\n'
            respond = respond + 'URL:\n' + song['url'] + '\n'
            respond = respond + 'ARTISTS:\n' + str(song['artists'])
            songList.append(respond)
        return songList



class spellCheck(object):
    def __init__(self, dir=''):
        with open(dir, 'r') as file:
            text = file.read()
        
        text = text.lower()
        self.vocab = set(re.findall('^[\u0621-\u064A]+$',text))

    def spell(self, word):
        if word in self.vocab:
            return word
        
        suggestions = list((word in self.vocab and word) or
                    (self.singleEdits(word).intersection(self.vocab)) or (self.doubleEdits(word).intersection(self.vocab)))[:5]
        
        minimum = float('inf')
        sugg = ''
        for suggestion in suggestions:
            distance = self.levenshtein_distance(word, suggestion)
            if distance < minimum:
                minimum = distance
                sugg = suggestion
        return sugg if sugg else word


    def levenshtein_distance(self, source, target, ins_cost = 1, del_cost = 2, rep_cost = 1):

        m = len(source)
        n = len(target)

        D = np.zeros((m+1, n+1), dtype=int)
        
        
        for row in range(1,m+1): 
            D[row,0] = D[row-1,0] + del_cost
            
        for col in range(1,n+1): 
            D[0,col] = D[0,col-1] + ins_cost
            
        for row in range(1,m+1):
            
            for col in range(1,n+1):
                
                r_cost = rep_cost
                
                if source[row-1] == target[col-1]:
                    r_cost = 0
                    
                D[row,col] = min(D[row-1, col] + del_cost, D[row, col-1] + ins_cost, D[row-1, col-1] + r_cost)
                
        med = D[m, n]
        
        return med


    def singleEdits(self, word): 
        
        splits = [(word[:i], word[i:]) for i in range(len(word))]
        # switchs = [L[:-1]+R[0]+L[-1]+R[1:] for L, R in splits if R and L]
        deletes = [L+R[1:] for L, R in splits if R]
        LETTERS = u'ابتةثجحخدذرزسشصضطظعغفقكلمنهويءآأؤإئى'
        replacements = list()
        for L, R in splits:
            if R:
                for letter in LETTERS:
                    if L+letter+R[1:] != word:
                        replacements.append(L+letter+R[1:])
        replace_set = set(replacements)
        replacements = sorted(list(replace_set))
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if R]
        inserts = [L + letter + R for L, R in splits for letter in LETTERS]

        singleEdit = set()
        singleEdit.update(deletes + replacements + inserts + transposes)

        return singleEdit

    def doubleEdits(self, word): 

        singleEdit = self.singleEdits(word)
        doubleEdit = [self.singleEdits(edit) for edit in singleEdit if edit]
        doubleEdit = set(doubleEdit)

        return doubleEdit



class grammerCheck(object):
    pass



    
