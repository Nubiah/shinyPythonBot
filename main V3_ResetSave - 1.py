#Importation des bibliothèques nécessaires
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
import ctypes

#Variables globales
POKEMON_AREA = (327, 242, 475, 376) # Zone de capture du sprite du Pokémon
LOAD_DELAY = 4
POST_INPUT_DELAY = 0.2  # Temps pour laisser apparaître le Pokémon
WINDOW_TITLE = "mGBA - 1"  # Titre de la fenêtre mGBA
boost = 20
MODE_DEBUG = False


# Envoie de touches sans focus via SendInput
MAP_KEYS = {
    'Z': 0x5A,
    'X': 0x58,
    'ENTER': 0x0D,
    'UP': 0x26,
    'F1': 0x70,
    'TAB': 0x09,
    'R': 0x52
}

POKEMON_AREA2 = {
    'mGBA - 1': (327, 242, 475, 376),
    'mGBA - 2': (1610, 242, 1753, 376),
    'mGBA - 3': (327, 938, 475, 1076),
    'mGBA - 4': (1605, 935, 1756, 1075),
}

#Fonctions
def find_mgba_window(title):
    hwnd = win32gui.FindWindow(None, title)
    if hwnd == 0:
        raise Exception(f"Fenêtre '{title}' introuvable.")
    return hwnd

def getFocus(title):
    hwnd_target = find_mgba_window(title)
    if hwnd_target:
        win32gui.SetForegroundWindow(hwnd_target)
        if MODE_DEBUG:
            print("[INFO] Focus to process :", hwnd_target)
    else:
        print("[WARNING] Process not found.")

def send_key(title, key):
    hwnd = find_mgba_window(title)
    if MODE_DEBUG:
        print(f"[DEBUG] Envoi de la touche {key} sur '{title}' (HWND: {hwnd})")
    win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, key, 0)
    time.sleep(0.3)
    win32gui.PostMessage(hwnd, win32con.WM_KEYUP, key, 0)

def save_attempts(attempts):
    with open("attempts.txt", "w") as file:
        file.write(str(attempts))

def saveColor(r,g,b):
    with open("color.txt", "a") as file:
        file.write(f"R={r:.1f}, G={g:.1f}, B={b:.1f}\n")

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
    print(f"[INFO] Couleur moyenne : R={r:.1f}, G={g:.1f}, B={b:.1f}")
    saveColor(r,g,b)
    return (r < 100)

def load_savestate():
    getFocus(WINDOW_TITLE)  # Mettre le focus sur la fenêtre mGBA
    time.sleep(1)
    send_key(WINDOW_TITLE, MAP_KEYS['R'])
    time.sleep(LOAD_DELAY/boost)  # Attendre que le jeu charge l'état sauvegardé

def perform_input_sequence_fast(): #Avec Boost
    print("[INFO] Envoi de la sequence...")
    send_key(WINDOW_TITLE, MAP_KEYS['X'])
    time.sleep(1/boost)
    send_key(WINDOW_TITLE, MAP_KEYS['X'])
    time.sleep(1/boost)
    send_key(WINDOW_TITLE, MAP_KEYS['X'])
    time.sleep(4/boost)
    send_key(WINDOW_TITLE, MAP_KEYS['X'])
    time.sleep(2/boost)
    #send_key(WINDOW_TITLE, MAP_KEYS['X'])
    #time.sleep(2/boost)
    #send_key(WINDOW_TITLE, MAP_KEYS['X'])
    #time.sleep(2/boost)
    if MODE_DEBUG:
        print("[INFO] Début face à la pokéball...")
    send_key(WINDOW_TITLE, MAP_KEYS['X'])
    time.sleep(1/boost)
    send_key(WINDOW_TITLE, MAP_KEYS['X'])
    time.sleep(1/boost)
    send_key(WINDOW_TITLE, MAP_KEYS['X'])
    time.sleep(1/boost)
    send_key(WINDOW_TITLE, MAP_KEYS['X'])
    time.sleep(5/boost)
    send_key(WINDOW_TITLE, MAP_KEYS['Z'])
    time.sleep(3/boost)
    send_key(WINDOW_TITLE, MAP_KEYS['X'])
    time.sleep(4/boost)
    send_key(WINDOW_TITLE, MAP_KEYS['ENTER'])
    time.sleep(1/boost)
    #send_key(WINDOW_TITLE, MAP_KEYS['UP'])
    #time.sleep(1/boost)
    #send_key(WINDOW_TITLE, MAP_KEYS['UP'])
    #time.sleep(1/boost)
    send_key(WINDOW_TITLE, MAP_KEYS['X'])
    time.sleep(0.5/boost)
    send_key(WINDOW_TITLE, MAP_KEYS['X'])
    time.sleep(0.5/boost)
    send_key(WINDOW_TITLE, MAP_KEYS['X'])
    time.sleep(0.5/boost)

    print("[INFO] Attente du sprite du Pokemon...")
    time.sleep(POST_INPUT_DELAY)

def shiny_hunting_loop():
    print("[INFO] Debut de la shasse dans 3 secondes, attention au focus automatique...")
    time.sleep(3)

    attempts = load_attempts()  # Charger les tentatives précédentes
    print(f"[INFO] Nombre de reset : {attempts}")

    while True:
        attempts += 1
        print(f"\n[RESET #{attempts}]")
        if MODE_DEBUG==False:
            save_attempts(attempts)  # Sauvegarder après chaque tentative
        win32gui.PostMessage(find_mgba_window(WINDOW_TITLE), win32con.WM_KEYDOWN, MAP_KEYS['TAB'], 0)
        load_savestate()
        perform_input_sequence_fast()
        img = take_screenshot()

        if is_shiny(img):
            win32gui.PostMessage(find_mgba_window(WINDOW_TITLE), win32con.WM_KEYUP, MAP_KEYS['TAB'], 0)
            print("[SUCCES] SHINY DETECTE !")
            pyautogui.alert("SHINY DETECTE !")
            break
        else:
            print("[INFO] Pas shiny. Nouvelle tentative...")

shiny_hunting_loop()