import pygame
import sys

SCREEN_W = 1200
SCREEN_H = 800


class GameOverScreen:
    def __init__(self, screen, clock, score):
        self.screen     = screen
        self.clock      = clock
        self.score      = score
        self.font_title = pygame.font.SysFont("couriernew", 64, bold=True)
        self.font_score = pygame.font.SysFont("couriernew", 32, bold=True)
        self.font_btn   = pygame.font.SysFont("couriernew", 32, bold=True)
        self.font_small = pygame.font.SysFont("couriernew", 20)
        self.options    = ["Play Again", "Return to Main Menu", "Quit"]
        self.selected   = 0

        self.bg_snapshot = self._make_blurred_bg()

    def _make_blurred_bg(self):
        snapshot = self.screen.copy()
        small    = pygame.transform.scale(snapshot, (SCREEN_W // 8, SCREEN_H // 8))
        blurred  = pygame.transform.scale(small, (SCREEN_W, SCREEN_H))
        dark     = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        dark.fill((0, 0, 0, 160))
        blurred.blit(dark, (0, 0))
        return blurred

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected = (self.selected - 1) % len(self.options)
                    elif event.key == pygame.K_DOWN:
                        self.selected = (self.selected + 1) % len(self.options)
                    elif event.key == pygame.K_RETURN:
                        if self.selected == 0:
                            return "restart"
                        elif self.selected == 1:
                            return "menu"
                        elif self.selected == 2:
                            return "quit"

            self._draw()
            self.clock.tick(60)

    def _draw_button(self, label, rect, selected):
        bg_color = (220, 220, 220) if selected else (160, 160, 160)
        pygame.draw.rect(self.screen, bg_color,     rect, border_radius=6)
        pygame.draw.rect(self.screen, (80, 80, 80), rect, 2, border_radius=6)
        text = self.font_btn.render(label, True, (0, 0, 0))
        self.screen.blit(text, text.get_rect(center=rect.center))

    def _draw(self):
        self.screen.blit(self.bg_snapshot, (0, 0))

        # Title with outline
        for ox, oy in [(-3,0),(3,0),(0,-3),(0,3),(-3,-3),(3,-3),(-3,3),(3,3)]:
            outline = self.font_title.render("GAME OVER", True, (0, 0, 0))
            self.screen.blit(outline, outline.get_rect(
                center=(SCREEN_W // 2 + ox, 190 + oy)
            ))
        title = self.font_title.render("GAME OVER", True, (220, 50, 50))
        self.screen.blit(title, title.get_rect(center=(SCREEN_W // 2, 190)))

        # Score
        score_text = self.font_score.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, score_text.get_rect(center=(SCREEN_W // 2, 270)))

        # Buttons
        btn_w, btn_h = 400, 60
        cx = SCREEN_W // 2
        for i, option in enumerate(self.options):
            rect = pygame.Rect(cx - btn_w // 2, 330 + i * 85, btn_w, btn_h)
            self._draw_button(option, rect, i == self.selected)

        # Nav hint
        hint = self.font_small.render(
            "UP / DOWN to navigate     ENTER to select",
            True, (160, 160, 160)
        )
        self.screen.blit(hint, hint.get_rect(center=(SCREEN_W // 2, SCREEN_H - 35)))

        pygame.display.flip()