from enum import Enum
import random
from time import sleep
import textwrap
import curses

from tiles import *
from maze_generation import generate_maze

@unique
class Outcome(Enum):
    WIN = 0
    LOSE = 1
    QUIT = 2

class TerminalMazeGame:
    # Pan when this close to a screen edge
    PAN_TRIGGER_DIST_X = 20
    PAN_TRIGGER_DIST_Y = 10

    # Move this far each time pan is triggered
    # (may take multiple frames to move fully)
    PAN_INCREMENT = 1

    VIEW_DISTANCE = 20

    paused = True

    def play_round(self, stdscr):
        self.stdscr = stdscr

        self.__setup_curses()
        self.__update_screen_size()

        start_x, start_y, self.maze_tiles = generate_maze()
        self.player = Player(start_x, start_y)
        self.maze_tiles.append(self.player)
        self.outcome = Outcome.QUIT
        self.move_count = 0

        self.paused = True

        # Area which is visible to player
        self.lit_area_x = 0
        self.lit_area_y = 0

        self.pan_x = self.player.x + random.randint(-50, 50)
        self.pan_y = self.player.y + random.randint(-25, 25)
        self.__initial_pan_to_player()

        self.paused = False
        while True:
            self.stdscr.erase()
            self.__update_screen_size()

            self.__draw_tiles()

            self.__draw_hud()
            # Update player separately after drawing hud,
            # as it blocks for input and we don't want that in the middle of the drawing loop
            try:
                self.player.player_update(self.stdscr, self.maze_tiles)
            except KeyboardInterrupt:
                break
            self.lit_area_x = self.player.x
            self.lit_area_y = self.player.y

            self.__pan_to_player()

            if not self.player.alive:
                self.outcome = Outcome.LOSE
                break
            elif self.player.finished:
                self.outcome = Outcome.WIN
                break

            self.stdscr.refresh()
            self.move_count += 1
    
        self.__show_outcome()

    def __setup_curses(self):
        curses.start_color()
        curses.init_pair(Tile.COLOR_PAIR_NUMBER, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(DeathTile.COLOR_PAIR_NUMBER, curses.COLOR_RED, curses.COLOR_WHITE)
        curses.init_pair(Player.COLOR_PAIR_NUMBER, curses.COLOR_BLUE, curses.COLOR_WHITE)
        curses.init_pair(FinishTile.COLOR_PAIR_NUMBER, curses.COLOR_GREEN, curses.COLOR_WHITE)

        self.stdscr.keypad(True)
        curses.noecho()
        curses.curs_set(False)
        curses.cbreak()

    def __initial_pan_to_player(self):
        target_x = self.player.x - self.screen_width // 2
        target_y = self.player.y - self.screen_height // 2

        while True:
            delta_x = self.pan_x - target_x
            delta_y = self.pan_y - target_y

            if delta_x > 1:
                self.pan_x -= 1
            elif delta_x < 1:
                self.pan_x += 1

            if delta_y > 1:
                self.pan_y -= 1
            elif delta_y < 1:
                self.pan_y += 1

            self.lit_area_x = self.pan_x + self.screen_width // 2
            self.lit_area_y = self.pan_y + self.screen_height // 2

            self.stdscr.clear()
            self.__draw_tiles()

            self.stdscr.move(0, 0)

            if abs(delta_x) <= 1 and abs(delta_y) <= 1:
                break

            sleep(0.01)
            self.stdscr.refresh()

    def __update_screen_size(self):
        self.screen_height, self.screen_width = self.stdscr.getmaxyx()

    def __draw_tiles(self):
        for tile in self.maze_tiles:
            # We divide by 2 because characters are only half as wide as they are tall,
            # so this makes a perfect circle
            if distance_squared(tile.x / 2, tile.y, self.lit_area_x / 2, self.lit_area_y) < \
                self.VIEW_DISTANCE ** 2:
                tile.draw(self.stdscr, self.pan_x, self.pan_y)
                if not self.paused:
                    tile.update(self.stdscr, self.maze_tiles, self.player)

    def __draw_hud(self):
        message = 'Arrow keys to move. Q to quit. ' + \
            'Your goal: get to the green F without dying. ' + \
            f'Move count: {self.move_count}'
        lines = textwrap.wrap(message, self.screen_width)
        for idx, line in enumerate(lines):
            self.stdscr.move(self.screen_height - (len(lines) - idx), 0)
        self.stdscr.addstr(line, curses.color_pair(0))

    def __pan_to_player(self):
        true_x, true_y = self.player.get_true_pos(self.pan_x, self.pan_y)
        if true_x < self.PAN_TRIGGER_DIST_X:
            self.pan_x -= self.PAN_INCREMENT
        elif true_x >= self.screen_width - self.PAN_TRIGGER_DIST_X:
            self.pan_x += self.PAN_INCREMENT
        if true_y < self.PAN_TRIGGER_DIST_Y:
            self.pan_y -= self.PAN_INCREMENT
        elif true_y >= self.screen_height - self.PAN_TRIGGER_DIST_Y:
            self.pan_y += self.PAN_INCREMENT

    def __show_outcome(self):
        self.stdscr.clear()

        if self.outcome == Outcome.QUIT:
            return

        text = 'Haha you died'
        if self.outcome == Outcome.WIN:
            text = 'Yay you won. '
            score = int(max(500 - self.move_count, 0) * 3.4253)
            text += f'You scored {score}'
        
        text += '\nPress q to exit'
        self.stdscr.move(self.screen_height // 2, 0)
        self.stdscr.addstr(center_text(text, self.screen_width))

        self.stdscr.refresh()

        while True:
            if self.stdscr.getkey() == 'q':
                break

def center_text(text: str, total_width: int):
    lines = []
    for line in text.split('\n'):
        padding_total = total_width - len(line)
        padding_l = padding_total // 2
        lines.append(' ' * padding_l + line)
    return '\n'.join(lines)
