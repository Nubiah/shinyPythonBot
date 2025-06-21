# Importation des bibliothèques nécessaires
import pyautogui
import numpy as np
import cv2
from PIL import ImageGrab
import time
import win32gui
import win32con
import threading
import mss
import ctypes
import win32api
import win32process

# Variables globales
POKEMON_AREA = (327, 242, 475, 376)  # Zone de capture du sprite du Pokémon
LOAD_DELAY = 0.5
POST_INPUT_DELAY = 0.2  # Temps pour laisser apparaître le Pokémon
WINDOW_TITLE = "mGBA - 0.10.5"  # Partie du titre de la fenêtre mGBA

# Envoi de touches sans focus via PostMessage
MAP_KEYS = {
    'Z': 0x5A,
    'X': 0x58,
    'ENTER': 0x0D,
    'UP': 0x26,
    'F1': 0x70,
    'TAB': 0x09,
    'R': 0x52
}

# Fonctions utilitaires
def find_all_mgba_windows(title_keyword):
    """Renvoie une liste de HWND pour toutes les fenêtres dont le titre contient title_keyword."""
    windows = []

    def enumHandler(hwnd, lParam):
        if win32gui.IsWindowVisible(hwnd):
            window_title = win32gui.GetWindowText(hwnd)
            if title_keyword in window_title:
                windows.append(hwnd)

    win32gui.EnumWindows(enumHandler, None)
    if not windows:
        raise Exception(f"Aucune fenêtre contenant '{title_keyword}' n'a été trouvée.")
    return windows

def send_key(key):
    """Envoie une touche via PostMessage à toutes les fenêtres correspondantes."""
    hwnds = find_all_mgba_windows(WINDOW_TITLE)
    for hwnd in hwnds:
        # Optionnel : Afficher le HWND pour le debug
        # print(f"[DEBUG] Envoi de la touche {key} à HWND: {hwnd}")
        win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, key, 0)
    time.sleep(0.3)
    for hwnd in hwnds:
        win32gui.PostMessage(hwnd, win32con.WM_KEYUP, key, 0)

def save_attempts(attempts):
    with open("attempts.txt", "w") as file:
        file.write(str(attempts))

def load_attempts():
    try:
        with open("attempts.txt", "r") as file:
            return int(file.read().strip())
    except FileNotFoundError:
        return 0  # Si le fichier n'existe pas encore, commence à 0

def take_screenshot():
    img = ImageGrab.grab(bbox=POKEMON_AREA)
    img_np = np.array(img)
    return cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)

def is_shiny(img):
    avg_color = img.mean(axis=(0, 1))
    r, g, b = avg_color
    print(f"[DEBUG] Couleur moyenne : R={r:.1f}, G={g:.1f}, B={b:.1f}")
    return (r < 100)

def load_savestate():
    send_key(MAP_KEYS['F1'])
    time.sleep(LOAD_DELAY)

def perform_input_sequence_fast():
    boost = 20
    print("[INFO] Envoi de la sequence...")
    send_key(MAP_KEYS['X'])
    time.sleep(1/boost)
    send_key(MAP_KEYS['X'])
    time.sleep(1/boost)
    send_key(MAP_KEYS['X'])
    time.sleep(1/boost)
    send_key(MAP_KEYS['X'])
    time.sleep(5/boost)
    send_key(MAP_KEYS['Z'])
    time.sleep(3/boost)
    send_key(MAP_KEYS['X'])
    time.sleep(4/boost)
    send_key(MAP_KEYS['ENTER'])
    time.sleep(1/boost)
    send_key(MAP_KEYS['UP'])
    time.sleep(1/boost)
    send_key(MAP_KEYS['UP'])
    time.sleep(1/boost)
    send_key(MAP_KEYS['X'])
    time.sleep(0.5/boost)
    send_key(MAP_KEYS['X'])
    time.sleep(0.5/boost)
    send_key(MAP_KEYS['X'])
    time.sleep(0.5/boost)

    print("[INFO] Attente du sprite du Pokémon...")
    time.sleep(POST_INPUT_DELAY)

def shiny_hunting_loop():
    print("[INFO] Début de la chasse dans 3 secondes, s'assurer que le jeu est actif...")
    time.sleep(3)

    attempts = load_attempts()  # Charger les tentatives précédentes
    print(f"[INFO] Nombre de resets : {attempts}")

    while True:
        attempts += 1
        print(f"\n[RESET #{attempts}]")
        save_attempts(attempts)  # Sauvegarder après chaque tentative
        load_savestate()
        # Envoi d'une touche supplémentaire (par exemple TAB) à toutes les fenêtres
        send_key(MAP_KEYS['TAB'])
        perform_input_sequence_fast()
        img = take_screenshot()

        if is_shiny(img):
            # Finaliser l'action en envoyant un signal de relâchement de touche par précaution
            send_key(MAP_KEYS['TAB'])
            print("[SUCCES] SHINY DÉTECTÉ !")
            pyautogui.alert("SHINY DÉTECTÉ !")
            break
        else:
            print("[INFO] Pas shiny. Nouvelle tentative...")

shiny_hunting_loop()