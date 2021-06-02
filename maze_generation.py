import random
from dataclasses import dataclass

from blocks import *

MIN_ROOMS = 40
MAX_ROOMS = 80
MIN_ROOM_SIZE = 6
MAX_ROOM_SIZE = 40
WALL_GAP_CHANCE = 1 / 10

MAX_X = 250
MAX_Y = 100

MIN_CONNECTIONS_PER_ROOM = 1
MAX_CONNECTIONS_PER_ROOM = 4

DEATH_BLOCK_DENSITY = 1 / 30

PASSAGE_WIDTH = 5

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

@dataclass
class Passage:
    start: Room
    end: Room

def generate_maze():
    rooms = generate_rooms()
    passages = generate_passages(rooms)
    blocks = generate_blocks(rooms, passages)
    blocks += generate_death_blocks()
    return blocks

def generate_rooms():
    rooms = []
    room_count = random.randint(MIN_ROOMS, MAX_ROOMS)
    for room_num in range(room_count):
        room_width = random.randint(MIN_ROOM_SIZE, MAX_ROOM_SIZE)
        room_height = random.randint(MIN_ROOM_SIZE, MAX_ROOM_SIZE) // 2
        room_x = random.randint(0, MAX_X)
        room_y = random.randint(0, MAX_Y)
        new_room = Room(room_x, room_y, room_width, room_height)

        if not any(rooms_intersect(room, new_room) for room in rooms):
            rooms.append(new_room)
    return rooms

def rooms_intersect(room_1, room_2):
    return room_1.right_x >= room_2.x and \
        room_1.x <= room_2.right_x and \
        room_1.bottom_y >= room_2.y and \
        room_1.y <= room_2.bottom_y

def generate_passages(rooms):
    passages = []
    for room in rooms:
        connection_amount = random.randint(MIN_CONNECTIONS_PER_ROOM,
            MAX_CONNECTIONS_PER_ROOM)
        other_rooms = [i for i in rooms if i != room]
        for i in range(connection_amount):
            other_room = random.choice(other_rooms)
            passage = Passage(room, other_room)
            passages.append(passage)
    return passages

def generate_blocks(rooms, passages):
    blocks = []

    # First create the outline of the rooms
    for room in rooms:
        for col_idx in range(room.width):
            # Top wall
            if random.uniform(0, 1) > WALL_GAP_CHANCE:
                blocks.append(WallBlock(col_idx + room.x, room.y))
            # Bottom wall
            if random.uniform(0, 1) > WALL_GAP_CHANCE:
                blocks.append(WallBlock(col_idx + room.x, room.bottom_y))
        for row_idx in range(room.height):
            # Left wall
            if random.uniform(0, 1) > WALL_GAP_CHANCE:
                blocks.append(WallBlock(room.x, row_idx + room.y))
            # Right wall
            if random.uniform(0, 1) > WALL_GAP_CHANCE:
                blocks.append(WallBlock(room.right_x, row_idx + room.y))
        # Bottom right corner requires special doing
        blocks.append(WallBlock(room.right_x, room.bottom_y))
    
    for passage in passages:
        # first find distance in 4 directions from start to end
        top_dist = passage.start.y - passage.end.bottom_y
        bottom_dist = passage.end.y - passage.start.bottom_y
        left_dist = passage.start.x - passage.end.right_x
        right_dist = passage.end.x - passage.start.right_x

        # draw a line of blocks from top middle of start to right middle of end
        crnt_y = passage.start.y
        crnt_x = (passage.start.x + passage.start.right_x) // 2
        end_y = (passage.end.y + passage.end.bottom_y) // 2
        end_x = passage.end.x
        while crnt_y != end_y:
            if crnt_y < end_y:
                crnt_y += 1
            else:
                crnt_y -= 1
            #blocks.append(DeathBlock(crnt_x, crnt_y))
        while crnt_x != end_x:
            if crnt_x < end_x:
                crnt_x += 1
            else:
                crnt_x -= 1
            #blocks.append(DeathBlock(crnt_x, crnt_y))

    return blocks

def generate_death_blocks():
    blocks = []
    death_block_amount = int(MAX_X * MAX_Y * DEATH_BLOCK_DENSITY)
    for i in range(death_block_amount):
        x = random.randint(0, MAX_X)
        y = random.randint(0, MAX_Y)
        blocks.append(DeathBlock(x, y))
    return blocks