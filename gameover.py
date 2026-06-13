import pygame
import sys
import os

SCREEN_W = 1200
SCREEN_H = 800

FONT_DIR   = os.path.join(os.path.dirname(__file__), "assets", "fonts")
BLACK      = (  0,   0,   0)
WHITE      = (255, 255, 255)
YELLOW     = (255, 216,   0)
RED        = (220,  50,  50)
LIGHT_GREY = (180, 180, 180)
MID_GREY   = ( 35,  35,  45)


def make_scanlines(w, h):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(0, h, 2):
        pygame.draw.line(surf, (0, 0, 0, 55), (0, y), (w, y))
    return surf


class GameOverScreen:
    def __init__(self, screen, clock, score):
        self.screen = screen
        self.clock  = clock
        self.score  = score

        font_path = os.path.join(FONT_DIR, "PressStart2P.ttf")
        self.f_title = pygame.font.Font(font_path, 38)
        self.f_score = pygame.font.Font(font_path, 14)
        self.f_btn   = pygame.font.Font(font_path, 16)
        self.f_hint  = pygame.font.Font(font_path,  9)

        self.options  = ["Play Again", "Main Menu", "Quit"]
        self.selected = 0
        self.scanlines   = make_scanlines(SCREEN_W, SCREEN_H)
        self.bg_snapshot = self._make_blurred_bg()
        self.blink_timer   = 0
        self.blink_visible = True

        # Title flicker
        self.flicker_timer = 0

    def _make_blurred_bg(self):
        snapshot = self.screen.copy()
        small    = pygame.transform.scale(snapshot, (SCREEN_W // 8, SCREEN_H // 8))
        blurred  = pygame.transform.scale(small, (SCREEN_W, SCREEN_H))
        dark     = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        dark.fill((0, 0, 0, 170))
        blurred.blit(dark, (0, 0))
        return blurred

    def _outline_text(self, font, text, color, cx, cy, d=2):
        for ox in range(-d, d+1):
            for oy in range(-d, d+1):
                if ox == 0 and oy == 0: continue
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

        # Panel
        pw, ph = 580, 420
        px     = SCREEN_W//2 - pw//2
        py     = SCREEN_H//2 - ph//2
        pygame.draw.rect(self.screen, MID_GREY, (px, py, pw, ph))
        pygame.draw.rect(self.screen, RED,      (px, py, pw, ph), 3)
        pygame.draw.rect(self.screen, (80, 20, 20),
                         (px+6, py+6, pw-12, ph-12), 1)

        # Title flicker
        self.flicker_timer += 1
        title_color = RED if (self.flicker_timer // 6) % 2 == 0 else (255, 120, 120)
        self._outline_text(self.f_title, "GAME OVER",
                           title_color, SCREEN_W//2, py + 65, d=3)

        # Divider
        pygame.draw.line(self.screen, RED,
                         (px+20, py+105), (px+pw-20, py+105), 1)

        # Score
        self._outline_text(self.f_score, f"SCORE:  {self.score}",
                           WHITE, SCREEN_W//2, py + 135, d=1)

        # Buttons
        cursor = self._blink()
        bw, bh = 440, 48
        bx     = SCREEN_W//2 - bw//2
        for i, opt in enumerate(self.options):
            by     = py + 175 + i * 72
            active = i == self.selected
            bg     = (60, 20, 20) if active else (28, 28, 38)
            border = RED if active else (55, 55, 75)
            pygame.draw.rect(self.screen, bg,     (bx, by, bw, bh))
            pygame.draw.rect(self.screen, border, (bx, by, bw, bh), 2)
            label = f"{cursor} {opt}" if active else f"  {opt}"
            color = RED if active else LIGHT_GREY
            self._outline_text(self.f_btn, label, color,
                               SCREEN_W//2, by + bh//2, d=1)

        # Hint
        self._outline_text(self.f_hint,
                           "UP/DOWN to navigate     ENTER to select",
                           (80, 80, 100), SCREEN_W//2, py + ph - 25, d=1)

        self.screen.blit(self.scanlines, (0, 0))
        pygame.display.flip()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected = (self.selected - 1) % len(self.options)
                    elif event.key == pygame.K_DOWN:
                        self.selected = (self.selected + 1) % len(self.options)
                    elif event.key == pygame.K_RETURN:
                        if self.selected == 0:   return "restart"
                        elif self.selected == 1: return "menu"
                        elif self.selected == 2: return "quit"

            self._draw()
            self.clock.tick(60)
