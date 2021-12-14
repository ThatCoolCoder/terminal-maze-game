import random
from abc import ABC, abstractmethod

import curses

from misc import *

class Tile:
    COLOR_PAIR_NUMBER = 1

    def __init__(self, x: int, y: int, char='?'):
        self.x = x
        self.y = y
        self.char = char
    
    def update(self, scr, tiles, *args):
        pass
    
    def draw(self, scr, pan_x=0, pan_y=0):
        # Drawing outside the screen will throw an error so catch that
        try:
            scr.move(self.y - pan_y, self.x - pan_x)
            scr.addch(self.char, curses.color_pair(self.COLOR_PAIR_NUMBER))
        except:
            pass
    
    def get_true_pos(self, pan_x=0, pan_y=0):
        return (self.x - pan_x, self.y - pan_y)

class FloorTile(Tile):
    def __init__(self, x: int, y: int):
        # \u2588 is a filled-in-rectangle character
        super().__init__(x, y, '\u2588')

class PassageFloorTile(Tile):
    # A floor tile used for in and around entrances of passages
    def __init__(self, x: int, y: int, direction: Direction):
        # \u2587 and \u2589 are a nearly-filled-in-rectangle characters
        if direction == direction.UP or direction == direction.DOWN:
            char = '\u2587'
        else:
            char = '\u2589'
        super().__init__(x, y, char)

class DeathTile(Tile):
    COLOR_PAIR_NUMBER = 2
    def __init__(self, x: int, y: int):
        super().__init__(x, y, 'X')

class FinishTile(Tile):
    COLOR_PAIR_NUMBER = 4
    def __init__(self, x: int, y: int):
        super().__init__(x, y, '\u2691')

class TileWalker(ABC, Tile):
    # Abstract class for anything that can walk on the tiles
    KILLED_BY = []
    COLLIDES_WITH = []
    WALKABLE_TILES = []

    def __init__(self, x: int, y: int, char='W'):
        super().__init__(x, y, char)
    
    def can_walk_to(self, new_x, new_y, tiles):
        is_floor = False
        no_obstacles = True
        for tile in tiles:
            if tile.x == new_x and tile.y == new_y:
                if type(tile) in self.WALKABLE_TILES:
                    is_floor = True
                elif type(tile) in self.COLLIDES_WITH:
                    no_obstacles = False
                    break
        return is_floor and no_obstacles

    def check_if_dead(self, new_x, new_y, tiles):
        touching_death_tile = False
        for tile in tiles:
            if tile.x == new_x and \
                tile.y == new_y and \
                type(tile) in self.KILLED_BY:

                touching_death_tile = True
                break
        return touching_death_tile

    @abstractmethod
    def update(self, src, tiles, *args):
        pass

class Player(TileWalker):
    COLOR_PAIR_NUMBER = 3

    def __init__(self, x: int, y: int, char='@'):
        super().__init__(x, y, char)
        self.alive = True
        self.health = 1
        self.finished = False

        # These are in __init__ so they can reference stuff defined later
        self.KILLED_BY = [DeathTile, MovingEnemy, ChasingEnemy]
        self.COLLIDES_WITH = [DeathTile, MovingEnemy, ChasingEnemy]
        self.WALKABLE_TILES = [FloorTile, PassageFloorTile]

    def check_if_finished(self, tiles):
        finished = False
        for tile in tiles:
            if tile.x == self.x and \
                tile.y == self.y and \
                type(tile) == FinishTile:

                finished = True
                break
        return finished
    
    def keybinds(self, scr, tiles):
        key = scr.getkey()
        new_x = self.x
        new_y = self.y
        moved = False
        if key == 'KEY_UP':
            new_y -= 1
            moved = True
        elif key == 'KEY_DOWN':
            new_y += 1
            moved = True
        elif key == 'KEY_LEFT':
            new_x -= 1
            moved = True
        elif key == 'KEY_RIGHT':
            new_x += 1
            moved = True

        return (new_x, new_y, moved)

    def update(self, scr, tiles, *args):
        new_x, new_y, moved = self.keybinds(scr, tiles)
        if moved:
            if self.can_walk_to(new_x, new_y, tiles):
                self.x = new_x
                self.y = new_y
            else:
                curses.beep()
            # Check both the current position and the new one
            # In case death things have moved while player stood still
            if self.check_if_dead(new_x, new_y, tiles) or \
                self.check_if_dead(self.x, self.y, tiles):
                self.alive = False
        self.finished = self.check_if_finished(tiles)

class ChasingEnemy(TileWalker):
    COLOR_PAIR_NUMBER = 2
    MOVEMENT_CHANCE = 0.5
    PLAYER_DETECTION_DIST = 30

    def __init__(self, x: int, y: int):
        super().__init__(x, y, char='!')

        self.COLLIDES_WITH = [MovingEnemy, ChasingEnemy, DeathTile, PassageFloorTile]
        self.WALKABLE_TILES = [FloorTile]
    
    def can_see_player(self, player):
        return distance_squared(self.x, self.y, player.x, player.y) < \
            self.PLAYER_DETECTION_DIST ** 2
    
    def update(self, scr, tiles, player):
        if random.uniform(0, 1) < self.MOVEMENT_CHANCE:
            if self.can_see_player(player):
                new_x = self.x
                new_y = self.y
                if player.x < self.x:
                    new_x -= 1
                elif player.x > self.x:
                    new_x += 1
                if player.y < self.y:
                    new_y -= 1
                elif player.y > self.y:
                    new_y += 1

                if self.can_walk_to(new_x, new_y, tiles):
                    self.x = new_x
                    self.y = new_y
                elif self.can_walk_to(new_x, self.y, tiles):
                    self.x = new_x
                elif self.can_walk_to(self.x, new_y, tiles):
                    self.y = new_y

class MovingEnemy(TileWalker):
    COLOR_PAIR_NUMBER = 2
    DIRECTION_TO_CHAR = {
        Direction.LEFT : '<',
        Direction.RIGHT : '>',
        Direction.UP : '^',
        Direction.DOWN : 'v'
    }

    def __init__(self, x: int, y: int, direction: Direction = None):
        # \u25c6 is a square tilted 45°
        super().__init__(x, y, char='\u25c6')

        self.COLLIDES_WITH = [MovingEnemy, ChasingEnemy, DeathTile, PassageFloorTile]
        self.WALKABLE_TILES = [FloorTile]

        if direction is None:
            direction = random.choice(list(Direction))
        self.direction = direction
    
    def update(self, src, tiles, player):
        self.char = self.DIRECTION_TO_CHAR[self.direction]

        new_x = self.x
        new_y = self.y
        if self.direction == Direction.LEFT:
            new_x -= 1
        elif self.direction == Direction.RIGHT:
            new_x += 1
        elif self.direction == Direction.UP:
            new_y -= 1
        elif self.direction == Direction.DOWN:
            new_y += 1

        if self.can_walk_to(new_x, new_y, tiles):
            self.x = new_x
            self.y = new_y
        else:
            old_dir = self.direction.name
            self.direction = Direction.opposite(self.direction)