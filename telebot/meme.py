import requests

def get_random_meme():
    r = requests.get('https://meme-api.herokuapp.com/gimme')
    return(r.json()['url'])