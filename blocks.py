import curses

class Block:
    def __init__(self, x:int, y:int, char='?'):
        self.x = x
        self.y = y
        self.char = char
    
    def draw(self, scr, pan_x=0, pan_y=0):
        # Drawing outside the screen will throw an error so catch that
        try:
            scr.move(self.y - pan_y, self.x - pan_x)
            scr.addch(self.char)
        except:
            pass
    
    def get_true_pos(self, pan_x=0, pan_y=0):
        return (self.x - pan_x, self.y - pan_y)

class WallBlock(Block):
    def __init__(self, x:int, y:int):
        # \u2588 is a filled-in-rectangle character
        super().__init__(x, y, '\u2588')

class DeathBlock(Block):
    def __init__(self, x:int, y:int):
        super().__init__(x, y, 'X')

class Player(Block):
    def __init__(self, x:int, y:int):
        super().__init__(x, y, '@')
        self.alive = True
        self.health = 1
    
    def will_hit_block(self, new_x, new_y, blocks):
        in_other_block = False
        for block in blocks:
            if block.x == new_x and \
                block.y == new_y and \
                type(block) == WallBlock:

                in_other_block = True
                break
        return in_other_block

    def will_die(self, new_x, new_y, blocks):
        touching_death_block = False
        for block in blocks:
            if block.x == new_x and \
                block.y == new_y and \
                type(block) == DeathBlock:

                touching_death_block = True
                break
        return touching_death_block
    
    def move(self, scr, blocks):
        key = scr.getkey()
        new_x = self.x
        new_y = self.y
        if key == 'KEY_UP':
            new_y -= 1
        elif key == 'KEY_DOWN':
            new_y += 1
        elif key == 'KEY_LEFT':
            new_x -= 1
        elif key == 'KEY_RIGHT':
            new_x += 1

        if self.will_hit_block(new_x, new_y, blocks):
            curses.beep()
        elif self.will_die(new_x, new_y, blocks):
            self.alive = False
        else:
            self.x = new_x
            self.y = new_y

