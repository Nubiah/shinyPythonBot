import subprocess
import socket
import time
import os
import requests
from config import *

def launch_emulator():
    subprocess.Popen([
        "mgba",
        "--script", "check_shiny.lua",
        "--savestate", "bulbizarre.st0",  # nom du savestate préparé
        "roms/Pokemon_LeafGreen.gba"
    ])

def listen_for_shiny():
    s = socket.socket()
    s.bind(("localhost", 5000))
    s.listen(1)
    conn, _ = s.accept()
    print("Connexion avec Lua établie !")

    while True:
        data = conn.recv(1024)
        if b"shiny" in data:
            print("✨ SHINY détecté ✨")
            notify_discord()
            return True
    return False

def notify_discord():
    requests.post(WEBHOOK_URL, json={"content": "✨ **Bulbizarre shiny trouvé !** 🌿🎉"})

def main():
    reset_count = 0
    while True:
        reset_count += 1
        print(f"Essai #{reset_count}")
        launch_emulator()
        time.sleep(2)
        found = listen_for_shiny()
        if found:
            break
        else:
            # ferme l'émulateur pour le relancer
            os.system("pkill mgba")
            time.sleep(1)

if __name__ == "__main__":
    main()
