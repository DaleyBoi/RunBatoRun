import pygame
import sys
import os

SCREEN_W = 1920
SCREEN_H = 1080

FONT_DIR   = os.path.join(os.path.dirname(__file__), "assets", "fonts")
BLACK      = (  0,   0,   0)
WHITE      = (255, 255, 255)
YELLOW     = (255, 216,   0)
LIGHT_GREY = (180, 180, 180)
MID_GREY   = ( 35,  35,  45)


def make_scanlines(w, h):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(0, h, 2):
        pygame.draw.line(surf, (0, 0, 0, 55), (0, y), (w, y))
    return surf


class PauseScreen:
    def __init__(self, screen, clock, settings=None,
                 apply_audio_settings=None, toggle_fullscreen=None):
        self.screen = screen
        self.clock  = clock
        self.settings = settings
        self.apply_audio_settings = apply_audio_settings
        self.toggle_fullscreen = toggle_fullscreen
        global SCREEN_W, SCREEN_H
        SCREEN_W, SCREEN_H = screen.get_size()

        fs = SCREEN_H / 1080
        self.font_path = os.path.join(FONT_DIR, "PressStart2P.ttf")
        self.f_title = pygame.font.Font(self.font_path, int(42 * fs))
        self.f_btn   = pygame.font.Font(self.font_path, int(16 * fs))
        self.f_hint  = pygame.font.Font(self.font_path, int( 9 * fs))

        self.options       = ["Resume", "Options", "Return to Main Menu"]
        self.selected      = 0
        self.scanlines     = make_scanlines(SCREEN_W, SCREEN_H)
        self.bg_snapshot   = self._make_blurred_bg()
        self.blink_timer   = 0
        self.blink_visible = True
        self.button_rects = []
        self.option_rects = {}
        self.dragging_slider = None

    def _refresh_display(self):
        global SCREEN_W, SCREEN_H
        SCREEN_W, SCREEN_H = self.screen.get_size()
        fs = SCREEN_H / 1080
        self.f_title = pygame.font.Font(self.font_path, int(42 * fs))
        self.f_btn   = pygame.font.Font(self.font_path, int(16 * fs))
        self.f_hint  = pygame.font.Font(self.font_path, int( 9 * fs))
        self.scanlines = make_scanlines(SCREEN_W, SCREEN_H)
        self.bg_snapshot = self._make_blurred_bg()

    def _make_blurred_bg(self):
        snapshot = self.screen.copy()
        small    = pygame.transform.scale(snapshot, (SCREEN_W // 8, SCREEN_H // 8))
        blurred  = pygame.transform.scale(small, (SCREEN_W, SCREEN_H))
        dark     = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        dark.fill((0, 0, 0, 160))
        blurred.blit(dark, (0, 0))
        return blurred

    def _outline_text(self, font, text, color, cx, cy, d=2):
        for ox in range(-d, d+1):
            for oy in range(-d, d+1):
                if ox == 0 and oy == 0:
                    continue
                s = font.render(text, False, BLACK)
                self.screen.blit(s, s.get_rect(center=(cx+ox, cy+oy)))
        s = font.render(text, False, color)
        self.screen.blit(s, s.get_rect(center=(cx, cy)))

    def _blink(self):
        self.blink_timer += 1
        if self.blink_timer >= 30:
            self.blink_visible = not self.blink_visible
            self.blink_timer   = 0
        return ">" if self.blink_visible else " "

    def _draw(self):
        self.screen.blit(self.bg_snapshot, (0, 0))

        pw = int(SCREEN_W * 0.42)
        ph = int(SCREEN_H * 0.55)
        px = SCREEN_W//2 - pw//2
        py = SCREEN_H//2 - ph//2

        pygame.draw.rect(self.screen, MID_GREY, (px, py, pw, ph))
        pygame.draw.rect(self.screen, YELLOW,   (px, py, pw, ph), 3)
        pygame.draw.rect(self.screen, (60, 60, 80),
                         (px+6, py+6, pw-12, ph-12), 1)

        # Title
        self._outline_text(self.f_title, "PAUSED",
                           YELLOW, SCREEN_W//2, py + int(ph * 0.18), d=3)

        # Divider
        pygame.draw.line(self.screen, YELLOW,
                         (px+20, py + int(ph * 0.30)),
                         (px+pw-20, py + int(ph * 0.30)), 1)

        # Buttons
        cursor = self._blink()
        bw     = int(pw * 0.82)
        bh     = int(ph * 0.14)
        gap    = int(ph * 0.04)
        bx     = SCREEN_W//2 - bw//2
        start_y = py + int(ph * 0.36)
        self.button_rects = []

        for i, opt in enumerate(self.options):
            by     = start_y + i * (bh + gap)
            rect   = pygame.Rect(bx, by, bw, bh)
            self.button_rects.append(rect)
            cx     = bx + bw//2
            cy     = by + bh//2
            active = i == self.selected
            bg     = (50, 50, 70) if active else (28, 28, 38)
            border = YELLOW if active else (55, 55, 75)
            pygame.draw.rect(self.screen, bg,     rect)
            pygame.draw.rect(self.screen, border, rect, 2)
            label = f"{cursor} {opt}" if active else f"  {opt}"
            color = YELLOW if active else LIGHT_GREY
            self._outline_text(self.f_btn, label, color, cx, cy, d=1)

        # Hint
        self._outline_text(self.f_hint,
                           "UP/DOWN   ENTER   ESC to resume",
                           (80, 80, 100), SCREEN_W//2, py + int(ph * 0.93), d=1)

        self.screen.blit(self.scanlines, (0, 0))
        pygame.display.flip()

    def _show_options(self):
        fs = SCREEN_H / 1080
        font_path = os.path.join(FONT_DIR, "PressStart2P.ttf")
        f_btn  = pygame.font.Font(font_path, int(16 * fs))
        f_sub  = pygame.font.Font(font_path, int(12 * fs))
        f_hint = pygame.font.Font(font_path, int( 9 * fs))

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                        return
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self._handle_options_mouse_down(event.pos)
                elif event.type == pygame.MOUSEMOTION and self.dragging_slider:
                    self._set_slider_value(self.dragging_slider, event.pos[0])
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.dragging_slider = None

            self.screen.blit(self.bg_snapshot, (0, 0))
            self.option_rects = {}

            bw = int(SCREEN_W * 0.42)
            bh = int(SCREEN_H * 0.42)
            bx = SCREEN_W//2 - bw//2
            by = SCREEN_H//2 - bh//2
            pygame.draw.rect(self.screen, MID_GREY, (bx, by, bw, bh))
            pygame.draw.rect(self.screen, YELLOW,   (bx, by, bw, bh), 3)
            pygame.draw.rect(self.screen, (60, 60, 80),
                             (bx+6, by+6, bw-12, bh-12), 1)

            cx = bx + bw//2
            self._outline_text(f_btn,  "OPTIONS",
                               YELLOW, cx, by + int(bh * 0.16), d=2)
            pygame.draw.line(self.screen, YELLOW,
                             (bx + 24, by + int(bh * 0.28)),
                             (bx + bw - 24, by + int(bh * 0.28)), 1)

            label_x = bx + int(bw * 0.18)
            control_x = bx + int(bw * 0.48)
            slider_w = int(bw * 0.34)
            row_y = by + int(bh * 0.42)
            row_gap = int(bh * 0.17)

            for i, label in enumerate(("Sound", "Music")):
                cy = row_y + i * row_gap
                setting_name = "sound_volume" if label == "Sound" else "music_volume"
                value = getattr(self.settings, setting_name, 0.65) if self.settings else 0.65
                slider_rect = pygame.Rect(control_x, cy - 10, slider_w, 20)
                self.option_rects[setting_name] = slider_rect
                self._outline_text(f_sub, label, WHITE,
                                   label_x, cy, d=1)
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
            self._outline_text(f_sub, "Fullscreen", WHITE,
                               label_x + int(bw * 0.04), checkbox_y, d=1)
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

            self._outline_text(f_hint, "ESC / ENTER to close",
                               (100,100,100), cx, by + int(bh * 0.88), d=1)

            self.screen.blit(self.scanlines, (0, 0))
            pygame.display.flip()
            self.clock.tick(60)

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

    def _handle_main_mouse_down(self, pos):
        for i, rect in enumerate(self.button_rects):
            if rect.collidepoint(pos):
                self.selected = i
                if i == 0:
                    return "resume"
                if i == 1:
                    self._show_options()
                    return None
                if i == 2:
                    return "menu"
        return None

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "resume"
                    elif event.key == pygame.K_UP:
                        self.selected = (self.selected - 1) % len(self.options)
                    elif event.key == pygame.K_DOWN:
                        self.selected = (self.selected + 1) % len(self.options)
                    elif event.key == pygame.K_RETURN:
                        if self.selected == 0:   return "resume"
                        elif self.selected == 1: self._show_options()
                        elif self.selected == 2: return "menu"
                elif event.type == pygame.MOUSEMOTION:
                    for i, rect in enumerate(self.button_rects):
                        if rect.collidepoint(event.pos):
                            self.selected = i
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    action = self._handle_main_mouse_down(event.pos)
                    if action:
                        return action

            self._draw()
            self.clock.tick(60)
