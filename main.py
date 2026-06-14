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
from music import play as play_music, fadeout as fadeout_music
from music import set_volume as set_music_volume
from sfx import load as load_sfx, play as play_sfx
from sfx import set_volume as set_sfx_volume
from cutscene import CutsceneScreen

ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets", "images")
FONT_PATH = os.path.join(os.path.dirname(__file__), "assets", "fonts", "PressStart2P.ttf")

# Colours
BLACK      = (  0,   0,   0)
WHITE      = (255, 255, 255)
YELLOW     = (255, 216,   0)
YELLOW_DIM = (160, 130,   0)


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


def make_scanlines(w, h):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(0, h, 2):
        pygame.draw.line(surf, (0, 0, 0, 40), (0, y), (w, y))
    return surf


class EndlessRunner:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        self.settings = Settings()
        self.screen   = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        global SCREEN_W, SCREEN_H
        SCREEN_W, SCREEN_H = self.screen.get_size()
        self.settings.screen_width  = SCREEN_W
        self.settings.screen_height = SCREEN_H
        self.settings.ground_y      = int(SCREEN_H * 0.81)
        pygame.display.set_caption("Run, Bato! Run!")
        self.clock = pygame.time.Clock()

        load_sfx()
        self._apply_audio_settings()
        self._load_background()

        self.player      = Player(self)
        self.stats       = GameStats()
        self.obstacles   = []
        self.spawn_timer = 0

        # Fonts
        self.f_score = pygame.font.Font(FONT_PATH, 18)
        self.f_small = pygame.font.Font(FONT_PATH, 11)

        # Scanlines
        self.scanlines = make_scanlines(SCREEN_W, SCREEN_H)

        # NEW BEST flash
        self.newbest_timer = 0

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

    def _apply_audio_settings(self):
        set_sfx_volume(self.settings.sound_volume)
        set_music_volume(self.settings.music_volume)

    def _toggle_fullscreen(self):
        self.settings.fullscreen = not self.settings.fullscreen
        if self.settings.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((1200, 800))

        global SCREEN_W, SCREEN_H
        SCREEN_W, SCREEN_H = self.screen.get_size()
        self.settings.screen_width = SCREEN_W
        self.settings.screen_height = SCREEN_H
        self.settings.ground_y = int(SCREEN_H * 0.81)
        self.scanlines = make_scanlines(SCREEN_W, SCREEN_H)
        self._load_background()
        if hasattr(self, "player"):
            self.player.rect.bottom = self.settings.ground_y
        return self.screen

    # ── Game loop ─────────────────────────────────────────────────────────
    def run_game(self):
        play_music("menu_music.mp3")
        menu   = MenuScreen(self.screen, self.clock, self.settings, self.stats,
                            self._apply_audio_settings, self._toggle_fullscreen)
        result = menu.run()
        if result == "quit":
            pygame.quit()
            sys.exit()
        fadeout_music(1000)
            
        cutscene = CutsceneScreen(self.screen, self.clock)
        cutscene.run()

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

    # ── Drawing ───────────────────────────────────────────────────────────
    def _draw_hud(self):
        def outline(text, color, x, y):
            for ox in [-1, 0, 1]:
                for oy in [-1, 0, 1]:
                    if ox == 0 and oy == 0:
                        continue
                    s = self.f_score.render(text, False, BLACK)
                    self.screen.blit(s, (x + ox, y + oy))
            s = self.f_score.render(text, False, color)
            self.screen.blit(s, (x, y))

        # Score box
        score_txt  = f"SCORE  {self.stats.score:06d}"
        best_txt   = f"BEST   {self.stats.best_score:06d}"

        # Box background
        box_w, box_h = 340, 70
        box = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        box.fill((0, 0, 0, 140))
        self.screen.blit(box, (16, 16))
        pygame.draw.rect(self.screen, YELLOW, (16, 16, box_w, box_h), 2)

        outline(score_txt, YELLOW, 26, 24)
        outline(best_txt,  WHITE,  26, 50)

        # NEW BEST flash
        if self.stats.new_best:
            self.newbest_timer += 1
            if (self.newbest_timer // 10) % 2 == 0:
                nb = self.f_small.render("★ NEW BEST! ★", False, YELLOW)
                self.screen.blit(nb, nb.get_rect(center=(SCREEN_W // 2, 30)))
            if self.newbest_timer > 180:
                self.newbest_timer  = 0
                self.stats.new_best = False

    def _update_screen(self):
        self.screen.fill((70, 160, 210))
        for layer in self.bg_layers:
            layer.draw(self.screen)

        pygame.draw.rect(
            self.screen, self.ground_color,
            (0, self.settings.ground_y,
             SCREEN_W, SCREEN_H - self.settings.ground_y)
        )
        pygame.draw.line(
            self.screen, (40, 40, 42),
            (0, self.settings.ground_y),
            (SCREEN_W, self.settings.ground_y), 3
        )

        self.player.draw()
        for obs in self.obstacles:
            obs.draw()

        self._draw_hud()
        self.screen.blit(self.scanlines, (0, 0))
        pygame.display.flip()

    # ── State transitions ─────────────────────────────────────────────────
    def _pause_game(self):
        self._update_screen()
        pause  = PauseScreen(self.screen, self.clock, self.settings,
                             self._apply_audio_settings, self._toggle_fullscreen)
        result = pause.run()
        if result == "menu":
            self._restart_game()
            play_music("menu_music.mp3")
            menu   = MenuScreen(self.screen, self.clock, self.settings, self.stats,
                                self._apply_audio_settings, self._toggle_fullscreen)
            action = menu.run()
            if action == "quit":
                pygame.quit()
                sys.exit()
            fadeout_music(1000)
            play_music("game.mp3")

    def _game_over(self):
        self.stats.update_best()
        play_sfx("hit")
        play_sfx("gameover")
        play_music("gameover.mp3", loop=False)
        self._update_screen()
        go     = GameOverScreen(self.screen, self.clock,
                                self.stats.score, self.stats.best_score,
                                self.stats.new_best)
        result = go.run()
        if result == "restart":
            self._restart_game()
            play_music("game.mp3")
        elif result == "menu":
            self._restart_game()
            play_music("menu_music.mp3")
            menu   = MenuScreen(self.screen, self.clock, self.settings, self.stats,
                                self._apply_audio_settings, self._toggle_fullscreen)
            action = menu.run()
            if action == "quit":
                pygame.quit()
                sys.exit()
            fadeout_music(1000)
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
        self.newbest_timer      = 0


if __name__ == "__main__":
    
    game = EndlessRunner()
    game.run_game()
