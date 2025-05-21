import pygame

class TileMap:
    def __init__(self, tile_image_path, tile_size, map_data):
        self.tile_size = tile_size
        self.tiles = self.load_tiles(tile_image_path)
        self.map_data = map_data

    def load_tiles(self, path):
        tile_sheet = pygame.image.load(path).convert_alpha()
        sheet_width, sheet_height = tile_sheet.get_size()
        tiles = []

        for y in range(0, sheet_height - self.tile_size + 1, self.tile_size):
            for x in range(0, sheet_width - self.tile_size + 1, self.tile_size):
                tile = tile_sheet.subsurface(pygame.Rect(x, y, self.tile_size, self.tile_size))
                tiles.append(tile)
        return tiles


    def draw(self, surface, camera):
        for row_index, row in enumerate(self.map_data):
            for col_index, tile_index in enumerate(row):
                if tile_index >= 0:  # -1 = espaço vazio
                    tile = self.tiles[tile_index]
                    x = col_index * self.tile_size - camera.offset.x
                    y = row_index * self.tile_size - camera.offset.y
                    surface.blit(tile, (x, y))
