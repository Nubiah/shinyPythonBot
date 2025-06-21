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
import multiprocessing as mp

#Variables globales
POKEMON_AREA = (327, 242, 475, 376) # Zone de capture du sprite du Pokémon
LOAD_DELAY = 0.5
POST_INPUT_DELAY = 0.2  # Temps pour laisser apparaître le Pokémon
WINDOW_TITLE = "mGBA - 0.10.5"  # Titre de la fenêtre mGBA
window_titles, window_hwnd, window_threads = [], [], []

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

#Fonctions
def is_admin():
    return ctypes.windll.shell32.IsUserAnAdmin()

if not is_admin():
    print("[ERROR] Administrator mode required.")
    exit()

def find_mgba_window(title):
    hwnd = win32gui.FindWindow(None, title)
    if hwnd == 0:
        raise Exception(f"Fenêtre '{title}' introuvable.")
    return hwnd

def rename_mgba_windows():
    base_title = "mGBA -"
    window_titles = []
    window_hwnd = []
    window_threads = []

    def enum_handler(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if base_title in title:
                new_title = f"mGBA - {len(window_titles)+1}"
                win32gui.SetWindowText(hwnd, new_title)
                window_titles.append(new_title)
                window_hwnd.append(hwnd)
                window_threads.append(win32process.GetWindowThreadProcessId(hwnd)[0])
                print(f"[INFO] Nouveau nom : {title} -> {new_title}")

    win32gui.EnumWindows(enum_handler, None)
    return window_titles, window_hwnd, window_threads

def send_key(title, key):
    hwnd = find_mgba_window(title)
    #print(f"[DEBUG] Envoi de la touche {key} sur '{title}' (HWND: {hwnd})")
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
    print(f"[DEBUG] Couleur moyenne : R={r:.1f}, G={g:.1f}, B={b:.1f}")
    saveColor(r,g,b)
    return (r < 100)

def perform_input_sequence_fast(title): #Avec Boost
    boost = 20
    print("[INFO] Envoi de la sequence...")
    send_key(title, MAP_KEYS['X'])
    time.sleep(1/boost)
    send_key(title, MAP_KEYS['X'])
    time.sleep(1/boost)
    send_key(title, MAP_KEYS['X'])
    time.sleep(1/boost)
    send_key(title, MAP_KEYS['X'])
    time.sleep(5/boost)
    send_key(title, MAP_KEYS['Z'])
    time.sleep(3/boost)
    send_key(title, MAP_KEYS['X'])
    time.sleep(4/boost)
    send_key(title, MAP_KEYS['ENTER'])
    time.sleep(1/boost)
    send_key(title, MAP_KEYS['UP'])
    time.sleep(1/boost)
    send_key(title, MAP_KEYS['UP'])
    time.sleep(1/boost)
    send_key(title, MAP_KEYS['X'])
    time.sleep(0.5/boost)
    send_key(title, MAP_KEYS['X'])
    time.sleep(0.5/boost)
    send_key(title, MAP_KEYS['X'])
    time.sleep(0.5/boost)

    print("[INFO] Attente du sprite du Pokemon...")
    time.sleep(POST_INPUT_DELAY)

def load_savestate(hwnd):
    print(f"[INFO] Focus sur la fenêtre : {hwnd} - Titre : {win32gui.GetWindowText(hwnd)}")
    win32gui.SetForegroundWindow(hwnd)
    send_key(win32gui.GetWindowText(hwnd), MAP_KEYS['F1'])
    win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, MAP_KEYS['TAB'], 0)
    time.sleep(1)

def executeInput(hwnd):
    print(f"[INFO] Exécution de la séquence d'input pour la fenêtre : {hwnd} - Titre : {win32gui.GetWindowText(hwnd)}")
    perform_input_sequence_fast(win32gui.GetWindowText(hwnd))
    time.sleep(1)

def shiny_hunting_loop():
    print("[INFO] Debut de la shasse dans 3 secondes, s'assurer que le jeu est en focus...")
    time.sleep(3)

    attempts = load_attempts()  # Charger les tentatives précédentes
    print(f"[INFO] Nombre de reset : {attempts}")

    while True:
        attempts += 1
        print(f"\n[RESET #{attempts}]")
        #save_attempts(attempts)  # Sauvegarder après chaque tentative

        if __name__ == "__main__":
            for hwnd in window_hwnd:
                print("Test 1")
                process_load_savestate = mp.Process(target=load_savestate, args=(hwnd,), daemon=True)
                process_execute_input = mp.Process(target=executeInput, args=(hwnd,), daemon=True)

                process_load_savestate.start()
                print("Démarrage Load Savestate")
                process_execute_input.start()
                print("Démarrage Execute Input")

                process_load_savestate.join()
                process_execute_input.join()

                time.sleep(2)

        img = take_screenshot()

        if is_shiny(img):
            win32gui.PostMessage(find_mgba_window(WINDOW_TITLE), win32con.WM_KEYUP, MAP_KEYS['TAB'], 0)
            print("[SUCCES] SHINY DETECTE !")
            pyautogui.alert("SHINY DETECTE !")
            break
        else:
            print("[INFO] Pas shiny. Nouvelle tentative...")

window_titles, window_hwnd, window_threads = rename_mgba_windows()
shiny_hunting_loop()

def debugMode():
    print("[DEBUG] Mode debug activé.")    
    print("[INFO] Debut de la shasse dans 3 secondes, s'assurer que le jeu est en focus...")
    time.sleep(3)
    send_key(WINDOW_TITLE, MAP_KEYS['F1'])  # Reset pour tester la fonction
#debugMode()