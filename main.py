import random

import curses

from blocks import *
from maze_generation import generate_maze

# setup player
player = Player(5, 5)

# Pan when this close to a wall
PAN_TRIGGER_DIST = 4

# Move this far each time pan is triggered
PAN_INCREMENT = 4

pan_x = 0
pan_y = 0

def draw():
    stdscr.erase()
    for block in maze_blocks:
        block.draw(stdscr, pan_x, pan_y)
    stdscr.refresh()

def main(stdscr):
    draw()
    while True:
        player.move(stdscr, maze_blocks)
        pan_to_player()
        draw()
        if not player.alive:
            break

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

stdscr = curses.initscr()
stdscr.keypad(True)
curses.noecho()
curses.curs_set(False)
curses.cbreak()

maze_blocks = generate_maze()
maze_blocks.append(player)
SCREEN_HEIGHT, SCREEN_WIDTH = stdscr.getmaxyx()

win = curses.newwin(SCREEN_HEIGHT, SCREEN_WIDTH, 0, 0)

curses.wrapper(main)

print('lol you die')