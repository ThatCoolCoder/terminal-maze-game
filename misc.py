from enum import Enum, unique

@unique
class Direction(Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3

    @staticmethod
    def opposite(direction):
        if direction == Direction.UP:
            return Direction.DOWN
        elif direction == Direction.DOWN:
            return Direction.UP
        elif direction == Direction.LEFT:
            return Direction.RIGHT
        else:
            return Direction.LEFT

def sort_based_on_key(items, key):
    # Sort a list of dicts by the value at dict[key]
    # Order of identical items is not garanteed

    sorting_set = []
    for item in items:
        sorting_set.append(item[key])
    
    sorted_set = sorting_set.copy()
    sorted_set.sort()

    result = []
    for item in sorted_set:
        index = sorting_set.index(item)
        result.append(items[index])
    return items

def distance_squared(x1: int, y1: int, x2: int, y2: int):
    return (x1 - x2) ** 2 + (y1 - y2) ** 2