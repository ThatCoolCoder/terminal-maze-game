import curses

from game import TerminalMazeGame

if __name__ == '__main__':
    stdscr = curses.initscr()
    game = TerminalMazeGame()
    curses.wrapper(game.play_round)