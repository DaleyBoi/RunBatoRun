import sys
import os
import pygame
from settings import Settings
from player import Player
from obstacle import Obstacle
from game_stats import GameStats
from menu import MenuScreen
from pause import PauseScreen
from gameover import GameOverScreen
from music import play as play_music, stop as stop_music
from sfx import load as load_sfx, play as play_sfx

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
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        self.settings = Settings()
        self.screen   = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Run, Bato! Run!")
        self.clock    = pygame.time.Clock()

        load_sfx()
        self._load_background()

        self.player      = Player(self)
        self.stats       = GameStats()
        self.obstacles   = []
        self.spawn_timer = 0
        font_path       = os.path.join(os.path.dirname(__file__), "assets", "fonts", "PressStart2P.ttf")
        self.font       = pygame.font.Font(font_path, 20)
        self.small_font = pygame.font.Font(font_path, 12)

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
        play_music("menu.mp3")
        menu   = MenuScreen(self.screen, self.clock)
        result = menu.run()
        if result == "quit":
            pygame.quit()
            sys.exit()

        play_music("game.mp3")

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
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    sys.exit()
                elif event.key == pygame.K_ESCAPE:
                    if self.stats.game_active:
                        self._pause_game()
                elif event.key == pygame.K_SPACE:
                    if self.stats.game_active:
                        self.player.jump()
                        play_sfx("jump")

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
                self._game_over()

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

        pygame.display.flip()

    def _pause_game(self):
        self._update_screen()
        pause  = PauseScreen(self.screen, self.clock)
        result = pause.run()
        if result == "resume":
            pass
        elif result == "menu":
            self._restart_game()
            play_music("menu.mp3")
            menu   = MenuScreen(self.screen, self.clock)
            action = menu.run()
            if action == "quit":
                pygame.quit()
                sys.exit()
            play_music("game.mp3")

    def _game_over(self):
        play_sfx("hit")
        play_sfx("gameover")
        play_music("gameover.mp3", loop=False)
        self._update_screen()
        go     = GameOverScreen(self.screen, self.clock, self.stats.score)
        result = go.run()
        if result == "restart":
            self._restart_game()
            play_music("game.mp3")
        elif result == "menu":
            self._restart_game()
            play_music("menu.mp3")
            menu   = MenuScreen(self.screen, self.clock)
            action = menu.run()
            if action == "quit":
                pygame.quit()
                sys.exit()
            play_music("game.mp3")
        elif result == "quit":
            pygame.quit()
            sys.exit()

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