import cv2
import numpy as np
from PIL import ImageGrab
POKEMON_AREA = (327, 242, 475, 376)  # Zone de capture du sprite du Pokémon

def take_screenshot():
    img = ImageGrab.grab(bbox=POKEMON_AREA)
    img_np = np.array(img)
    return cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)

def is_shiny_bulbasaur(img):
    avg_color = img.mean(axis=(0, 1))
    r, g, b = avg_color
    print(f"[DEBUG] Couleur moyenne : R={r:.1f}, G={g:.1f}, B={b:.1f}")
    return (r < 85)

#Bulbasaur normal = 159 180 148
#Bulbasaur shiny = 82 176 130

is_shiny_bulbasaur(take_screenshot())