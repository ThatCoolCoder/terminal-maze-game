import random

import curses

from tiles import *
from maze_generation import generate_maze

stdscr = curses.initscr()
SCREEN_HEIGHT, SCREEN_WIDTH = stdscr.getmaxyx()

# setup player
player = Player(5, 5)

# Pan when this close to a wall
PAN_TRIGGER_DIST = min(SCREEN_WIDTH, SCREEN_HEIGHT) // 4

# Move this far each time pan is triggered
# (may take multiple frames to move fully)
PAN_INCREMENT = 1

pan_x = 0
pan_y = 0

def main(stdscr):
    while True:
        stdscr.erase()
        for tile in maze_tiles:
            tile.draw(stdscr, pan_x, pan_y)
            tile.update(stdscr, maze_tiles, player)
            
        pan_to_player()
        if not player.alive:
            break

        stdscr.refresh()

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

curses.start_color()
curses.init_pair(Tile.COLOR_PAIR_NUMBER, curses.COLOR_WHITE, curses.COLOR_BLACK)
curses.init_pair(DeathTile.COLOR_PAIR_NUMBER, curses.COLOR_RED, curses.COLOR_WHITE)
curses.init_pair(Player.COLOR_PAIR_NUMBER, curses.COLOR_BLUE, curses.COLOR_WHITE)

stdscr.keypad(True)
curses.noecho()
curses.curs_set(False)
curses.cbreak()

start_x, start_y, maze_tiles = generate_maze()
player.x = start_x
player.y = start_y
pan_x = player.x - PAN_INCREMENT - SCREEN_WIDTH // 2
pan_y = player.y - PAN_INCREMENT - SCREEN_HEIGHT // 2
maze_tiles.append(player)

win = curses.newwin(SCREEN_HEIGHT, SCREEN_WIDTH, 0, 0)

curses.wrapper(main)