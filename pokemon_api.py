import requests

def get_pokemon_cards(api_key, query=''):
    headers = {"X-Api-Key": api_key}
    url = f"https://api.pokemontcg.io/v2/cards?q={query}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def get_pokemon_card_by_id(api_key, card_id):
    url = f"https://api.pokemontcg.io/v2/cards/{card_id}"
    headers = {'X-Api-Key': api_key}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()['data']
    else:
        print("Failed to fetch data:", response.status_code, response.text)
        return None