import pygame
import os
import sys
import math
import random

SCREEN_W = 1200
SCREEN_H = 800

ASSET_DIR  = os.path.join(os.path.dirname(__file__), "assets", "images")
FONT_DIR   = os.path.join(os.path.dirname(__file__), "assets", "fonts")

# ── Palette ───────────────────────────────────────────────────────────────
BLACK      = (  0,   0,   0)
WHITE      = (255, 255, 255)
YELLOW     = (255, 216,   0)
YELLOW_DIM = (160, 130,   0)
RED        = (220,  50,  50)
DARK_GREY  = ( 18,  18,  24)
MID_GREY   = ( 35,  35,  45)
LIGHT_GREY = (180, 180, 180)
BLUE_PH    = (  0,  56, 168)
RED_PH     = (206,  17,  38)

MEME_LINES = [
    "Wag kang bumaba, baka mahulog!",
    "Para sa bayan! (daw)",
    "Boy Sili(hahahaha)",
    "Di ko kasalanan 'yan!",
    "To God be the glory... at sa score",
    "Ano ba 'yan, grabe naman",
    "Sige na nga, maglaro ka na",
    "Sus, drama queen talaga",
]


# ── Scanline surface (generated once) ────────────────────────────────────
def make_scanlines(w, h):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(0, h, 2):
        pygame.draw.line(surf, (0, 0, 0, 55), (0, y), (w, y))
    return surf


# ── Parallax background using the game's own bg layers ───────────────────
class BgLayer:
    def __init__(self, image, speed, y):
        self.speed  = speed
        self.y      = y
        w, h        = image.get_size()
        scale       = SCREEN_W / w
        self.image  = pygame.transform.scale(image, (SCREEN_W, int(h * scale)))
        self.img_w  = self.image.get_width()
        self.scroll = 0.0

    def update(self):
        self.scroll -= self.speed
        if self.scroll <= -self.img_w:
            self.scroll = 0.0

    def draw(self, screen):
        x = int(self.scroll)
        while x < SCREEN_W:
            screen.blit(self.image, (x, self.y))
            x += self.img_w


# ── Pixel star field ──────────────────────────────────────────────────────
class StarField:
    def __init__(self):
        self.stars = [
            [random.randint(0, SCREEN_W),
             random.randint(0, SCREEN_H // 2),
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


# ── Cursor blink ─────────────────────────────────────────────────────────
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


# ── Menu ─────────────────────────────────────────────────────────────────
class MenuScreen:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock  = clock

        # Fonts
        font_path = os.path.join(FONT_DIR, "PressStart2P.ttf")
        self.f_title  = pygame.font.Font(font_path, 42)
        self.f_sub    = pygame.font.Font(font_path, 11)
        self.f_btn    = pygame.font.Font(font_path, 18)
        self.f_meme   = pygame.font.Font(font_path, 10)
        self.f_hint   = pygame.font.Font(font_path,  9)

        # Background layers
        def load(name):
            return pygame.image.load(
                os.path.join(ASSET_DIR, name)
            ).convert_alpha()

        src_h    = 324
        scale    = SCREEN_W / 576
        scaled_h = int(src_h * scale)
        layer_y  = 650 - scaled_h   # align to ground_y

        self.bg_layers = [
            BgLayer(load("bg_layer1.png"), 0.0,  layer_y),
            BgLayer(load("bg_layer2.png"), 0.3,  layer_y),
            BgLayer(load("bg_layer3.png"), 0.8,  layer_y),
            BgLayer(load("bg_layer4.png"), 1.5,  layer_y),
            BgLayer(load("bg_layer5.png"), 2.5,  layer_y),
        ]

        # Fill below ground
        self.ground_strip = pygame.Surface((SCREEN_W, SCREEN_H - 650), pygame.SRCALPHA)
        self.ground_strip.fill((80, 120, 50))

        self.scanlines = make_scanlines(SCREEN_W, SCREEN_H)
        self.stars     = StarField()
        self.cursor    = BlinkCursor()

        self.options   = ["Start", "Options", "Quit"]
        self.selected  = 0

        # Title colour cycle
        self.title_tick  = 0
        self.title_colors = [YELLOW, WHITE, RED, WHITE, YELLOW]

        # Meme ticker
        self.meme_idx   = 0
        self.meme_timer = 0
        self.meme_alpha = 255
        self.meme_fading = False

        self.show_options = False

    # ── helpers ──────────────────────────────────────────────────────────
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
        self.screen.blit(self.ground_strip, (0, 650))

    def _draw_title(self):
        self.title_tick += 1
        # Colour flicker every 8 frames
        ci    = (self.title_tick // 8) % len(self.title_colors)
        color = self.title_colors[ci]

        # Shadow block
        shadow = self.f_title.render("Run, Bato! Run!", False, BLACK)
        sr     = shadow.get_rect(center=(SCREEN_W//2 + 4, 180 + 4))
        self.screen.blit(shadow, sr)

        # Main title
        self._outline_text(self.f_title, "Run, Bato! Run!", color,
                           SCREEN_W//2, 180, BLACK, 3)

        # Subtitle
        self._outline_text(self.f_sub, "~ Laro ng Bayan, Para sa Bayan ~",
                           LIGHT_GREY, SCREEN_W//2, 240, BLACK, 1)

    def _draw_buttons(self):
        self.cursor.update()
        for i, opt in enumerate(self.options):
            y      = 330 + i * 80
            active = i == self.selected

            # Button box
            bw, bh = 360, 52
            bx     = SCREEN_W//2 - bw//2
            by     = y - bh//2

            if active:
                pygame.draw.rect(self.screen, MID_GREY,  (bx, by, bw, bh))
                pygame.draw.rect(self.screen, YELLOW,    (bx, by, bw, bh), 2)
            else:
                pygame.draw.rect(self.screen, (25,25,35),(bx, by, bw, bh))
                pygame.draw.rect(self.screen, (60,60,80),(bx, by, bw, bh), 2)

            # Cursor + label
            cursor  = self.cursor.symbol() if active else " "
            label   = f"{cursor} {opt}"
            color   = YELLOW if active else LIGHT_GREY
            self._outline_text(self.f_btn, label, color, SCREEN_W//2, y, BLACK, 2)

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
        self.screen.blit(surf, surf.get_rect(center=(SCREEN_W//2, SCREEN_H - 50)))

    def _draw_hint(self):
        hint = self.f_hint.render(
            "UP / DOWN    ENTER to select", False, (70, 70, 90)
        )
        self.screen.blit(hint, hint.get_rect(center=(SCREEN_W//2, SCREEN_H - 25)))

    def _draw_options_overlay(self):
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        bw, bh = 500, 260
        bx     = SCREEN_W//2 - bw//2
        by     = SCREEN_H//2 - bh//2
        pygame.draw.rect(self.screen, MID_GREY, (bx, by, bw, bh))
        pygame.draw.rect(self.screen, YELLOW,   (bx, by, bw, bh), 2)

        self._outline_text(self.f_btn,  "OPTIONS",
                           YELLOW, SCREEN_W//2, by + 55, BLACK, 2)
        self._outline_text(self.f_sub,  "Coming soon...",
                           WHITE,  SCREEN_W//2, SCREEN_H//2, BLACK, 1)
        self._outline_text(self.f_hint, "ESC / ENTER to close",
                           LIGHT_GREY, SCREEN_W//2, by + bh - 35, BLACK, 1)

    # ── main loop ────────────────────────────────────────────────────────
    def run(self):
        while True:
            mouse = pygame.mouse.get_pos()

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
                            if self.selected == 0: return "play"
                            elif self.selected == 1: self.show_options = True
                            elif self.selected == 2: return "quit"
                        elif event.key == pygame.K_ESCAPE:
                            return "quit"

            # Update
            for layer in self.bg_layers:
                layer.update()
            self.stars.update()

            # Draw
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
