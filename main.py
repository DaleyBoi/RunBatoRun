import sys
import os
import pygame
from settings import Settings
from player import Player
from obstacle import Obstacle
from game_stats import GameStats
from menu import MenuScreen

ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets", "images")

SCREEN_W = 1200
SCREEN_H = 800


class ParallaxLayer:
    def __init__(self, image, speed_factor, y):
        self.speed  = speed_factor
        self.y      = y
        w, h        = image.get_size()
        scale       = SCREEN_W / w
        self.image  = pygame.transform.scale(image, (SCREEN_W, int(h * scale)))
        self.img_w  = self.image.get_width()
        self.scroll = 0.0

    def update(self, game_speed):
        self.scroll -= game_speed * self.speed
        if self.scroll <= -self.img_w:
            self.scroll = 0.0

    def draw(self, screen):
        x = int(self.scroll)
        while x < SCREEN_W:
            screen.blit(self.image, (x, self.y))
            x += self.img_w


class EndlessRunner:
    def __init__(self):
        pygame.init()
        self.settings = Settings()
        self.screen   = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Endless Runner")
        self.clock    = pygame.time.Clock()

        self._load_background()
        self.player      = Player(self)
        self.stats       = GameStats()
        self.obstacles   = []
        self.spawn_timer = 0
        self.font        = pygame.font.SysFont(None, 48)
        self.small_font  = pygame.font.SysFont(None, 32)

    def _load_background(self):
        def load(name):
            return pygame.image.load(
                os.path.join(ASSET_DIR, name)
            ).convert_alpha()

        src_h    = 324
        scale    = SCREEN_W / 576
        scaled_h = int(src_h * scale)
        layer_y  = self.settings.ground_y - scaled_h

        self.bg_layers = [
            ParallaxLayer(load("bg_layer1.png"), 0.0,  layer_y),
            ParallaxLayer(load("bg_layer2.png"), 0.05, layer_y),
            ParallaxLayer(load("bg_layer3.png"), 0.15, layer_y),
            ParallaxLayer(load("bg_layer4.png"), 0.3,  layer_y),
            ParallaxLayer(load("bg_layer5.png"), 0.5,  layer_y),
        ]

        self.ground_color = (80, 120, 50)
    def run_game(self):
        menu   = MenuScreen(self.screen, self.clock)
        result = menu.run()
        if result == "quit":
            pygame.quit()
            sys.exit()

        while True:
            self._check_events()
            if self.stats.game_active:
                self._update_game()
            self._update_screen()
            self.clock.tick(self.settings.fps)

    def _check_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    sys.exit()
                elif event.key == pygame.K_SPACE:
                    if self.stats.game_active:
                        self.player.jump()
                elif event.key == pygame.K_e:
                    if not self.stats.game_active:
                        self._restart_game()

    def _update_game(self):
        self.player.update()
        self._spawn_obstacles()
        self._update_obstacles()
        for layer in self.bg_layers:
            layer.update(self.settings.game_speed)
        self.stats.score += 1
        if self.stats.score % 1000 == 0:
            self.settings.increase_speed()

    def _spawn_obstacles(self):
        self.spawn_timer += 1
        if self.spawn_timer >= self.settings.obstacle_spawn_time:
            self.obstacles.append(Obstacle(self))
            self.spawn_timer = 0

    def _update_obstacles(self):
        for obs in self.obstacles[:]:
            obs.update()
            if obs.rect.right < 0:
                self.obstacles.remove(obs)
            elif self.player.rect.colliderect(obs.rect):
                self.stats.game_active = False

    def _update_screen(self):
        self.screen.fill((70, 160, 210))
        for layer in self.bg_layers:
            layer.draw(self.screen)

        pygame.draw.rect(
            self.screen, self.ground_color,
            (0, self.settings.ground_y, SCREEN_W, SCREEN_H - self.settings.ground_y)
        )
        pygame.draw.line(
            self.screen, (40, 40, 42),
            (0, self.settings.ground_y), (SCREEN_W, self.settings.ground_y), 3
        )

        self.player.draw()
        for obs in self.obstacles:
            obs.draw()

        shadow = self.font.render(f"Score: {self.stats.score}", True, (0, 0, 0))
        score  = self.font.render(f"Score: {self.stats.score}", True, (255, 255, 255))
        self.screen.blit(shadow, (22, 22))
        self.screen.blit(score,  (20, 20))

        if not self.stats.game_active:
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))
            go   = self.font.render("GAME OVER", True, (255, 80, 80))
            hint = self.small_font.render("Press  E  to restart", True, (220, 220, 220))
            self.screen.blit(go,   go.get_rect(center=(SCREEN_W//2, SCREEN_H//2 - 30)))
            self.screen.blit(hint, hint.get_rect(center=(SCREEN_W//2, SCREEN_H//2 + 25)))

        pygame.display.flip()

    def _restart_game(self):
        self.settings.initialize_dynamic_settings()
        self.stats.reset_stats()
        self.stats.game_active = True
        self.obstacles.clear()
        self.player.rect.x      = self.settings.player_x
        self.player.rect.bottom = self.settings.ground_y
        self.player.velocity_y  = 0
        self.spawn_timer        = 0


if __name__ == "__main__":
    game = EndlessRunner()
    game.run_game()