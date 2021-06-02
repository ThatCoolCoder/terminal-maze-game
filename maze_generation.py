import random
from dataclasses import dataclass

from blocks import *

MIN_ROOMS = 5
MAX_ROOMS = 10
MIN_ROOM_SIZE = 6
MAX_ROOM_SIZE = 20

@dataclass
class Room:
    x: int
    y: int
    width: int
    height: int

    @property
    def right_x(self):
        return self.x + self.width

    @property
    def bottom_y(self):
        return self.y + self.height

def generate_maze():
    blocks = []
    return blocks

def generate_rooms():
    rooms = []
    room_count = random.randint(MIN_ROOMS, MAX_ROOMS)
    for room_num in range(room_count):
        room_width = random.randint(MIN_ROOM_SIZE, MAX_ROOM_SIZE)
        room_height = random.randint(MIN_ROOM_SIZE, MAX_ROOM_SIZE)
    return rooms