import win32gui
import win32con
import threading
import time
import numpy as np
import cv2
import mss
import ctypes
import win32api

POKEMON_AREA = (253, 282, 398, 407)
LOAD_DELAY = 2.0
POST_INPUT_DELAY = 3.0

# Renommage automatique des fenetres mGBA
def rename_mgba_windows():
    base_title = "mGBA"
    window_titles = []

    def enum_handler(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if base_title in title:
                new_title = f"mGBA - {len(window_titles)+1}"
                win32gui.SetWindowText(hwnd, new_title)
                window_titles.append(new_title)
                print(f"[INFO] Nouveau nom : {title} -> {new_title}")

    win32gui.EnumWindows(enum_handler, None)
    return window_titles

# Envoie de touches sans focus via SendInput
MAP_KEYS = {
    'Z': 0x5A,
    'X': 0x58,
    'ENTER': win32con.VK_RETURN,
    'UP': win32con.VK_UP,
    'F1': win32con.VK_F1
}

def send_input_key(key):
    extra = ctypes.c_ulong(0)
    ii_ = ctypes.Union(
        [
            ("ki", ctypes.Structure(
                [
                    ("wVk", ctypes.c_ushort),
                    ("wScan", ctypes.c_ushort),
                    ("dwFlags", ctypes.c_ulong),
                    ("time", ctypes.c_ulong),
                    ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
                ]
            ))
        ]
    )

    class INPUT(ctypes.Structure):
        _fields_ = [("type", ctypes.c_ulong),
                    ("union", ii_)]

    def make_input(vk, flags):
        return INPUT(
            type=1,
            union=ii_.from_buffer_copy(
                (ctypes.c_ushort * 5)(vk, 0, flags, 0, ctypes.cast(ctypes.pointer(extra), ctypes.POINTER(ctypes.c_ulong)))
            )
        )

    inputs = [make_input(key, 0), make_input(key, win32con.KEYEVENTF_KEYUP)]
    ctypes.windll.user32.SendInput(len(inputs), ctypes.byref(inputs[0]), ctypes.sizeof(INPUT))

# Capture fiable avec MSS
def get_window_rect(hwnd):
    return win32gui.GetWindowRect(hwnd)

def take_screenshot(hwnd):
    rect = get_window_rect(hwnd)
    x1, y1, x2, y2 = rect
    left = x1 + POKEMON_AREA[0]
    top = y1 + POKEMON_AREA[1]
    width = POKEMON_AREA[2] - POKEMON_AREA[0]
    height = POKEMON_AREA[3] - POKEMON_AREA[1]

    with mss.mss() as sct:
        monitor = {"left": left, "top": top, "width": width, "height": height}
        img = sct.grab(monitor)
        img_np = np.array(img)
        return cv2.cvtColor(img_np, cv2.COLOR_BGRA2RGB)

# Detection shiny
def is_shiny(img):
    avg_color = img.mean(axis=(0, 1))
    r, g, b = avg_color
    print(f"[DEBUG] Moyenne RGB: R={r:.1f} G={g:.1f} B={b:.1f}")
    return (r < 85)

# Gestion des tentatives
def load_attempts(file_name):
    try:
        with open(file_name, "r") as f:
            return int(f.read().strip())
    except FileNotFoundError:
        return 0

def save_attempts(file_name, attempts):
    with open(file_name, "w") as f:
        f.write(str(attempts))

# Sequence d'inputs (utilise SendInput globalement)
def perform_input_sequence():
    print("[INFO] Envoi des inputs...")
    for _ in range(3):
        send_input_key(MAP_KEYS['X'])
        time.sleep(1)
    send_input_key(MAP_KEYS['Z'])
    time.sleep(3)
    send_input_key(MAP_KEYS['X'])
    time.sleep(4)
    send_input_key(MAP_KEYS['ENTER'])
    time.sleep(1)
    send_input_key(MAP_KEYS['UP'])
    time.sleep(0.3)
    send_input_key(MAP_KEYS['UP'])
    time.sleep(0.3)
    for _ in range(4):
        send_input_key(MAP_KEYS['X'])
        time.sleep(0.5)
    time.sleep(POST_INPUT_DELAY)

def bot_loop(window_title):
    hwnd = win32gui.FindWindow(None, window_title)
    if hwnd == 0:
        print(f"[ERREUR] Fenetre '{window_title}' introuvable.")
        return

    print(f"[{window_title}] Demarrage de la shasse.")
    attempts_file = f"{window_title}_attempts.txt"
    attempts = load_attempts(attempts_file)

    while True:
        attempts += 1
        save_attempts(attempts_file, attempts)
        print(f"[{window_title}] Tentative #{attempts}")

        win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, MAP_KEYS['F1'], 0)
        win32api.PostMessage(hwnd, win32con.WM_KEYUP, MAP_KEYS['F1'], 0)
        print(f"[{window_title}] Savestate chargee.")
        time.sleep(LOAD_DELAY)

        perform_input_sequence()
        img = take_screenshot(hwnd)

        if is_shiny(img):
            print(f"[\U0001F389 {window_title}] SHINY DETECTE ! Tentative #{attempts}")
            cv2.imwrite(f"{window_title}_shiny_{attempts}.png", cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
            win32gui.MessageBox(hwnd, "SHINY DETECTE !", "Felicitations", 0)
            break
        else:
            print(f"[{window_title}] Pas shiny...")

# === Lancement global ===
if __name__ == "__main__":
    print("[INFO] Renommage automatique des fenetres mGBA...")
    window_titles = rename_mgba_windows()

    if not window_titles:
        print("[ERREUR] Aucune fenetre mGBA trouvee.")
    else:
        print(f"[INFO] Fenetres trouvees : {window_titles}")
        print("[INFO] Demarrage de la shasse sur chaque instance...")

        for title in window_titles:
            thread = threading.Thread(target=bot_loop, args=(title,))
            thread.start()