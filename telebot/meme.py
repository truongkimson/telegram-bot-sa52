import requests
import json

def get_random_meme():
    r = requests.get('https://meme-api.herokuapp.com/gimme')
    parsed = json.loads(r.text)
    return(parsed['url'])