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
import main

#Variables globales
window_titles = []
window_hwnd = []
window_threads = []

#Fonction

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

window_titles, window_hwnd, window_threads = rename_mgba_windows()
print("[INFO] Noms des fenêtres mGBA :", window_titles)
print("[INFO] Handles des fenêtres mGBA :", window_hwnd)
print("[INFO] Threads des fenêtres mGBA :", window_threads)

def testFocus():
    for each in window_hwnd:
        print(f"[INFO] Focus sur la fenêtre : {each} - Titre : {win32gui.GetWindowText(each)}")
        win32gui.SetForegroundWindow(each)
        main.send_key(win32gui.GetWindowText(each), main.MAP_KEYS['F1'])
        time.sleep(2)
    
testFocus()