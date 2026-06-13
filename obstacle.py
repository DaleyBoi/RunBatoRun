import pygame

class Obstacle:
    def __init__(self, game):
        self.screen   = game.screen
        self.settings = game.settings
        w = self.settings.obstacle_width
        h = self.settings.obstacle_height
        self.rect = pygame.Rect(
            self.settings.screen_width,
            self.settings.ground_y - h,
            w, h
        )

    def update(self):
        self.rect.x -= self.settings.game_speed

    def draw(self):
        pygame.draw.rect(self.screen, (255, 0, 0), self.rect)
        pygame.draw.rect(self.screen, (180, 0, 0), self.rect, 3)
