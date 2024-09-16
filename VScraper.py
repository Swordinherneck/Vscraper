import requests
import json
import os
import time
from fake_useragent import UserAgent
import re
import uuid
from colorama import init, Fore, Style
import fade

def clean_filename(hostname):
    return re.sub(r'^([0-9])', '', re.sub(r'[/:"*?<>|]', '', hostname)).replace('^0','').replace('^1','').replace('^2','').replace('^3','').replace('^4','').replace('^5','').replace('^6','').replace('^7','').replace('^8','').replace('^9','')

def check_if_player_exists(filename, player_data, added_players):
    if not os.path.exists(filename):
        return False

    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        try:
            existing_player = json.loads(line)
        except json.JSONDecodeError:
            continue

        if existing_player.get('fivem') == player_data.get('fivem'):
            fields_to_check = ['steam', 'name', 'live', 'xbl', 'license', 'license2', 'name']
            fields_match = True

            for field in fields_to_check:
                existing_field_value = existing_player.get(field)
                new_field_value = player_data.get(field)

                if (existing_field_value is not None or new_field_value is not None) and existing_field_value != new_field_value:
                    fields_match = False
                    break

            if fields_match:
                return True

    if player_data['identifiers'] in added_players:
        return True

    return False

def get_server_info(server_id, proxy, added_players):
    url = f'https://servers-frontend.fivem.net/api/servers/single/{server_id}'
    user_agent = UserAgent()
    headers = {
        'User-Agent': user_agent.random,
        'method': 'GET'
    }

    try:
        response = requests.get(url, headers=headers, proxies=proxy)

        if response.status_code == 200:
            server_data = response.json()
            hostname = clean_filename(str(uuid.uuid4()))

            try:
                hostname = clean_filename(server_data['Data']['hostname'])[:100]
            except Exception as err:
                print(err)

            try:
                if len(server_data['Data']['vars']['sv_projectName']) >= 10:
                    hostname = clean_filename(server_data['Data']['vars']['sv_projectName'])[:100]
            except:
                pass

            if not os.path.exists('scrap'):
                os.makedirs('scrap')

            filename = f'scrap/{hostname}.txt'
            players_added_count = 0  # Nouvelle variable pour le compteur de joueurs ajoutés

            for player in server_data['Data']['players']:
                player_data = json.dumps(player, ensure_ascii=False)
                player_identifiers = player['identifiers']

                if not check_if_player_exists(filename, player, added_players):
                    with open(filename, 'a', encoding='utf-8') as file:
                        file.write(player_data)
                        file.write('\n')

                    print(Fore.GREEN + f'[NEW]' + Style.RESET_ALL + f' {player["name"]} a été trouvé ✅')
                    added_players.append(player_identifiers)
                    players_added_count += 1  # Incrémenter le compteur

            print(Fore.CYAN + f'[INFO]' + Style.RESET_ALL + f' Project SwordInHerNeck')        
            print(Fore.CYAN + f'[INFO]' + Style.RESET_ALL + f' Nombre de joueurs ajoutés dans {filename}: {players_added_count}')
            print(Fore.CYAN + '[INFO]' + Style.RESET_ALL + f' Nombre total de joueurs ajoutés : {len(added_players)}\n')

        else:
            print(Fore.RED + f'\n[ERROR]' + Style.RESET_ALL + f" Message d'erreur 🚫({server_id}: {response.status_code})\n")

    except Exception as e:
        print(f'Erreur: {str(e)}')

def process_servers(server_ids, proxies, added_players):
    for server_id, proxy in zip(server_ids, proxies):
        get_server_info(server_id, proxy, added_players)
        time.sleep(0.5)

def main():
    with open('serveur.txt', 'r') as server_file:
        french_server_ids = [line.strip() for line in server_file.readlines()]

    with open('proxy.txt', 'r') as proxy_file:
        proxy_list = [{'http': f'socks5://{proxy.strip()}'} for proxy in proxy_file]

    proxy_index = 0
    total_proxies = len(proxy_list)
    added_players = []

    while True:
        half_length = len(french_server_ids) // 2
        first_half = french_server_ids[:half_length]
        second_half = french_server_ids[half_length:]

        process_servers(first_half, proxy_list, added_players)
        process_servers(second_half, proxy_list, added_players)

        print(Fore.MAGENTA + "\n[TIME]" + Style.RESET_ALL + " merci d'attendre un peu ! (10sec) ...\n")
        time.sleep(10)

def startup():
    os.system("cls")
    banner = '''

 (                                                                                           
 )\ )                                                                                     )  
(()/(     (       )           (   (         (   (     )           (   (        (   (   ( /(  
 /(_)) (  )(   ( /(  `  )    ))\  )(        )\  )\ ( /(  `  )    ))\  )(       )\  )\  )(_)) 
(_))   )\(()\  )(_)) /(/(   /((_)(()\      ((_)((_))(_)) /(/(   /((_)(()\     ((_)((_)((_)   
/ __| ((_)((_)((_)_ ((_)_\ (_))   ((_)     \ \ / /((_)_ ((_)_\ (_))   ((_)    \ \ / / |_  )  
\__ \/ _|| '_|/ _` || '_ \)/ -_) | '_|      \ V / / _` || '_ \)/ -_) | '_|     \ V /   / /      | swordInHerNeck
|___/\__||_|  \__,_|| .__/ \___| |_|         \_/  \__,_|| .__/ \___| |_|        \_/   /___|  
                    |_|                                 |_|                                  

'''
    faded_text = fade.greenblue(banner)
    print(faded_text)

    time.sleep(5)
    main()

startup()