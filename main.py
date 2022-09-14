import curses

from game import TerminalMazeGame

def main(stdscr):
    game = TerminalMazeGame(stdscr)
    game.mainloop()

if __name__ == '__main__':
    stdscr = curses.initscr()
    curses.wrapper(main)