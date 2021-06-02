import random

import curses

from blocks import *
from maze_generation import generate_maze

SCREEN_HEIGHT = 50
SCREEN_WIDTH = 100

# setup player
player = Player(1, 1)

maze_blocks = generate_maze()

def draw(stdscr):
    stdscr.erase()
    for block in maze_blocks:
        block.draw(stdscr)
    stdscr.refresh()

def main(stdscr):
    draw(stdscr)
    while True:
        player.move(stdscr, maze_blocks)
        draw(stdscr)
        if not player.alive:
            break

stdscr = curses.initscr()
stdscr.keypad(True)
curses.noecho()
curses.curs_set(False)
curses.cbreak()

win = curses.newwin(SCREEN_HEIGHT, SCREEN_WIDTH, 0, 0)

curses.wrapper(main)

print('Lol you die')