import pygame
import os

ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets", "images")


class Player:
    def __init__(self, game):
        self.screen   = game.screen
        self.settings = game.settings

        target_h = self.settings.player_height

        def scale_frame(surf):
            orig_w, orig_h = surf.get_size()
            scale   = target_h / orig_h
            new_w   = max(1, int(orig_w * scale))
            return pygame.transform.scale(surf, (new_w, target_h))

        def load_frames(filename):
            sheet = pygame.image.load(
                os.path.join(ASSET_DIR, filename)
            ).convert_alpha()

            frame_ranges = []
            in_frame = False
            start_x = 0
            for x in range(sheet.get_width()):
                has_pixel = any(
                    sheet.get_at((x, y)).a > 0
                    for y in range(sheet.get_height())
                )
                if has_pixel and not in_frame:
                    start_x = x
                    in_frame = True
                elif not has_pixel and in_frame:
                    frame_ranges.append((start_x, x))
                    in_frame = False
            if in_frame:
                frame_ranges.append((start_x, sheet.get_width()))

            frames = []
            for x1, x2 in frame_ranges:
                frame = sheet.subsurface(
                    pygame.Rect(x1, 0, x2 - x1, sheet.get_height())
                )
                frames.append(scale_frame(frame))
            return frames

        self.frames_run  = load_frames("run.PNG")
        self.frames_jump = load_frames("jump.PNG")
        self.frames_idle = [self.frames_run[0]]

        self.image = self.frames_idle[0]
        self.rect  = self.image.get_rect()
        self.rect.x      = self.settings.player_x
        self.rect.bottom = self.settings.ground_y

        self.velocity_y  = 0
        self._anim_timer = 0
        self._anim_frame = 0
        self._jump_timer = 0
        self._jump_frame = 0

    def jump(self):
        if self.rect.bottom >= self.settings.ground_y:
            self.velocity_y = self.settings.jump_power
            self._jump_timer = 0
            self._jump_frame = 0

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
            self._jump_timer += 1
            if self._jump_timer >= 6:
                self._jump_timer = 0
                self._jump_frame = min(
                    self._jump_frame + 1,
                    len(self.frames_jump) - 1
                )
            self.image = self.frames_jump[self._jump_frame]
        else:
            self._jump_timer = 0
            self._jump_frame = 0
            self._anim_timer += 1
            if self._anim_timer >= 6:
                self._anim_timer = 0
                self._anim_frame = (self._anim_frame + 1) % len(self.frames_run)
            self.image = self.frames_run[self._anim_frame]

    def draw(self):
        draw_rect = self.image.get_rect(bottomleft=self.rect.bottomleft)
        self.screen.blit(self.image, draw_rect)
