import pygame
import os

ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets", "images")


class Obstacle:
    # Load frames once at class level
    _frames = None

    def __init__(self, game):
        self.screen   = game.screen
        self.settings = game.settings

        if Obstacle._frames is None:
            Obstacle._frames = [
                pygame.image.load(
                    os.path.join(ASSET_DIR, f"moneybag_{i}.png")
                ).convert_alpha()
                for i in range(2)
            ]

        # Scale to obstacle size
        w = self.settings.obstacle_width
        h = self.settings.obstacle_height
        self.frames = [
            pygame.transform.scale(f, (w, h)) for f in Obstacle._frames
        ]

        self.rect = self.frames[0].get_rect()
        self.rect.x      = self.settings.screen_width
        self.rect.bottom = self.settings.ground_y

        # Bounce animation
        self.anim_timer = 0
        self.anim_frame = 0
        self.bob_y      = 0.0
        self.bob_vel    = -3.0
        self.on_ground  = True

    def update(self):
        self.rect.x -= self.settings.game_speed

        # Bob up and down
        self.bob_vel += 0.5
        self.bob_y   += self.bob_vel
        if self.bob_y >= 0:
            self.bob_y  = 0
            self.bob_vel = -4.0
            self.anim_frame = 1   # squish frame on land
        else:
            self.anim_frame = 0   # normal frame in air

    def draw(self):
        draw_y = self.rect.y + int(self.bob_y)
        self.screen.blit(self.frames[self.anim_frame], (self.rect.x, draw_y))
