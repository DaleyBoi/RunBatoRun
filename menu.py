import pygame
import os
import sys

SCREEN_W = 1200
SCREEN_H = 800


class MenuScreen:
    def __init__(self, screen, clock):
        self.screen  = screen
        self.clock   = clock
        self.font_title  = pygame.font.SysFont("couriernew", 80, bold=True)
        self.font_btn    = pygame.font.SysFont("couriernew", 36, bold=True)
        self.options     = ["Start", "Options", "Quit"]
        self.selected    = 0

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
                        if self.selected == 0:
                            return "play"
                        elif self.selected == 1:
                            self._show_options()
                        elif self.selected == 2:
                            return "quit"

            self._draw()
            self.clock.tick(60)

    def _show_options(self):
        font = pygame.font.SysFont("couriernew", 32, bold=True)
        font_small = pygame.font.SysFont("couriernew", 24)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                        return

            self.screen.fill((0, 0, 0))
            title = font.render("OPTIONS", True, (255, 255, 255))
            soon  = font_small.render("Coming soon...", True, (180, 180, 180))
            hint  = font_small.render("Press ENTER or ESC to go back", True, (120, 120, 120))
            self.screen.blit(title, title.get_rect(center=(SCREEN_W//2, SCREEN_H//2 - 60)))
            self.screen.blit(soon,  soon.get_rect(center=(SCREEN_W//2, SCREEN_H//2)))
            self.screen.blit(hint,  hint.get_rect(center=(SCREEN_W//2, SCREEN_H//2 + 60)))
            pygame.display.flip()
            self.clock.tick(60)

    def _draw(self):
        self.screen.fill((0, 0, 0))

        # Title
        title = self.font_title.render("Run, Bato! Run!", True, (255, 255, 255))
        self.screen.blit(title, title.get_rect(center=(SCREEN_W//2, 250)))

        # Menu options
        for i, option in enumerate(self.options):
            color    = (255, 255, 0) if i == self.selected else (180, 180, 180)
            prefix   = "> " if i == self.selected else "  "
            text     = self.font_btn.render(f"{prefix}{option}", True, color)
            self.screen.blit(text, text.get_rect(center=(SCREEN_W//2, 430 + i * 70)))

        # Nav hint
        hint = pygame.font.SysFont("couriernew", 20).render(
            "UP / DOWN to navigate     ENTER to select", True, (80, 80, 80)
        )
        self.screen.blit(hint, hint.get_rect(center=(SCREEN_W//2, SCREEN_H - 40)))

        pygame.display.flip()