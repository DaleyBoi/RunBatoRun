import pygame
import os

AUDIO_DIR = os.path.join(os.path.dirname(__file__), "assets", "audio")
_volume = 0.5


def play(filename, loop=True):
    path = os.path.join(AUDIO_DIR, filename)
    if not os.path.exists(path):
        return
    pygame.mixer.music.load(path)
    pygame.mixer.music.set_volume(_volume)
    pygame.mixer.music.play(-1 if loop else 0)


def stop():
    pygame.mixer.music.stop()


def fadeout(duration=1000):
    pygame.mixer.music.fadeout(duration)


def set_volume(vol):
    global _volume
    _volume = max(0.0, min(1.0, vol))
    pygame.mixer.music.set_volume(_volume)
