import pygame

from src.constants import (
    GRID_COLS,
    GRID_LINE,
    GRID_ROWS,
    MAP_OFFSET_X,
    MAP_OFFSET_Y,
    ROAD,
    ROAD_EDGE,
    TILE_SIZE,
)


class GameMap:
    def __init__(self):
        self.path_nodes = [
            (0, 4),
            (4, 4),
            (4, 2),
            (8, 2),
            (8, 6),
            (11, 6),
            (11, 3),
            (15, 3),
        ]
        self.path_points = [self.cell_center(cell) for cell in self.path_nodes]

    def cell_center(self, cell):
        col, row = cell
        x = MAP_OFFSET_X + col * TILE_SIZE + TILE_SIZE // 2
        y = MAP_OFFSET_Y + row * TILE_SIZE + TILE_SIZE // 2
        return x, y

    def draw(self, surface):
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                rect = pygame.Rect(
                    MAP_OFFSET_X + col * TILE_SIZE,
                    MAP_OFFSET_Y + row * TILE_SIZE,
                    TILE_SIZE,
                    TILE_SIZE,
                )
                pygame.draw.rect(surface, GRID_LINE, rect, 1)

        self.draw_road(surface, ROAD_EDGE, 50, y_offset=-2)
        self.draw_road(surface, ROAD, 38, y_offset=-2)
        pygame.draw.circle(surface, (80, 245, 150), self.path_points[0], 12)
        pygame.draw.circle(surface, (245, 80, 115), self.path_points[-1], 15)

    def draw_road(self, surface, color, width, y_offset=0):
        radius = width // 2
        for start, end in zip(self.path_points, self.path_points[1:]):
            shifted_start = (start[0], start[1] + y_offset)
            shifted_end = (end[0], end[1] + y_offset)
            pygame.draw.line(surface, color, shifted_start, shifted_end, width)
        for point in self.path_points:
            shifted_point = (point[0], point[1] + y_offset)
            pygame.draw.circle(surface, color, shifted_point, radius)
