from enum import Enum, unique
from dataclasses import dataclass

# wrote this file without intellisense or testing it so have no idea if it is correct.
# also need to figure out how to properly do data typing

@unique
class ScoreProfile(Enum):
    Defualt = 0

@dataclass
class ScoreHistory:
    profiles: dict # dict of ScoreProfile to list of Score    

@dataclass
class Score:
    value: int
    date = 5 # todo: how do dates work in python?

class ScoreManager:
    # should this class be static or not?
    score_file_path = os.path.join(get_settings_dir_somehow(), 'terminal-maze-game.json',  # todo: import os or maybe use proper paths instead

    def load_score_history(self) -> ScoreHistory:
        return ScoreHistory()

    def save_score_history(self, score_history)
        pass
