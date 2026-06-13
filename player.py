import pygame
import os

ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets", "images")

# Sprite sheet crop boxes: (x1, y1, x2, y2)
RUN_CROPS = [
    (22,  4,  75,  98),
    (96,  4, 161,  98),
    (174, 4, 250,  98),
    (274, 4, 329,  98),
    (350, 4, 411,  98),
    (428, 4, 500,  98),
]
JUMP_UP_CROP   = (25,  164,  71, 261)
JUMP_DOWN_CROP = (96,  164, 158, 261)


class Player:
    def __init__(self, game):
        self.screen   = game.screen
        self.settings = game.settings

        sheet = pygame.image.load(
            os.path.join(ASSET_DIR, "sprites.png")
        ).convert_alpha()

        target_h = self.settings.player_height   # 94 px

        def crop_and_scale(box):
            x1, y1, x2, y2 = box
            surf = sheet.subsurface(pygame.Rect(x1, y1, x2 - x1, y2 - y1))
            orig_w, orig_h = surf.get_size()
            scale = target_h / orig_h
            new_w = max(1, int(orig_w * scale))
            return pygame.transform.scale(surf, (new_w, target_h))

        self.frames_run  = [crop_and_scale(c) for c in RUN_CROPS]
        self.frame_jump_up   = crop_and_scale(JUMP_UP_CROP)
        self.frame_jump_down = crop_and_scale(JUMP_DOWN_CROP)

        self.image = self.frames_run[0]
        self.rect  = self.image.get_rect()
        self.rect.x      = self.settings.player_x
        self.rect.bottom = self.settings.ground_y

        self.velocity_y  = 0
        self._anim_timer = 0
        self._anim_frame = 0

    def jump(self):
        if self.rect.bottom >= self.settings.ground_y:
            self.velocity_y = self.settings.jump_power

    def update(self):
        self.velocity_y += self.settings.gravity
        self.rect.y     += self.velocity_y
        if self.rect.bottom >= self.settings.ground_y:
            self.rect.bottom = self.settings.ground_y
            self.velocity_y  = 0
        self._animate()

    def _animate(self):
        in_air = self.rect.bottom < self.settings.ground_y
        if in_air:
            self.image = (self.frame_jump_up if self.velocity_y < 0
                          else self.frame_jump_down)
        else:
            self._anim_timer += 1
            if self._anim_timer >= 6:
                self._anim_timer = 0
                self._anim_frame = (self._anim_frame + 1) % len(self.frames_run)
            self.image = self.frames_run[self._anim_frame]

    def draw(self):
        # Keep rect bottom fixed; image width varies per frame, so align left edge
        draw_rect = self.image.get_rect(bottomleft=self.rect.bottomleft)
        self.screen.blit(self.image, draw_rect)
