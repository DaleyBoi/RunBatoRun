import pygame
import os
import sys
import math
import random

SCREEN_W = 1920
SCREEN_H = 1080

ASSET_DIR  = os.path.join(os.path.dirname(__file__), "assets", "images")
FONT_DIR   = os.path.join(os.path.dirname(__file__), "assets", "fonts")

BLACK      = (  0,   0,   0)
WHITE      = (255, 255, 255)
YELLOW     = (255, 216,   0)
YELLOW_DIM = (160, 130,   0)
RED        = (220,  50,  50)
DARK_GREY  = ( 18,  18,  24)
MID_GREY   = ( 35,  35,  45)
LIGHT_GREY = (180, 180, 180)

MEME_LINES = [
    "Wag kang bumaba, baka mahulog!",
    "Para sa bayan! (daw)",
    "Laro na pre, wag nang mag-esenyo",
    "Di ko kasalanan 'yan!",
    "To God be the glory... at sa score",
    "Ano ba 'yan, grabe naman",
    "Sige na nga, maglaro ka na",
    "Sus, drama queen talaga",
]


def make_scanlines(w, h):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(0, h, 2):
        pygame.draw.line(surf, (0, 0, 0, 55), (0, y), (w, y))
    return surf


class BgLayer:
    def __init__(self, image, speed, screen_w, screen_h, ground_y):
        self.speed = speed
        w, h       = image.get_size()
        scale      = screen_w / w
        new_h      = int(h * scale)
        self.image = pygame.transform.scale(image, (screen_w, new_h))
        self.img_w = screen_w
        self.y     = ground_y - new_h
        self.scroll = 0.0

    def update(self):
        self.scroll -= self.speed
        if self.scroll <= -self.img_w:
            self.scroll = 0.0

    def draw(self, screen):
        x = int(self.scroll)
        while x < self.img_w:
            screen.blit(self.image, (x, self.y))
            x += self.img_w


class StarField:
    def __init__(self, w, h):
        self.stars = [
            [random.randint(0, w),
             random.randint(0, h // 3),
             random.randint(1, 3),
             random.uniform(0, math.pi * 2)]
            for _ in range(80)
        ]

    def update(self):
        for s in self.stars:
            s[3] += 0.03

    def draw(self, screen):
        for x, y, r, phase in self.stars:
            a = int(120 + 100 * math.sin(phase))
            pygame.draw.circle(screen, (a, a, a), (x, y), r)


class BlinkCursor:
    def __init__(self):
        self.timer   = 0
        self.visible = True

    def update(self):
        self.timer += 1
        if self.timer >= 30:
            self.visible = not self.visible
            self.timer   = 0

    def symbol(self):
        return ">" if self.visible else " "


class MenuScreen:
    def __init__(self, screen, clock, settings=None, stats=None,
                 apply_audio_settings=None, toggle_fullscreen=None):
        self.screen = screen
        self.clock  = clock
        self.settings = settings
        self.stats = stats
        self.apply_audio_settings = apply_audio_settings
        self.toggle_fullscreen = toggle_fullscreen
        global SCREEN_W, SCREEN_H
        SCREEN_W, SCREEN_H = screen.get_size()

        fs = SCREEN_H / 1080
        self.font_path = os.path.join(FONT_DIR, "PressStart2P.ttf")
        self.f_title = pygame.font.Font(self.font_path, int(52 * fs))
        self.f_sub   = pygame.font.Font(self.font_path, int(13 * fs))
        self.f_btn   = pygame.font.Font(self.font_path, int(22 * fs))
        self.f_meme  = pygame.font.Font(self.font_path, int(12 * fs))
        self.f_hint  = pygame.font.Font(self.font_path, int(10 * fs))

        self.ground_y = int(SCREEN_H * 0.62)

        def load(name):
            return pygame.image.load(
                os.path.join(ASSET_DIR, name)
            ).convert_alpha()

        self.bg_layers = [
            BgLayer(load("bg_layer1.png"), 0.0, SCREEN_W, SCREEN_H, self.ground_y),
            BgLayer(load("bg_layer2.png"), 0.3, SCREEN_W, SCREEN_H, self.ground_y),
            BgLayer(load("bg_layer3.png"), 0.8, SCREEN_W, SCREEN_H, self.ground_y),
            BgLayer(load("bg_layer4.png"), 1.5, SCREEN_W, SCREEN_H, self.ground_y),
            BgLayer(load("bg_layer5.png"), 2.5, SCREEN_W, SCREEN_H, self.ground_y),
        ]

        self.ground_color = (80, 120, 50)
        self.scanlines    = make_scanlines(SCREEN_W, SCREEN_H)
        self.stars        = StarField(SCREEN_W, SCREEN_H)
        self.cursor       = BlinkCursor()
        self.options      = ["Start", "Options", "Quit"]
        self.selected     = 0
        self.title_tick   = 0
        self.title_colors = [YELLOW, WHITE, RED, WHITE, YELLOW]
        self.meme_idx     = 0
        self.meme_timer   = 0
        self.meme_alpha   = 255
        self.meme_fading  = False
        self.show_options = False
        self.button_rects = []
        self.option_rects = {}
        self.dragging_slider = None

    def _refresh_display(self):
        global SCREEN_W, SCREEN_H
        SCREEN_W, SCREEN_H = self.screen.get_size()
        fs = SCREEN_H / 1080
        self.f_title = pygame.font.Font(self.font_path, int(52 * fs))
        self.f_sub   = pygame.font.Font(self.font_path, int(13 * fs))
        self.f_btn   = pygame.font.Font(self.font_path, int(22 * fs))
        self.f_meme  = pygame.font.Font(self.font_path, int(12 * fs))
        self.f_hint  = pygame.font.Font(self.font_path, int(10 * fs))
        self.ground_y = int(SCREEN_H * 0.62)

        def load(name):
            return pygame.image.load(
                os.path.join(ASSET_DIR, name)
            ).convert_alpha()

        self.bg_layers = [
            BgLayer(load("bg_layer1.png"), 0.0, SCREEN_W, SCREEN_H, self.ground_y),
            BgLayer(load("bg_layer2.png"), 0.3, SCREEN_W, SCREEN_H, self.ground_y),
            BgLayer(load("bg_layer3.png"), 0.8, SCREEN_W, SCREEN_H, self.ground_y),
            BgLayer(load("bg_layer4.png"), 1.5, SCREEN_W, SCREEN_H, self.ground_y),
            BgLayer(load("bg_layer5.png"), 2.5, SCREEN_W, SCREEN_H, self.ground_y),
        ]
        self.scanlines = make_scanlines(SCREEN_W, SCREEN_H)
        self.stars = StarField(SCREEN_W, SCREEN_H)

    def _outline_text(self, font, text, color, cx, cy, outline_color=BLACK, d=2):
        for ox in range(-d, d+1):
            for oy in range(-d, d+1):
                if ox == 0 and oy == 0:
                    continue
                s = font.render(text, False, outline_color)
                self.screen.blit(s, s.get_rect(center=(cx+ox, cy+oy)))
        s = font.render(text, False, color)
        self.screen.blit(s, s.get_rect(center=(cx, cy)))

    def _draw_bg(self):
        self.screen.fill(DARK_GREY)
        for layer in self.bg_layers:
            layer.draw(self.screen)
        pygame.draw.rect(self.screen, self.ground_color,
                         (0, self.ground_y, SCREEN_W, SCREEN_H - self.ground_y))

    def _draw_title(self):
        self.title_tick += 1
        ci    = (self.title_tick // 8) % len(self.title_colors)
        color = self.title_colors[ci]

        title_y = int(SCREEN_H * 0.18)
        sub_y   = int(SCREEN_H * 0.26)

        shadow = self.f_title.render("Run, Bato! Run!", False, BLACK)
        self.screen.blit(shadow, shadow.get_rect(center=(SCREEN_W//2 + 4, title_y + 4)))
        self._outline_text(self.f_title, "Run, Bato! Run!", color,
                           SCREEN_W//2, title_y, BLACK, 3)
        self._outline_text(self.f_sub, "~ Laro ng Bayan, Para sa Bayan ~",
                           LIGHT_GREY, SCREEN_W//2, sub_y, BLACK, 1)

    def _draw_buttons(self):
        self.cursor.update()
        bw = int(SCREEN_W * 0.28)
        bh = int(SCREEN_H * 0.08)
        gap = int(SCREEN_H * 0.02)
        start_y = int(SCREEN_H * 0.38)
        self.button_rects = []

        for i, opt in enumerate(self.options):
            by     = start_y + i * (bh + gap)
            bx     = SCREEN_W//2 - bw//2
            rect   = pygame.Rect(bx, by, bw, bh)
            self.button_rects.append(rect)
            cx     = bx + bw//2
            cy     = by + bh//2
            active = i == self.selected

            bg     = MID_GREY if active else (25, 25, 35)
            border = YELLOW   if active else (60, 60, 80)
            pygame.draw.rect(self.screen, bg,     rect)
            pygame.draw.rect(self.screen, border, rect, 2)

            color  = YELLOW if active else LIGHT_GREY
            self._outline_text(self.f_btn, opt, color, cx, cy, BLACK, 2)

            if active:
                label_w = self.f_btn.size(opt)[0]
                cursor_x = cx - label_w // 2 - int(SCREEN_W * 0.025)
                self._outline_text(
                    self.f_btn, self.cursor.symbol(), color,
                    cursor_x, cy, BLACK, 2
                )

    def _draw_meme(self):
        self.meme_timer += 1
        if self.meme_timer > 220:
            self.meme_fading = True
        if self.meme_fading:
            self.meme_alpha -= 5
            if self.meme_alpha <= 0:
                self.meme_alpha  = 255
                self.meme_fading = False
                self.meme_timer  = 0
                self.meme_idx    = (self.meme_idx + 1) % len(MEME_LINES)

        surf = self.f_meme.render(
            f'"{MEME_LINES[self.meme_idx]}"', False, YELLOW_DIM
        )
        surf.set_alpha(self.meme_alpha)
        self.screen.blit(surf, surf.get_rect(
            center=(SCREEN_W//2, int(SCREEN_H * 0.93))
        ))

    def _draw_hint(self):
        hint = self.f_hint.render(
            "UP / DOWN    ENTER to select", False, (70, 70, 90)
        )
        self.screen.blit(hint, hint.get_rect(
            center=(SCREEN_W//2, int(SCREEN_H * 0.97))
        ))

    def _draw_options_overlay(self):
        self.option_rects = {}
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        bw = int(SCREEN_W * 0.45)
        bh = int(SCREEN_H * 0.52)
        bx = SCREEN_W//2 - bw//2
        by = SCREEN_H//2 - bh//2
        pygame.draw.rect(self.screen, MID_GREY, (bx, by, bw, bh))
        pygame.draw.rect(self.screen, YELLOW,   (bx, by, bw, bh), 2)
        pygame.draw.rect(self.screen, (60, 60, 80),
                         (bx+6, by+6, bw-12, bh-12), 1)

        self._outline_text(self.f_btn,  "OPTIONS",
                           YELLOW, SCREEN_W//2, by + int(bh * 0.14), BLACK, 2)
        pygame.draw.line(self.screen, YELLOW,
                         (bx + 24, by + int(bh * 0.24)),
                         (bx + bw - 24, by + int(bh * 0.24)), 1)

        label_x = bx + int(bw * 0.16)
        control_x = bx + int(bw * 0.48)
        slider_w = int(bw * 0.35)
        row_y = by + int(bh * 0.35)
        row_gap = int(bh * 0.14)

        for i, label in enumerate(("Sound", "Music")):
            cy = row_y + i * row_gap
            setting_name = "sound_volume" if label == "Sound" else "music_volume"
            value = getattr(self.settings, setting_name, 0.65) if self.settings else 0.65
            slider_rect = pygame.Rect(control_x, cy - 10, slider_w, 20)
            self.option_rects[setting_name] = slider_rect
            self._outline_text(self.f_sub, label, WHITE,
                               label_x, cy, BLACK, 1)
            pygame.draw.rect(self.screen, (20, 20, 30),
                             (control_x, cy - 6, slider_w, 12))
            pygame.draw.rect(self.screen, (75, 75, 95),
                             (control_x, cy - 6, slider_w, 12), 2)
            fill_w = int(slider_w * value)
            pygame.draw.rect(self.screen, YELLOW,
                             (control_x, cy - 6, fill_w, 12))
            knob_x = control_x + fill_w
            pygame.draw.rect(self.screen, WHITE,
                             (knob_x - 6, cy - 14, 12, 28))
            pygame.draw.rect(self.screen, BLACK,
                             (knob_x - 6, cy - 14, 12, 28), 1)

        checkbox_y = row_y + 2 * row_gap
        box_size = int(SCREEN_H * 0.035)
        checkbox_rect = pygame.Rect(control_x, checkbox_y - box_size//2,
                                    box_size, box_size)
        self.option_rects["fullscreen"] = checkbox_rect
        self._outline_text(self.f_sub, "Fullscreen", WHITE,
                           label_x + int(bw * 0.04), checkbox_y, BLACK, 1)
        pygame.draw.rect(self.screen, (20, 20, 30),
                         checkbox_rect)
        pygame.draw.rect(self.screen, YELLOW,
                         checkbox_rect, 2)
        if getattr(self.settings, "fullscreen", True):
            pygame.draw.line(self.screen, WHITE,
                             (control_x + 7, checkbox_y),
                             (control_x + box_size//2 - 1, checkbox_y + 8), 3)
            pygame.draw.line(self.screen, WHITE,
                             (control_x + box_size//2 - 1, checkbox_y + 8),
                             (control_x + box_size - 7, checkbox_y - 9), 3)

        delete_y = row_y + 3 * row_gap
        delete_w = int(bw * 0.56)
        delete_h = int(bh * 0.12)
        delete_x = SCREEN_W//2 - delete_w//2
        delete_rect = pygame.Rect(delete_x, delete_y - delete_h//2,
                                  delete_w, delete_h)
        self.option_rects["delete_save"] = delete_rect
        pygame.draw.rect(self.screen, (65, 28, 34),
                         delete_rect)
        pygame.draw.rect(self.screen, RED,
                         delete_rect, 2)
        self._outline_text(self.f_sub, "Delete Save Data", RED,
                           SCREEN_W//2, delete_y, BLACK, 1)

        self._outline_text(self.f_hint, "ESC / ENTER to close",
                           LIGHT_GREY, SCREEN_W//2, by + int(bh * 0.92), BLACK, 1)

    def _set_slider_value(self, name, mouse_x):
        if not self.settings or name not in self.option_rects:
            return
        rect = self.option_rects[name]
        value = (mouse_x - rect.left) / rect.width
        value = max(0.0, min(1.0, value))
        setattr(self.settings, name, value)
        if self.apply_audio_settings:
            self.apply_audio_settings()

    def _handle_options_mouse_down(self, pos):
        if "sound_volume" in self.option_rects and self.option_rects["sound_volume"].collidepoint(pos):
            self.dragging_slider = "sound_volume"
            self._set_slider_value("sound_volume", pos[0])
            return
        if "music_volume" in self.option_rects and self.option_rects["music_volume"].collidepoint(pos):
            self.dragging_slider = "music_volume"
            self._set_slider_value("music_volume", pos[0])
            return
        if "fullscreen" in self.option_rects and self.option_rects["fullscreen"].collidepoint(pos):
            if self.toggle_fullscreen:
                self.screen = self.toggle_fullscreen()
                self._refresh_display()
            elif self.settings:
                self.settings.fullscreen = not self.settings.fullscreen
            return
        if "delete_save" in self.option_rects and self.option_rects["delete_save"].collidepoint(pos):
            if self.stats:
                self.stats.delete_save_data()

    def _handle_main_mouse_down(self, pos):
        for i, rect in enumerate(self.button_rects):
            if rect.collidepoint(pos):
                self.selected = i
                if i == 0:
                    return "play"
                if i == 1:
                    self.show_options = True
                    return None
                if i == 2:
                    return "quit"
        return None

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.KEYDOWN:
                    if self.show_options:
                        if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                            self.show_options = False
                    else:
                        if event.key == pygame.K_UP:
                            self.selected = (self.selected - 1) % len(self.options)
                        elif event.key == pygame.K_DOWN:
                            self.selected = (self.selected + 1) % len(self.options)
                        elif event.key == pygame.K_RETURN:
                            if self.selected == 0:   return "play"
                            elif self.selected == 1: self.show_options = True
                            elif self.selected == 2: return "quit"
                        elif event.key == pygame.K_ESCAPE:
                            return "quit"
                elif event.type == pygame.MOUSEMOTION:
                    if self.show_options and self.dragging_slider:
                        self._set_slider_value(self.dragging_slider, event.pos[0])
                    elif not self.show_options:
                        for i, rect in enumerate(self.button_rects):
                            if rect.collidepoint(event.pos):
                                self.selected = i
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.show_options:
                        self._handle_options_mouse_down(event.pos)
                    else:
                        action = self._handle_main_mouse_down(event.pos)
                        if action:
                            return action
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.dragging_slider = None

            for layer in self.bg_layers:
                layer.update()
            self.stars.update()

            self._draw_bg()
            self.stars.draw(self.screen)
            self._draw_title()
            self._draw_buttons()
            self._draw_meme()
            self._draw_hint()
            self.screen.blit(self.scanlines, (0, 0))

            if self.show_options:
                self._draw_options_overlay()

            pygame.display.flip()
            self.clock.tick(60)
