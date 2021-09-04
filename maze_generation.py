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

MIN_CONNECTIONS_PER_ROOM = 1
MAX_CONNECTIONS_PER_ROOM = 1

MAX_PASSAGE_LENGTH = 80

DEATH_TILE_DENSITY = 1 / 30
MIN_ENEMIES_PER_ROOM = 1
MAX_ENEMIES_PER_ROOM = 3

FINISH_TILE_AMOUNT = 10

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

@dataclass
class Passage:
    start_x: int
    start_y: int
    end_x: int
    end_y: int

def generate_maze():
    rooms = generate_rooms()
    start_x, start_y = generate_start_point(rooms)
    tiles = generate_tiles(rooms)
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

    for room in rooms:
        # First fill the rooms with floor tiles
        for col_idx in range(room.width + 1):
            for row_idx in range(room.height + 1):
                tiles.append(FloorTile(col_idx + room.x, row_idx + room.y))
        
        # Don't bother building passages if there's only one room
        if len(rooms) == 1:
            continue

        # Choose an amount of passages from this room
        connection_amount = int(random.uniform(MIN_CONNECTIONS_PER_ROOM,
            MAX_CONNECTIONS_PER_ROOM))
        
        # Find distance to all rooms for later
        room_distances = []
        for other_room in rooms:
            data = {
                'dist' : calc_required_passage_length(room, other_room),
                'room' : other_room
            }
            room_distances.append(data)

        # Then sort the rooms and choose some

        # I can't find how to sort a list of dicts by one of their keys
        # so just find what the index was originally to calc dist
        closest_room_distances = room_distances.copy()
        closest_room_distances = sort_based_on_key(closest_room_distances, 'dist')

        # Definitely connect to the very closest
        tiles += generate_passage(room, room_distances[0]['room'])

        closest_room_distances = closest_room_distances[1:connection_amount * 2]
        rooms_to_connect_with = random.sample(closest_room_distances,
            connection_amount - 1)
        
        for other_room in rooms_to_connect_with:
            tiles += generate_passage(room, other_room['room'])

    return tiles

def calc_required_passage_length(start_room, end_room):
    return abs(start_room.x - end_room.x) + abs(start_room.y - end_room.y)

def generate_passage(start_room, end_room):
    # This is a very long and probably bad function
    # that will generate a neat-looking passage from start to end

    tiles = []

    x_dist = abs(end_room.center_x - start_room.center_x)
    y_dist = abs(end_room.center_y - start_room.center_y)

    # If this passage will be more vertical
    if x_dist < y_dist:
        start_x = start_room.center_x
        # If going up
        if end_room.center_y < start_room.center_y:
            start_y = start_room.y
        # If going down
        else:
            start_y = start_room.bottom_y
        
        # If no turns need to be made
        if end_room.x < start_x < end_room.right_x:
            end_x = start_x
            end_y = end_room.bottom_y
        # If we need to go left
        elif end_room.right_x < start_x:
            end_x = end_room.right_x
            end_y = end_room.center_y
        # If we need to go right
        else:
            end_x = end_room.x
            end_y = end_room.center_y
        
        # Go up/down until you reach target y
        crnt_x = start_x
        crnt_y = start_y + 1
        while crnt_y != end_y:
            tiles.append(PassageFloorTile(crnt_x, crnt_y))
            if crnt_y < end_y:
                crnt_y += 1
            else:
                crnt_y -= 1
        while crnt_x != end_x:
            tiles.append(PassageFloorTile(crnt_x, crnt_y))
            if crnt_x < end_x:
                crnt_x += 1
            else:
                crnt_x -= 1

    # If this passage will be more horizontal
    else:
        start_y = start_room.center_y
        # If going left
        if end_room.center_x < start_room.center_x:
            start_x = start_room.x
        # If going right
        else:
            start_x = start_room.right_x
        
        # If no turns need to be made
        if end_room.y < start_y < end_room.bottom_y:
            end_x = end_room.right_x
            end_y = start_y
        # If we need to go up
        elif end_room.bottom_y < start_y:
            end_x = end_room.center_x
            end_y = end_room.bottom_y
        # If we need to go down
        else:
            end_x = end_room.center_x
            end_y = end_room.y
        
        # Go right/left until you reach target x
        crnt_x = start_x
        crnt_y = start_y
        while crnt_x != end_x:
            tiles.append(PassageFloorTile(crnt_x, crnt_y))
            if crnt_x < end_x:
                crnt_x += 1
            else:
                crnt_x -= 1
        
        # Then finish by going to target y
        while crnt_y != end_y:
            tiles.append(PassageFloorTile(crnt_x, crnt_y))
            if crnt_y < end_y:
                crnt_y += 1
            else:
                crnt_y -= 1

    return tiles

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
            tiles.append(MovingEnemy(x, y))
    return tiles

def generate_finish_tiles(rooms):
    tiles = []
    rooms_with_finish_point = random.sample(rooms, FINISH_TILE_AMOUNT)
    for room in rooms_with_finish_point:
        x_pos = random.randint(room.x, room.right_x)
        y_pos = random.randint(room.y, room.bottom_y)
        tiles.append(FinishTile(x_pos, y_pos))
    return tiles
