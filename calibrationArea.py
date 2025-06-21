import pyautogui
import time

print("Place ta souris sur le coin **haut gauche** du sprite de Bulbizarre.")
time.sleep(5)
x1, y1 = pyautogui.position()
print(f"Haut gauche : {x1}, {y1}")

print("Place ta souris sur le coin **bas droit** du sprite de Bulbizarre.")
time.sleep(5)
x2, y2 = pyautogui.position()
print(f"Bas droit : {x2}, {y2}")

print(f"Utilise : POKEMON_AREA = ({x1}, {y1}, {x2}, {y2})")
