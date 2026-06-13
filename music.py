import pygame
import os

AUDIO_DIR = os.path.join(os.path.dirname(__file__), "assets", "audio")


def play(filename, loop=True):
    path = os.path.join(AUDIO_DIR, filename)
    if not os.path.exists(path):
        return
    pygame.mixer.music.load(path)
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1 if loop else 0)


def stop():
    pygame.mixer.music.stop()


def set_volume(vol):
    pygame.mixer.music.set_volume(vol)