import requests

def get_pokemon_cards(api_key, query=''):
    headers = {"X-Api-Key": api_key}
    url = f"https://api.pokemontcg.io/v2/cards?q={query}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None
