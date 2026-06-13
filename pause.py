import pygame
import sys

SCREEN_W = 1200
SCREEN_H = 800


class PauseScreen:
    def __init__(self, screen, clock):
        self.screen     = screen
        self.clock      = clock
        self.font_title = pygame.font.SysFont("couriernew", 64, bold=True)
        self.font_btn   = pygame.font.SysFont("couriernew", 32, bold=True)
        self.font_small = pygame.font.SysFont("couriernew", 20)
        self.options    = ["Resume", "Options", "Return to Main Menu"]
        self.selected   = 0

        # Take a snapshot of the game screen and fake-blur it
        self.bg_snapshot = self._make_blurred_bg()

    def _make_blurred_bg(self):
        # Fake blur: scale down then scale back up = pixelated blur effect
        snapshot = self.screen.copy()
        small    = pygame.transform.scale(snapshot, (SCREEN_W // 8, SCREEN_H // 8))
        blurred  = pygame.transform.scale(small, (SCREEN_W, SCREEN_H))
        # Darken it on top
        dark = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        dark.fill((0, 0, 0, 140))
        blurred.blit(dark, (0, 0))
        return blurred

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "resume"
                    elif event.key == pygame.K_UP:
                        self.selected = (self.selected - 1) % len(self.options)
                    elif event.key == pygame.K_DOWN:
                        self.selected = (self.selected + 1) % len(self.options)
                    elif event.key == pygame.K_RETURN:
                        if self.selected == 0:
                            return "resume"
                        elif self.selected == 1:
                            self._show_options()
                        elif self.selected == 2:
                            return "menu"

            self._draw()
            self.clock.tick(60)

    def _show_options(self):
        font       = pygame.font.SysFont("couriernew", 32, bold=True)
        font_small = pygame.font.SysFont("couriernew", 24)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                        return

            self.screen.blit(self.bg_snapshot, (0, 0))

            box = pygame.Rect(SCREEN_W // 2 - 220, SCREEN_H // 2 - 120, 440, 240)
            pygame.draw.rect(self.screen, (30, 30, 30), box, border_radius=10)
            pygame.draw.rect(self.screen, (255, 255, 255), box, 2, border_radius=10)

            title = font.render("OPTIONS", True, (255, 255, 255))
            soon  = font_small.render("Coming soon...", True, (180, 180, 180))
            hint  = font_small.render("ESC / ENTER to go back", True, (100, 100, 100))

            self.screen.blit(title, title.get_rect(center=(SCREEN_W // 2, box.y + 55)))
            self.screen.blit(soon,  soon.get_rect(center=(SCREEN_W // 2, box.centery + 10)))
            self.screen.blit(hint,  hint.get_rect(center=(SCREEN_W // 2, box.bottom - 35)))

            pygame.display.flip()
            self.clock.tick(60)

    def _draw_button(self, label, rect, selected):
        # Button background
        bg_color = (220, 220, 220) if selected else (160, 160, 160)
        pygame.draw.rect(self.screen, bg_color,    rect, border_radius=6)
        pygame.draw.rect(self.screen, (80, 80, 80), rect, 2, border_radius=6)

        # Label
        color = (0, 0, 0)
        text  = self.font_btn.render(label, True, color)
        self.screen.blit(text, text.get_rect(center=rect.center))

    def _draw(self):
        # Blurred background
        self.screen.blit(self.bg_snapshot, (0, 0))

        # Title
        # Black outline
        for ox, oy in [(-3,0),(3,0),(0,-3),(0,3),(-3,-3),(3,-3),(-3,3),(3,3)]:
            outline = self.font_title.render("PAUSED", True, (0, 0, 0))
            self.screen.blit(outline, outline.get_rect(
                center=(SCREEN_W // 2 + ox, 210 + oy)
            ))
        title = self.font_title.render("PAUSED", True, (255, 165, 0))
        self.screen.blit(title, title.get_rect(center=(SCREEN_W // 2, 210)))

        # Buttons
        btn_w, btn_h = 400, 60
        cx = SCREEN_W // 2
        for i, option in enumerate(self.options):
            rect = pygame.Rect(cx - btn_w // 2, 310 + i * 85, btn_w, btn_h)
            self._draw_button(option, rect, i == self.selected)

        # Nav hint
        hint = self.font_small.render(
            "UP / DOWN   ENTER to select   ESC to resume",
            True, (160, 160, 160)
        )
        self.screen.blit(hint, hint.get_rect(center=(SCREEN_W // 2, SCREEN_H - 35)))

        pygame.display.flip()