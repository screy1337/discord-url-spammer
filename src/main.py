import requests
import time
import json
import datetime
from concurrent.futures import ThreadPoolExecutor
from colorama import Fore, init as colorama_init
import os

import sys
if os.name == 'nt':
    import ctypes

colorama_init()

config_line = os.path.join('7k', 'settings.json')

config = json.load(open(config_line, encoding="utf-8"))

def clear(): 
    os.system('cls' if os.name =='nt' else 'clear')

def print01(text):
    for c in text:
        sys.stdout.write(c)
        sys.stdout.flush()
        time.sleep(0.020)

clear()
print01(Fore.RED + "Realize the Facts" + Fore.RESET + "\n")
time.sleep(1)
print01(Fore.CYAN + "screy#1337" + Fore.RESET + "\n")
time.sleep(3)

clear()

token_line = os.path.join('7k', 'tokens.txt')
tokens = open(token_line, 'r').read().replace('\r', '').split('\n')

with open(config_line, 'r') as config_file:
    config_data = json.load(config_file)

webhook_url = config_data['webhook_url']
delay = config_data['delay']
data = config_data['data']
snipe_enabled = config_data.get('snipe_enabled', False)

start_time = datetime.datetime.strptime(config_data['date'], '%Y-%m-%dT%H:%M:%S')

token_position = 0
snipped = False
reqs = 0
num_symbols = len(tokens)
num_servers = len(data)

max_threads = 10 

def webhook(value):
    data = {
        "content": value
    }
    requests.post(webhook_url, json=data)

def snipe(value):
    global reqs
    key, value = value
    url = f"https://canary.discord.com/api/v7/guilds/{value[1]}/vanity-url"
    headers = {
        "Accept": "*/*",
        "Authorization": get_token(),
        "Content-Type": "application/json"
    }
    try:
        payload = {
            "code": value[0]
        }
        response = requests.patch(url, headers=headers, data=json.dumps(payload), timeout=10)
        json_response = response.json()

        if json_response.get("code") == 50001:
            print(f"{Fore.MAGENTA}[{get_time()}] {Fore.RESET} || {Fore.RED}[PERMİSSİONS]")
            return
        
        if json_response.get("errors") and json_response["errors"].get("code") and json_response["errors"]["code"]["_errors"][0]["code"]:
            error_message = json_response["errors"]["code"]["_errors"][0]["message"]
            print(f"{Fore.MAGENTA}[{get_time()}]  || {Fore.RED}[ERROR MESSAGE: {error_message}]")
            return
        
        if json_response.get("code") == 0:
            print(f"{Fore.MAGENTA}[{get_time()}] {Fore.RESET} || {Fore.RED}[INVALID TOKEN]")
            return

        if json_response.get("code") == value[0]:
            print("[{}] screy#1337 [{}]".format(get_time(), value[0]))
            webhook("https://discord.gg/{}\n\n`{}`\n||https://open.spotify.com/track/4LPfP8XzAp7OESNP28AUFB?si=3dc2c7c12c2e49d7||\n@everyone".format(value[0], {reqs}))
            if snipe_enabled:
                os._exit(0)
        else:
            if "retry_after" in json_response:
                print(f"{Fore.MAGENTA}[{get_time()}]{Fore.RESET} {Fore.RED} Retry after: [{get_cooldown(time.time() + json_response['retry_after'])}] {Fore.RESET}-->{Fore.RED} ID Server: [{value[1]}]")

            elif json_response.get("code") == 50020:
                reqs += 1
                print(f"{Fore.MAGENTA}[{get_time()}] {Fore.RESET}  {Fore.CYAN}Vanity: {Fore.CYAN}[{value[0]}] {Fore.RESET}-->{Fore.CYAN} Server: {Fore.CYAN}[{value[1]}]{Fore.RESET}")

                elapsed_time = time.time() - start_time.timestamp()
                speed = reqs / elapsed_time

                ctypes.windll.kernel32.SetConsoleTitleW(f"Vanity-URL Spammer  screy#1337 --> Token: [{num_symbols}] --> Server: [{num_servers}]  --> Speed: {speed:.2f} requests/sec --> Time Left: {get_cooldown(time.time() + json_response['retry_after'])}")

    except Exception as e:
        pass

def get_cooldown(cooldown):
    time_left = int(cooldown - time.time())
    hours, remainder = divmod(time_left, 3600)
    minutes, seconds = divmod(remainder, 60)
    return "{:02d}H:{:02d}M".format(hours, minutes)

def get_token():
    global token_position
    if token_position > len(tokens) - 1:
        token_position = 0
    token = tokens[token_position]
    token_position += 1
    return token

def get_time():
    return datetime.datetime.now().strftime("%H:%M")

def wait_until_start():
    now = datetime.datetime.now()
    while now < start_time:
        print(f"{Fore.RED}Waiting until {start_time.strftime('%Y-%m-%d %H:%M:%S')}.")
        time.sleep(60)  
        now = datetime.datetime.now()

wait_until_start()

print(f"{Fore.CYAN}[{get_time()}] {Fore.RESET} --> {Fore.CYAN} Speed: [{delay}ms]\n")
time.sleep(2)

with ThreadPoolExecutor(max_workers=max_threads) as executor:
    try:
        while not snipped:
            executor.map(snipe, data.items())
            time.sleep(delay)
    except KeyboardInterrupt:
        pass
