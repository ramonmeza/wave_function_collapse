from __future__ import annotations
from enum import IntEnum
from typing import NamedTuple, Optional

import random
 

# can't forward declare this, sorry
class Tiles(IntEnum):
    UNSET = -1
    SEA = 0
    COAST = 1
    LAND = 2


# config
MAP_HEIGHT: int = 32
MAP_WIDTH: int = 48
WEIGHTS: dict[Tiles, float] = {
    Tiles.SEA: 1.0,
    Tiles.COAST: 0.5,
    Tiles.LAND: 0.5,
}


# helpful types and enums
class Directions(IntEnum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3

class Connection(NamedTuple):
    tile: Tiles
    connects_to: Tiles
    from_dir: Directions

class Neighbors(NamedTuple):
    # indices of neighbors
    up: Optional[int] = None
    down: Optional[int] = None
    left: Optional[int] = None
    right: Optional[int] = None


# functions
def find_lowest_entropy(map: list[list[Tiles]]) -> list[int]:
    # find lowest length (entropy heuristic)
    lowest_length: Optional[int] = None
    lowest_indices: list[int] = []
    for i, options in enumerate(map):
        options_len: int = len(options)
        if options_len == 1:
            continue

        if lowest_length is None or options_len < lowest_length:
            # first or new lowest, clear accumulated and add new lowest
            lowest_length = options_len
            lowest_indices.clear()
            lowest_indices.append(i)
        elif options_len == lowest_length:
            lowest_indices.append(i)

    # return list of indices into map with lowest entropy
    return lowest_indices

def get_neighbors(i: int, grid: list[list[Tiles]], rows: int, cols: int) -> Neighbors:
    row, col = divmod(i, cols)

    up: Optional[int] = (row - 1) * cols + col if row > 0 else None
    down: Optional[int] = (row + 1) * cols + col if row < rows - 1 else None
    left: Optional[int] = row * cols + (col - 1) if col > 0 else None
    right: Optional[int] = row * cols + (col + 1) if col < cols - 1 else None

    return Neighbors(
        up=up,
        down=down,
        left=left,
        right=right
    )


# connections list
CONNECTIONS: list[Connection] = [
    # sea connects to sea from all directions
    Connection(Tiles.SEA, Tiles.SEA, Directions.UP),
    Connection(Tiles.SEA, Tiles.SEA, Directions.DOWN),
    Connection(Tiles.SEA, Tiles.SEA, Directions.LEFT),
    Connection(Tiles.SEA, Tiles.SEA, Directions.RIGHT),
    
    # sea connects to coast from all directions
    Connection(Tiles.SEA, Tiles.COAST, Directions.UP),
    Connection(Tiles.SEA, Tiles.COAST, Directions.DOWN),
    Connection(Tiles.SEA, Tiles.COAST, Directions.LEFT),
    Connection(Tiles.SEA, Tiles.COAST, Directions.RIGHT),

    # coast connects to sea from all directions
    Connection(Tiles.COAST, Tiles.SEA, Directions.UP),
    Connection(Tiles.COAST, Tiles.SEA, Directions.DOWN),
    Connection(Tiles.COAST, Tiles.SEA, Directions.LEFT),
    Connection(Tiles.COAST, Tiles.SEA, Directions.RIGHT),
    Connection(Tiles.COAST, Tiles.SEA, Directions.RIGHT),
    
    # coast connects to coast from all directions
    Connection(Tiles.COAST, Tiles.COAST, Directions.UP),
    Connection(Tiles.COAST, Tiles.COAST, Directions.DOWN),
    Connection(Tiles.COAST, Tiles.COAST, Directions.LEFT),
    Connection(Tiles.COAST, Tiles.COAST, Directions.RIGHT),
    
    # coast connects to land from all directions
    Connection(Tiles.COAST, Tiles.LAND, Directions.UP),
    Connection(Tiles.COAST, Tiles.LAND, Directions.DOWN),
    Connection(Tiles.COAST, Tiles.LAND, Directions.LEFT),
    Connection(Tiles.COAST, Tiles.LAND, Directions.RIGHT),
    
    # land connects to land from all directions
    Connection(Tiles.LAND, Tiles.LAND, Directions.UP),
    Connection(Tiles.LAND, Tiles.LAND, Directions.DOWN),
    Connection(Tiles.LAND, Tiles.LAND, Directions.LEFT),
    Connection(Tiles.LAND, Tiles.LAND, Directions.RIGHT),
    
    # land connects to coast from all directions
    Connection(Tiles.LAND, Tiles.COAST, Directions.UP),
    Connection(Tiles.LAND, Tiles.COAST, Directions.DOWN),
    Connection(Tiles.LAND, Tiles.COAST, Directions.LEFT),
    Connection(Tiles.LAND, Tiles.COAST, Directions.RIGHT),
]


# main entry
def main() -> None:
    # simplified WFC algorithm
    # create tilemap with "super-positioned" cells
    rows: int = MAP_HEIGHT
    cols: int = MAP_WIDTH
    tile_weights: dict[Tiles, float] = WEIGHTS
    map: list[list[Tiles]] = []
    for row in range(rows):
        for col in range(cols):
            map.append([Tiles.SEA, Tiles.COAST, Tiles.LAND])

    for _ in range(rows * cols):
        # return set of lowest entropy
        # since each element of our map grid is a list of possible tiles, the entropy heuristic is just the length of possible tiles
        # this can be modified for better results, i think "Shannon entropy" is what is used in actual WFC implementations
        lowest: list[int] = find_lowest_entropy(map)
        i: int = random.choice(lowest)

        # collapse
        # get the weights of the remaining possible tiles
        # place a tile based on weights
        weights: list[float] = []
        for t in map[i]:
            weights.append(tile_weights[t])

        tile: Tiles = Tiles(random.choices(map[i], weights)[0])
        map[i] = [tile]

        # propagate (for each neighbor, remove tiles that don't conform to placed tile rule)
        up_i, down_i, left_i, right_i = get_neighbors(i, map, rows, cols)

        # apply rules :)
        # check if the connection between map[i] and possible neighbor exists in rules
        # if not, the tile from possible generated tiles
        # hard-coding each direction doesn't *feel* good, but it works
        if up_i is not None:
            for t in map[up_i][:]:
                check_connection = Connection(
                    tile=t,
                    connects_to=tile,
                    from_dir=Directions.DOWN,
                )
                if check_connection not in CONNECTIONS:
                    map[up_i].remove(t)
        
        if down_i is not None:
            for t in map[down_i][:]:
                check_connection = Connection(
                    tile=t,
                    connects_to=tile,
                    from_dir=Directions.UP,
                )
                if check_connection not in CONNECTIONS:
                    map[down_i].remove(t)
                    
        if left_i is not None:
            for t in map[left_i][:]:
                check_connection = Connection(
                    tile=t,
                    connects_to=tile,
                    from_dir=Directions.RIGHT,
                )
                if check_connection not in CONNECTIONS:
                    map[left_i].remove(t)
                    
        if right_i is not None:
            for t in map[right_i][:]:
                check_connection = Connection(
                    tile=t,
                    connects_to=tile,
                    from_dir=Directions.LEFT,
                )
                if check_connection not in CONNECTIONS:
                    map[right_i].remove(t)
        
    # render
    for row in range(rows):
        for col in range(cols):
            i = (row * cols) + col
            tile: Tiles = map[i][0] if len(map[i]) == 1 else Tiles.UNSET
            colored_tile: str = ""
            tile_str: str = "   "
            match tile: # i made chatgpt write this statement and i still had to hand modify it...
                case Tiles.SEA:
                    colored_tile = f"\x1b[44m{tile_str}\x1b[0m"
                case Tiles.COAST:
                    colored_tile = f"\x1b[43m{tile_str}\x1b[0m"
                case Tiles.LAND:
                    colored_tile = f"\x1b[42m{tile_str}\x1b[0m"
                case _:
                    colored_tile = "\x1b[37m \N{BULLET} \x1b[0m"

            print(colored_tile, end="")
        print("\n", end="")


if __name__ == "__main__":
    main()
