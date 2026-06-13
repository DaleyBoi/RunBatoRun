import pygame
import os

AUDIO_DIR = os.path.join(os.path.dirname(__file__), "assets", "audio")

_sounds = {}

def load():
    files = {
        "jump":     "jump.wav",
        "hit":      "hit.mp3",
        "gameover": "gameover.wav",
    }
    for key, filename in files.items():
        path = os.path.join(AUDIO_DIR, filename)
        if os.path.exists(path):
            _sounds[key] = pygame.mixer.Sound(path)
            _sounds[key].set_volume(0.4)

def play(name):
    if name in _sounds:
        _sounds[name].play()