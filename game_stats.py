class GameStats:
    def __init__(self):
        self.reset_stats()
        self.game_active = True

    def reset_stats(self):
        self.score = 0
