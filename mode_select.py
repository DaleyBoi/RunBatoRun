import os
import pygame

ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets", "images")
FONT_DIR = os.path.join(os.path.dirname(__file__), "assets", "fonts")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 216, 0)
DARK_GREY = (18, 18, 24)
MID_GREY = (35, 35, 45)
LIGHT_GREY = (180, 180, 180)


def make_scanlines(w, h):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(0, h, 2):
        pygame.draw.line(surf, (0, 0, 0, 55), (0, y), (w, y))
    return surf


class BgLayer:
    def __init__(self, image, speed, screen_w, ground_y):
        self.speed = speed
        w, h = image.get_size()
        scale = screen_w / w
        new_h = int(h * scale)
        self.image = pygame.transform.scale(image, (screen_w, new_h))
        self.img_w = screen_w
        self.y = ground_y - new_h
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


class BlinkCursor:
    def __init__(self):
        self.timer = 0
        self.visible = True

    def update(self):
        self.timer += 1
        if self.timer >= 30:
            self.visible = not self.visible
            self.timer = 0

    def symbol(self):
        return ">" if self.visible else " "


class ModeSelectScreen:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.selected = 0
        self.options = [
            ("Story Mode", "3 levels. Finish the run."),
            ("Endless Mode", "Survive as long as you can."),
        ]
        self.button_rects = []
        self.cursor = BlinkCursor()
        self._refresh_display()

    def _refresh_display(self):
        self.screen_w, self.screen_h = self.screen.get_size()
        fs = self.screen_h / 1080
        font_path = os.path.join(FONT_DIR, "PressStart2P.ttf")
        self.f_title = pygame.font.Font(font_path, int(38 * fs))
        self.f_btn = pygame.font.Font(font_path, int(20 * fs))
        self.f_sub = pygame.font.Font(font_path, int(11 * fs))
        self.f_hint = pygame.font.Font(font_path, int(10 * fs))
        self.ground_y = int(self.screen_h * 0.62)
        self.scanlines = make_scanlines(self.screen_w, self.screen_h)

        def load(name):
            return pygame.image.load(os.path.join(ASSET_DIR, name)).convert_alpha()

        self.bg_layers = [
            BgLayer(load("bg_layer1.png"), 0.0, self.screen_w, self.ground_y),
            BgLayer(load("bg_layer2.png"), 0.3, self.screen_w, self.ground_y),
            BgLayer(load("bg_layer3.png"), 0.8, self.screen_w, self.ground_y),
            BgLayer(load("bg_layer4.png"), 1.5, self.screen_w, self.ground_y),
            BgLayer(load("bg_layer5.png"), 2.5, self.screen_w, self.ground_y),
        ]

    def _outline_text(self, font, text, color, cx, cy, outline_color=BLACK, d=2):
        for ox in range(-d, d + 1):
            for oy in range(-d, d + 1):
                if ox == 0 and oy == 0:
                    continue
                s = font.render(text, False, outline_color)
                self.screen.blit(s, s.get_rect(center=(cx + ox, cy + oy)))
        s = font.render(text, False, color)
        self.screen.blit(s, s.get_rect(center=(cx, cy)))

    def _draw_bg(self):
        self.screen.fill(DARK_GREY)
        for layer in self.bg_layers:
            layer.draw(self.screen)
        pygame.draw.rect(
            self.screen,
            (80, 120, 50),
            (0, self.ground_y, self.screen_w, self.screen_h - self.ground_y),
        )

    def _draw_title(self):
        self._outline_text(
            self.f_title,
            "Choose Game Mode",
            YELLOW,
            self.screen_w // 2,
            int(self.screen_h * 0.22),
            BLACK,
            3,
        )
        self._outline_text(
            self.f_sub,
            "Pick your run",
            LIGHT_GREY,
            self.screen_w // 2,
            int(self.screen_h * 0.29),
            BLACK,
            1,
        )

    def _draw_buttons(self):
        self.cursor.update()
        bw = int(self.screen_w * 0.36)
        bh = int(self.screen_h * 0.11)
        gap = int(self.screen_h * 0.035)
        start_y = int(self.screen_h * 0.40)
        self.button_rects = []

        for i, (label, desc) in enumerate(self.options):
            rect = pygame.Rect(
                self.screen_w // 2 - bw // 2,
                start_y + i * (bh + gap),
                bw,
                bh,
            )
            self.button_rects.append(rect)
            active = i == self.selected
            bg = MID_GREY if active else (25, 25, 35)
            border = YELLOW if active else (60, 60, 80)
            color = YELLOW if active else LIGHT_GREY

            pygame.draw.rect(self.screen, bg, rect)
            pygame.draw.rect(self.screen, border, rect, 2)
            self._outline_text(
                self.f_btn,
                label,
                color,
                rect.centerx,
                rect.centery - int(bh * 0.16),
                BLACK,
                2,
            )
            self._outline_text(
                self.f_sub,
                desc,
                WHITE if active else LIGHT_GREY,
                rect.centerx,
                rect.centery + int(bh * 0.20),
                BLACK,
                1,
            )

            if active:
                label_w = self.f_btn.size(label)[0]
                cursor_x = rect.centerx - label_w // 2 - int(self.screen_w * 0.025)
                self._outline_text(
                    self.f_btn,
                    self.cursor.symbol(),
                    color,
                    cursor_x,
                    rect.centery - int(bh * 0.16),
                    BLACK,
                    2,
                )

    def _draw_hint(self):
        hint = self.f_hint.render("UP / DOWN    ENTER to select    ESC to go back", False, (70, 70, 90))
        self.screen.blit(hint, hint.get_rect(center=(self.screen_w // 2, int(self.screen_h * 0.96))))

    def _select_current(self):
        return "story" if self.selected == 0 else "endless"

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected = (self.selected - 1) % len(self.options)
                    elif event.key == pygame.K_DOWN:
                        self.selected = (self.selected + 1) % len(self.options)
                    elif event.key == pygame.K_RETURN:
                        return self._select_current()
                    elif event.key == pygame.K_ESCAPE:
                        return "back"
                elif event.type == pygame.MOUSEMOTION:
                    for i, rect in enumerate(self.button_rects):
                        if rect.collidepoint(event.pos):
                            self.selected = i
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for i, rect in enumerate(self.button_rects):
                        if rect.collidepoint(event.pos):
                            self.selected = i
                            return self._select_current()

            for layer in self.bg_layers:
                layer.update()

            self._draw_bg()
            self._draw_title()
            self._draw_buttons()
            self._draw_hint()
            self.screen.blit(self.scanlines, (0, 0))
            pygame.display.flip()
            self.clock.tick(60)
