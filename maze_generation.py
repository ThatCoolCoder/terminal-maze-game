import random
from dataclasses import dataclass

from tiles import *
from misc import *

MIN_ROOMS = 40
MAX_ROOMS = 80
MIN_ROOM_SIZE = 6
MAX_ROOM_SIZE = 40
WALL_GAP_CHANCE = 1 / 10

MAX_X = 250
MAX_Y = 100

MIN_CONNECTIONS_PER_ROOM = 3
MAX_CONNECTIONS_PER_ROOM = 4

MAX_PASSAGE_LENGTH = 80
# passage is extended this many tiles past the edge of the room into the room
# (prevents enemies from walking into passages)
PASSAGE_INDENT = 1

DEATH_TILE_DENSITY = 1 / 30
MIN_ENEMIES_PER_ROOM = 2
MAX_ENEMIES_PER_ROOM = 5
ENEMY_TYPES = [MovingEnemy, ChasingEnemy]

FINISH_TILE_DENSITY = 1 / 10

@dataclass
class Room:
    x: int
    y: int
    width: int
    height: int

    @property
    def center_x(self):
        return self.x + self.width // 2

    @property
    def center_y(self):
        return self.y + self.height // 2

    @property
    def right_x(self):
        return self.x + self.width

    @property
    def bottom_y(self):
        return self.y + self.height
    
    @property
    def area(self):
        return self.width * self.height

def generate_maze():
    rooms = generate_rooms()
    start_x, start_y = generate_start_point(rooms)
    tiles = generate_tiles(rooms)
    tiles += generate_passages(rooms)
    tiles += generate_death_tiles(rooms)
    tiles += generate_enemies(rooms)
    tiles += generate_finish_tiles(rooms)
    return start_x, start_y, tiles

def generate_rooms():
    # This will generate a bunch of Room objects which do not intersect or touch
    rooms = []
    room_count = random.randint(MIN_ROOMS, MAX_ROOMS)
    for room_num in range(room_count):
        room_width = random.randint(MIN_ROOM_SIZE, MAX_ROOM_SIZE)
        room_height = random.randint(MIN_ROOM_SIZE, MAX_ROOM_SIZE) // 2
        room_x = random.randint(0, MAX_X)
        room_y = random.randint(0, MAX_Y)
        new_room = Room(room_x, room_y, room_width, room_height)

        if not any(rooms_touch(room, new_room) for room in rooms):
            rooms.append(new_room)
    return rooms

def rooms_touch(room_1, room_2):
    # Whether the two rooms overlap or touch by an edge
    # There are +1's everywhere to stop them from touching by an edge
    return room_1.right_x + 1 >= room_2.x and \
        room_1.x <= room_2.right_x + 1 and \
        room_1.bottom_y + 1 >= room_2.y and \
        room_1.y <= room_2.bottom_y + 1

def generate_start_point(rooms):
    # If there are no rooms then give up
    if len(rooms) == 0:
        return (0, 0)
    # Else choose a random room and start in the middle of it
    else:
        room = random.choice(rooms)
        start_x = room.x + room.width // 2
        start_y = room.y + room.height // 2
        return (start_x, start_y)

def generate_tiles(rooms):
    tiles = []

    # Fill the rooms with floor tiles
    for room in rooms:
        for col_idx in range(room.width + 1):
            for row_idx in range(room.height + 1):
                tiles.append(FloorTile(col_idx + room.x, row_idx + room.y))

    return tiles

def generate_passages(rooms):
    # Don't bother building passages if there's only one room (or none)
    if len(rooms) <= 1:
        return []

    tiles = []
    for room in rooms:
        available_directions = [Direction.LEFT, Direction.RIGHT, Direction.UP, Direction.DOWN]
        for _ in range(random.randint(MIN_CONNECTIONS_PER_ROOM, MAX_CONNECTIONS_PER_ROOM)):
            passage_direction = random.choice(available_directions)
            tiles += generate_passage(room, passage_direction, rooms)
            available_directions.remove(passage_direction)
    return tiles

def generate_passage(start_room: Room, direction: Direction, rooms):
    # Calc start point of the passage
    if direction == Direction.LEFT:
        crnt_position_x = start_room.x + (PASSAGE_INDENT - 1)
        crnt_position_y = start_room.center_y
    elif direction == Direction.UP:
        crnt_position_x = start_room.center_x
        crnt_position_y = start_room.y + (PASSAGE_INDENT - 1)
    elif direction == Direction.RIGHT:
        crnt_position_x = start_room.right_x - (PASSAGE_INDENT - 1)
        crnt_position_y = start_room.center_y
    else:
        crnt_position_x = start_room.center_x
        crnt_position_y = start_room.bottom_y - (PASSAGE_INDENT - 1)
    
    tiles = []
    success = False
    passage_length = 0
    consecutive_room_hits = 0 # counts how many consecutive steps we've been in a room

    while True:
        tiles.append(PassageFloorTile(crnt_position_x, crnt_position_y, direction))
        passage_length += 1
        if passage_length > MAX_PASSAGE_LENGTH:
            break

        if direction == Direction.LEFT:
            crnt_position_x -= 1
        elif direction == Direction.UP:
            crnt_position_y -= 1
        elif direction == Direction.RIGHT:
            crnt_position_x += 1
        else:
            crnt_position_y += 1
        
        in_room = False
        for room in rooms:
            if room == start_room:
                continue
            if room.x <= crnt_position_x and crnt_position_x <= room.right_x and \
                room.y <= crnt_position_y and crnt_position_y <= room.bottom_y:
                in_room = True
        
        if in_room:
            consecutive_room_hits += 1
        else:
            consecutive_room_hits = 0

        if consecutive_room_hits > PASSAGE_INDENT:
            success = True
            break
    
    # Only add the passage if it hit another room
    if success:
        return tiles
    else:
        return []

def generate_death_tiles(rooms):
    tiles = []
    for room in rooms:
        death_tile_amount = int(room.area * DEATH_TILE_DENSITY)
        for i in range(death_tile_amount):
            x = random.randint(0, room.width) + room.x
            y = random.randint(0, room.height) + room.y
            tiles.append(DeathTile(x, y))
    return tiles

def generate_enemies(rooms):
    tiles = []
    for room in rooms:
        enemy_amount = random.randint(MIN_ENEMIES_PER_ROOM, MAX_ENEMIES_PER_ROOM)
        for i in range(enemy_amount):
            x = random.randint(0, room.width) + room.x
            y = random.randint(0, room.height) + room.y
            enemy_type = random.choice(ENEMY_TYPES)
            tiles.append(enemy_type(x, y))
    return tiles

def generate_finish_tiles(rooms):
    tiles = []
    rooms_with_finish_point = random.sample(rooms, int(len(rooms) * FINISH_TILE_DENSITY))
    for room in rooms_with_finish_point:
        x_pos = random.randint(room.x, room.right_x)
        y_pos = random.randint(room.y, room.bottom_y)
        tiles.append(FinishTile(x_pos, y_pos))
    return tiles
