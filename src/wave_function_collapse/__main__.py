from __future__ import annotations
from typing import Any

import dataclasses
import enum
import math
import random

import pyray


UNSET = -1


class Tileset(enum.IntEnum):
    TILE_WATER = 42 # done
    TILE_GRASS_SHORE_TL = 37
    TILE_GRASS_SHORE_T = 38
    TILE_GRASS_SHORE_TR = 39
    TILE_GRASS_SHORE_L = 49
    TILE_GRASS = 50 # done
    TILE_GRASS_SHORE_R = 51
    TILE_GRASS_SHORE_BL = 61
    TILE_GRASS_SHORE_B = 62
    TILE_GRASS_SHORE_BR = 63


Tile = Tileset


def draw_tile(
        tileset_texture: pyray.Texture,
        tileset_cols: int,
        tile_i: int,
        tile_w: int,
        tile_h: int,
        dest_x: float,
        dest_y: float,
        scale: float = 1.0
    ) -> None:
    x = (tile_i % tileset_cols) * tile_w
    y = math.floor(tile_i / tileset_cols) * tile_h
    source = (x, y, tile_w, tile_h)
    dest = (dest_x, dest_y, tile_w * scale, tile_h * scale)
    origin = (0, 0)
    rotation = 0
    tint = pyray.WHITE
    pyray.draw_texture_pro(tileset_texture, source, dest, origin, rotation, tint)


def draw_tileset(tileset_texture: pyray.Texture, tile_size: tuple[int, int], dest_x: int, dest_y: int):
    space_between: int = 10
    for i, tile_i in enumerate(Tileset):
        x = dest_x + (i * (tile_size[0] + space_between))
        draw_tile(tileset_texture, 12, tile_i, *tile_size, x, dest_y)


def draw_tilemap(tilemap: list[int | WFCTile], tilemap_cols: int, tileset_texture: pyray.Texture, tileset_cols: int, tile_size: tuple[int, int]) -> None:
    for i, tile in enumerate(tilemap):
        if tile == UNSET:
            continue
        
        if isinstance(tile, WFCTile):
            actual_tile = tile.tile
        else:
            actual_tile = tile

        x = (i % tilemap_cols) * tile_size[0]
        y = math.floor(i / tilemap_cols) * tile_size[1]
        draw_tile(tileset_texture, tileset_cols, actual_tile, *tile_size, x, y)


@dataclasses.dataclass
class WFCTile:
    tile: Tile | int = UNSET
    up: list[Tile] = dataclasses.field(default_factory=list[Tile])
    down: list[Tile] = dataclasses.field(default_factory=list[Tile])
    left: list[Tile] = dataclasses.field(default_factory=list[Tile])
    right: list[Tile] =dataclasses.field(default_factory=list[Tile])

def wfc_collapse(options: list[Tile]) -> Tile:
    return options[random.randrange(0, len(options))]


def draw_wfc_tile(wfc_tile: WFCTile, tileset_texture: pyray.Texture, tileset_cols: int, tile_size: tuple[int, int], dest_x: int = 0, dest_y: int = 0) -> None:
    font_size: int = 12
    font_color = pyray.WHITE
    space_between_sections: int = 10
    tile_start_x: int = dest_x + 32

    cur_x: int = dest_x
    cur_y: int = dest_y
    pyray.draw_text("Tile", cur_x, cur_y, font_size, font_color)
    cur_x = tile_start_x
    draw_tile(tileset_texture, tileset_cols, wfc_tile.tile, *tile_size, cur_x, cur_y)
    cur_y += tile_size[1]
    cur_y += space_between_sections

    cur_x = dest_x
    pyray.draw_text("Up", cur_x, cur_y, font_size, font_color)
    cur_x = tile_start_x
    for _, tile_i in enumerate(wfc_tile.up):
        y = cur_y
        draw_tile(tileset_texture, tileset_cols, tile_i, *tile_size, cur_x, y)
        y += tile_size[1]
        draw_tile(tileset_texture, tileset_cols, wfc_tile.tile, *tile_size, cur_x, y)
        cur_x += tile_size[0]
        cur_x += space_between_sections

    cur_y += tile_size[1] * 2
    cur_y += space_between_sections
    
    cur_x = dest_x
    pyray.draw_text("Down", cur_x, cur_y, font_size, font_color)
    cur_x = tile_start_x
    for _, tile_i in enumerate(wfc_tile.down):
        y = cur_y
        draw_tile(tileset_texture, tileset_cols, wfc_tile.tile, *tile_size, cur_x, y)
        y += tile_size[1]
        draw_tile(tileset_texture, tileset_cols, tile_i, *tile_size, cur_x, y)
        cur_x += tile_size[0]
        cur_x += space_between_sections

    cur_y += tile_size[1] * 2
    cur_y += space_between_sections
    
    cur_x = dest_x
    pyray.draw_text("Left", cur_x, cur_y, font_size, font_color)
    cur_x = tile_start_x
    for _, tile_i in enumerate(wfc_tile.left):
        x = cur_x
        draw_tile(tileset_texture, tileset_cols, tile_i, *tile_size, x, cur_y)
        x += tile_size[0]
        draw_tile(tileset_texture, tileset_cols, wfc_tile.tile, *tile_size, x, cur_y)
        cur_y += tile_size[1]
        cur_y += space_between_sections

    cur_x = dest_x
    pyray.draw_text("Right", cur_x, cur_y, font_size, font_color)
    cur_x = tile_start_x
    for _, tile_i in enumerate(wfc_tile.right):
        x = cur_x
        draw_tile(tileset_texture, tileset_cols, wfc_tile.tile, *tile_size, x, cur_y)
        x += tile_size[0]
        draw_tile(tileset_texture, tileset_cols, tile_i, *tile_size, x, cur_y)
        cur_y += tile_size[1]
        cur_y += space_between_sections


def draw_wfc_tiles(wfc_tiles: dict[Tile, WFCTile], tileset_texture: pyray.Texture, tileset_cols: int, tile_size: tuple[int, int], x: int = 0, y: int = 0) -> None:
    pyray.draw_text("Tileset", x, y, 12, pyray.WHITE)
    draw_tileset(tileset_texture, tile_size, x + 50, y)
    y += 32
    for _, tile in wfc_tiles.items():
        draw_wfc_tile(tile, tileset_texture, tileset_cols, tile_size, x, y)
        x += 155


def main() -> None:
    pyray.init_window(1700, 400, "Wave Function Collapse")

    tileset_texture = pyray.load_texture("assets/tiles_packed.png")
    _tileset_rows, tileset_cols = (10, 12)
    tile_size = _tile_w, _tile_h = (16, 16)

    wfc_tiles: dict[Tile, WFCTile] = {
        Tile.TILE_WATER: WFCTile(
            Tile.TILE_WATER,
            up=[Tile.TILE_WATER, Tile.TILE_GRASS_SHORE_B],
            down=[Tile.TILE_WATER, Tile.TILE_GRASS_SHORE_T],
            left=[Tile.TILE_WATER, Tile.TILE_GRASS_SHORE_R],
            right=[Tile.TILE_WATER, Tile.TILE_GRASS_SHORE_L],
        ),
        Tile.TILE_GRASS_SHORE_TL: WFCTile(
            Tile.TILE_GRASS_SHORE_TL,
            up=[Tile.TILE_WATER, Tile.TILE_GRASS_SHORE_B, Tile.TILE_GRASS_SHORE_BL, Tile.TILE_GRASS_SHORE_BR],
            down=[Tile.TILE_GRASS_SHORE_L, Tile.TILE_GRASS_SHORE_BL],
            left=[Tile.TILE_WATER, Tile.TILE_GRASS_SHORE_R, Tile.TILE_GRASS_SHORE_BR, Tile.TILE_GRASS_SHORE_TR],
            right=[Tile.TILE_GRASS_SHORE_T, Tile.TILE_GRASS_SHORE_TR],
        ),
        Tile.TILE_GRASS_SHORE_T: WFCTile(
            Tile.TILE_GRASS_SHORE_T,
            up=[Tile.TILE_WATER, Tile.TILE_GRASS_SHORE_B, Tile.TILE_GRASS_SHORE_BL, Tile.TILE_GRASS_SHORE_BR],
            down=[Tile.TILE_GRASS, Tile.TILE_GRASS_SHORE_B],
            left=[Tile.TILE_GRASS_SHORE_T, Tile.TILE_GRASS_SHORE_TL],
            right=[Tile.TILE_GRASS_SHORE_T, Tile.TILE_GRASS_SHORE_TR],
        ),
        Tile.TILE_GRASS_SHORE_TR: WFCTile(
            Tile.TILE_GRASS_SHORE_TR,
            up=[Tile.TILE_WATER, Tile.TILE_GRASS_SHORE_B, Tile.TILE_GRASS_SHORE_BL, Tile.TILE_GRASS_SHORE_BR],
            down=[Tile.TILE_GRASS_SHORE_R, Tile.TILE_GRASS_SHORE_BR],
            left=[Tile.TILE_GRASS_SHORE_T, Tile.TILE_GRASS_SHORE_TL],
            right=[Tile.TILE_WATER, Tile.TILE_GRASS_SHORE_L, Tile.TILE_GRASS_SHORE_BL, Tile.TILE_GRASS_SHORE_TL],
        ),
        Tile.TILE_GRASS_SHORE_L: WFCTile(
            Tile.TILE_GRASS_SHORE_L,
            up=[Tile.TILE_GRASS_SHORE_L, Tile.TILE_GRASS_SHORE_TL],
            down=[Tile.TILE_GRASS_SHORE_L, Tile.TILE_GRASS_SHORE_BL],
            left=[Tile.TILE_WATER, Tile.TILE_GRASS_SHORE_R, Tile.TILE_GRASS_SHORE_TR, Tile.TILE_GRASS_SHORE_BR],
            right=[Tile.TILE_GRASS, Tile.TILE_GRASS_SHORE_R],
        ),
        Tile.TILE_GRASS: WFCTile(
            Tile.TILE_GRASS,
            up=[Tile.TILE_GRASS, Tile.TILE_GRASS_SHORE_T],
            down=[Tile.TILE_GRASS, Tile.TILE_GRASS_SHORE_B],
            left=[Tile.TILE_GRASS, Tile.TILE_GRASS_SHORE_L],
            right=[Tile.TILE_GRASS, Tile.TILE_GRASS_SHORE_R],
        ),
        Tile.TILE_GRASS_SHORE_R: WFCTile(
            Tile.TILE_GRASS_SHORE_R,
            up=[Tile.TILE_GRASS_SHORE_R, Tile.TILE_GRASS_SHORE_TR],
            down=[Tile.TILE_GRASS_SHORE_R, Tile.TILE_GRASS_SHORE_BR],
            left=[Tile.TILE_GRASS, Tile.TILE_GRASS_SHORE_L],
            right=[Tile.TILE_WATER, Tile.TILE_GRASS_SHORE_L, Tile.TILE_GRASS_SHORE_TL, Tile.TILE_GRASS_SHORE_BL],
        ),
        Tile.TILE_GRASS_SHORE_BL: WFCTile(
            Tile.TILE_GRASS_SHORE_BL,
            up=[Tile.TILE_GRASS_SHORE_L, Tile.TILE_GRASS_SHORE_TL],
            down=[Tile.TILE_WATER, Tile.TILE_GRASS_SHORE_T, Tile.TILE_GRASS_SHORE_TR, Tile.TILE_GRASS_SHORE_TL],
            left=[Tile.TILE_WATER, Tile.TILE_GRASS_SHORE_R, Tile.TILE_GRASS_SHORE_TR, Tile.TILE_GRASS_SHORE_BR],
            right=[Tile.TILE_GRASS, Tile.TILE_GRASS_SHORE_R],
        ),
        Tile.TILE_GRASS_SHORE_B: WFCTile(
            Tile.TILE_GRASS_SHORE_B,
            up=[Tile.TILE_GRASS, Tile.TILE_GRASS_SHORE_T],
            down=[Tile.TILE_WATER, Tile.TILE_GRASS_SHORE_T, Tile.TILE_GRASS_SHORE_TL, Tile.TILE_GRASS_SHORE_TR],
            left=[Tile.TILE_GRASS_SHORE_B, Tile.TILE_GRASS_SHORE_BL],
            right=[Tile.TILE_GRASS_SHORE_B, Tile.TILE_GRASS_SHORE_BR],
        ),
        Tile.TILE_GRASS_SHORE_BR: WFCTile(
            Tile.TILE_GRASS_SHORE_BR,
            up=[Tile.TILE_GRASS_SHORE_R, Tile.TILE_GRASS_SHORE_TR],
            down=[Tile.TILE_WATER, Tile.TILE_GRASS_SHORE_T, Tile.TILE_GRASS_SHORE_TR, Tile.TILE_GRASS_SHORE_TL],
            left=[Tile.TILE_GRASS_SHORE_B, Tile.TILE_GRASS_SHORE_BL],
            right=[Tile.TILE_WATER, Tile.TILE_GRASS_SHORE_L, Tile.TILE_GRASS_SHORE_TL, Tile.TILE_GRASS_SHORE_BL],
        )
    }

    # wfc_tiles is the list of possible ("super-positioned") tiles
    # each tile has a list of possible tiles for each direction
    _tilemap_size = tilemap_rows, tilemap_cols = (20, 20)
    tilemap: list[Any] = [UNSET] * tilemap_rows * tilemap_cols

    # choose random starting cell
    i: int = random.randrange(0, len(tilemap))
    # set to random WFC tile
    _, tilemap[i] = random.choice(list(wfc_tiles.items()))

    # up = random.randrange(0, len(wfc_tiles[i].up))
    # down = random.randrange(0, len(wfc_tiles[i].down))
    # left = random.randrange(0, len(wfc_tiles[i].left))
    # right = random.randrange(0, len(wfc_tiles[i].right))
    


    # main loop
    while not pyray.window_should_close():
        pyray.begin_drawing()
        pyray.clear_background(pyray.BLACK)

        #draw_wfc_tiles(wfc_tiles, tileset_texture, tileset_cols, tile_size, 10, 10)

        draw_tilemap(tilemap, tilemap_cols, tileset_texture, tileset_cols, tile_size)

        if pyray.is_key_released(pyray.KeyboardKey.KEY_SPACE):
            for i, tile in enumerate(tilemap):
                # if the tile in the tilemap is unset, then we skip it
                if tile == UNSET:
                    continue

                # if the tile is not a WFCTile object, then we skip it
                if not isinstance(tile, WFCTile):
                    continue

                # now we only check WFCTiles and their neighbors


        #     # find lowest entropy set?
        #     # for each tile in set ?
        #     # - pick random tile from that direction?

        pyray.end_drawing()

    pyray.unload_texture(tileset_texture)
    pyray.close_window()


if __name__ == "__main__":
    main()
