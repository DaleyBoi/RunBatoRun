class Settings:
    def __init__(self):
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_color = (135, 206, 235)
        self.fps = 60
        self.sound_volume = 0.4
        self.music_volume = 0.5
        self.fullscreen = True

        self.ground_y = 650

        self.player_width = 80
        self.player_height = 94
        self.player_x = 150
        self.jump_power = -18
        self.gravity = 0.8

        self.obstacle_width = 50
        self.obstacle_height = 60
        self.obstacle_spawn_time = 90

        self.speedup_scale = 1.1
        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        self.game_speed = 7

    def increase_speed(self):
        self.game_speed *= self.speedup_scale
