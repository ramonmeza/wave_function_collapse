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
    weight: float

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

def get_neighbors(i: int, rows: int, cols: int) -> Neighbors:
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

def analyze_map(map: list[Tiles], rows: int, cols: int) -> set[Connection]:
    all_connection_constraints: list[tuple[Tiles, Tiles, Directions]] = []
    for i, tile in enumerate(map):
        up_i, down_i, left_i, right_i = get_neighbors(i, rows, cols)
        
        if up_i is not None:
            conn: tuple[Tiles, Tiles, Directions] = (map[up_i], tile, Directions.UP)
            all_connection_constraints.append(conn)

        if down_i is not None:
            conn = (map[down_i], tile, Directions.DOWN)
            all_connection_constraints.append(conn)

        if left_i is not None:
            conn = (map[left_i], tile, Directions.LEFT)
            all_connection_constraints.append(conn)

        if right_i is not None:
            conn = (map[right_i], tile, Directions.RIGHT)
            all_connection_constraints.append(conn)
    
    connections: set[Connection] = set([])
    check_conns: set[tuple[Tiles, Tiles, Directions]] = set(all_connection_constraints)
    for i, temp_conn in enumerate(check_conns):
        weight: int = all_connection_constraints.count(temp_conn)
        connection: Connection = Connection(
            *temp_conn,
            weight
        )
        connections.add(connection)

    return connections

def render_map(rows: int, cols: int, map: list[list[Tiles]] | list[Tiles]):
    for row in range(rows):
        for col in range(cols):
            i: int = (row * cols) + col

            if isinstance(map[i], Tiles):
                tile: Tiles = map[i]  # type: ignore
            else:
                tile: Tiles = map[i][0] if len(map[i]) == 1 else Tiles.UNSET  # type: ignore

            colored_tile: str = ""
            tile_str: str = "   "
            match tile:
                case Tiles.SEA:
                    colored_tile = f"\x1b[44m{tile_str}\x1b[0m"
                case Tiles.COAST:
                    colored_tile = f"\x1b[43m{tile_str}\x1b[0m"
                case Tiles.LAND:
                    colored_tile = f"\x1b[42m{tile_str}\x1b[0m"
                case _:  # type: ignore
                    colored_tile = "\x1b[37m \N{BULLET} \x1b[0m"

            print(colored_tile, end="")
        print(end="\n")


# main entry
def main() -> None:
    # simplified WFC algorithm
    # create a sample tilemap
    sample_map_rows: int = 6
    sample_map_cols: int = 6
    sample_map: list[Tiles] = [
        Tiles.LAND, Tiles.LAND, Tiles.LAND, Tiles.LAND, Tiles.LAND, Tiles.LAND,
        Tiles.LAND, Tiles.COAST, Tiles.COAST, Tiles.COAST, Tiles.LAND, Tiles.LAND,
        Tiles.LAND, Tiles.COAST, Tiles.SEA, Tiles.SEA, Tiles.COAST, Tiles.LAND,
        Tiles.LAND, Tiles.COAST, Tiles.SEA, Tiles.SEA, Tiles.COAST, Tiles.LAND,
        Tiles.LAND, Tiles.LAND, Tiles.COAST, Tiles.COAST, Tiles.LAND, Tiles.LAND,
        Tiles.LAND, Tiles.LAND, Tiles.LAND, Tiles.LAND, Tiles.LAND, Tiles.LAND,
    ]
    print("Sample Map")
    render_map(sample_map_rows, sample_map_cols, sample_map)
    print(end="\n")

    # analyze map to discover connection constraints and weights
    connections = analyze_map(sample_map, sample_map_rows, sample_map_cols)

    # create tilemap with "super-positioned" cells
    rows: int = MAP_HEIGHT
    cols: int = MAP_WIDTH
    map: list[list[Tiles]] = []
    for _ in range(rows * cols):
        map.append([Tiles.SEA, Tiles.COAST, Tiles.LAND])

    for _ in range(rows * cols):
        # return set of lowest entropy
        # since each element of our map grid is a list of possible tiles, the entropy heuristic is just the length of possible tiles
        # this can be modified for better results, i think "Shannon entropy" is what is used in actual WFC implementations
        lowest: list[int] = find_lowest_entropy(map)
        if len(lowest) == 0:
            break
        
        i: int = random.choice(lowest)

        # collapse
        # get the weights of the remaining possible tiles
        # place a tile
        tile: Tiles = Tiles(random.choice(map[i]))
        map[i] = [tile]

        # propagate (for each neighbor, remove tiles that don't conform to placed tile rule)
        up_i, down_i, left_i, right_i = get_neighbors(i, rows, cols)

        # apply rules to each neighbor, removing tiles that violate the connection constraints
        dirs = list(Directions)
        for i, neighbor_i in enumerate([up_i, down_i, left_i, right_i]):
            if neighbor_i is not None:
                for t in map[neighbor_i][:]:
                    check_connection: Optional[Connection] = next(iter(x for x in connections if x.tile == t and x.connects_to == tile and x.from_dir == dirs[i]), None)
                    # had to add safeguard to avoid removing all possibilities from the cell. maybe this can be fixed, but I don't know how to at the moment.
                    # this results in slightly inaccurate representations, where a cell may violate a rule. I'm okay with this for now..
                    if check_connection is None and len(map[neighbor_i]) > 1:
                        map[neighbor_i].remove(t)

    # render
    print("Generated Map")
    render_map(rows, cols, map)


if __name__ == "__main__":
    main()
