import random
from time import sleep
import math
from enum import Enum, unique

import curses

from tiles import *
from maze_generation import generate_maze

# setup player
player = Player(5, 5)

# Pan when this close to a wall
PAN_TRIGGER_DIST = 10

# Move this far each time pan is triggered
# (may take multiple frames to move fully)
PAN_INCREMENT = 1

VIEW_DISTANCE = 20

@unique
class Outcome(Enum):
    WIN = 0
    LOSE = 1

def setup_curses():
    curses.start_color()
    curses.init_pair(Tile.COLOR_PAIR_NUMBER, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(DeathTile.COLOR_PAIR_NUMBER, curses.COLOR_RED, curses.COLOR_WHITE)
    curses.init_pair(Player.COLOR_PAIR_NUMBER, curses.COLOR_BLUE, curses.COLOR_WHITE)
    curses.init_pair(FinishTile.COLOR_PAIR_NUMBER, curses.COLOR_GREEN, curses.COLOR_WHITE)

    stdscr.keypad(True)
    curses.noecho()
    curses.curs_set(False)
    curses.cbreak()

def main(stdscr):
    setup_curses()

    outcome = Outcome.LOSE
    move_count = 0
    while True:
        stdscr.erase()
        for tile in maze_tiles:
            # We divide by 2 because characters are only half as wide as they are tall,
            # so this makes a perfect circle
            if distance_squared(tile.x / 2, tile.y, player.x / 2, player.y) < \
                VIEW_DISTANCE ** 2:
                tile.draw(stdscr, pan_x, pan_y)
                tile.update(stdscr, maze_tiles, player)
            
        pan_to_player()
        if not player.alive:
            outcome = Outcome.LOSE
            break
        elif player.finished:
            outcome = Outcome.WIN
            break

        stdscr.refresh()
        move_count += 1

    return outcome, move_count

def pan_to_player():
    global pan_x, pan_y

    true_x, true_y = player.get_true_pos(pan_x, pan_y)
    if true_x < PAN_TRIGGER_DIST:
        pan_x -= PAN_INCREMENT
    elif true_x >= SCREEN_WIDTH - PAN_TRIGGER_DIST:
        pan_x += PAN_INCREMENT
    if true_y < PAN_TRIGGER_DIST:
        pan_y -= PAN_INCREMENT
    elif true_y >= SCREEN_HEIGHT - PAN_TRIGGER_DIST:
        pan_y += PAN_INCREMENT

def show_outcome(outcome: Outcome, move_count: int):
    if outcome == Outcome.WIN:
        print('Yay you won')
        score = int(max(500 - move_count, 0) * 3.4253)
        print(f'You scored {score}')
    else:
        print('Lol you lost')

start_x, start_y, maze_tiles = generate_maze()
player.x = start_x
player.y = start_y
maze_tiles.append(player)

stdscr = curses.initscr()
SCREEN_HEIGHT, SCREEN_WIDTH = stdscr.getmaxyx()

# set these two now so we can use screen width & height
pan_x = player.x - SCREEN_WIDTH // 2
pan_y = player.y - SCREEN_HEIGHT // 2

win = curses.newwin(SCREEN_HEIGHT, SCREEN_WIDTH, 0, 0)

outcome, move_count = curses.wrapper(main)

show_outcome(outcome, move_count)