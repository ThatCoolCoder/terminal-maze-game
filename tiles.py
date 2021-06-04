import random

import curses

class Tile:
    COLOR_PAIR_NUMBER = 1

    def __init__(self, x:int, y:int, char='?'):
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
    def __init__(self, x:int, y:int):
        # \u2588 is a filled-in-rectangle character
        super().__init__(x, y, '\u2588')

class DeathTile(Tile):
    COLOR_PAIR_NUMBER = 2
    def __init__(self, x:int, y:int):
        super().__init__(x, y, 'X')

class FinishTile(Tile):
    COLOR_PAIR_NUMBER = 4
    def __init__(self, x:int, y:int):
        super().__init__(x, y, '\u2691')

class Player(Tile):
    COLOR_PAIR_NUMBER = 3

    def __init__(self, x:int, y:int, controllable=True, char='@'):
        super().__init__(x, y, char)
        self.controllable = controllable
        self.alive = True
        self.health = 1
        self.finished = False

        # These are in __init__ so they can reference stuff defined later
        self.KILLED_BY = [DeathTile, MovingEnemy]
        self.COLLIDES_WITH = [DeathTile, MovingEnemy]
    
    def can_walk_to(self, new_x, new_y, tiles):
        is_floor = False
        no_obstacles = True
        for tile in tiles:
            if tile.x == new_x and tile.y == new_y:
                if type(tile) == FloorTile:
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
        if self.controllable:
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

class MovingEnemy(Player):
    COLOR_PAIR_NUMBER = 2
    MOVEMENT_CHANCE = 0.5
    PLAYER_DETECTION_DIST = 30

    def __init__(self, x:int, y:int):
        super().__init__(x, y, char='!')

        # This has to be in __init__ so we can include MovingEnemy
        self.COLLIDES_WITH = [MovingEnemy, DeathTile]
    
    def can_see_player(self, player):
        dist_sq = (self.x - player.x) ** 2 + (self.y - player.y) ** 2
        return dist_sq < self.PLAYER_DETECTION_DIST ** 2
    
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