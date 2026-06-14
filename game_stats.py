import os

SAVE_FILE = os.path.join(os.path.dirname(__file__), "best_score.txt")


class GameStats:
    def __init__(self):
        self.best_score  = self._load_best()
        self.reset_stats()
        self.game_active = True
        self.new_best    = False

    def reset_stats(self):
        self.score    = 0
        self.new_best = False

    def update_best(self):
        if self.score > self.best_score:
            self.best_score = self.score
            self.new_best   = True
            self._save_best()

    def _load_best(self):
        try:
            with open(SAVE_FILE, "r") as f:
                return int(f.read().strip())
        except Exception:
            return 0

    def _save_best(self):
        try:
            with open(SAVE_FILE, "w") as f:
                f.write(str(self.best_score))
        except Exception:
            pass

    def delete_save_data(self):
        self.best_score = 0
        self.new_best = False
        try:
            with open(SAVE_FILE, "w") as f:
                f.write("0")
        except Exception:
            pass
