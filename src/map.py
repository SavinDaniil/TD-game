import pygame

from src.constants import (
    GRID_COLS,
    GRID_LINE,
    GRID_ROWS,
    LEVEL_DATA,
    MAP_OFFSET_X,
    MAP_OFFSET_Y,
    ROAD,
    ROAD_EDGE,
    TILE_SIZE,
)


class GameMap:
    def __init__(self, level_id=1):
        self.level_id = level_id
        self.level_data = LEVEL_DATA[level_id]
        self.path_nodes = self.level_data["path_nodes"]
        self.path_cells = self.make_path_cells()
        self.path_points = [self.cell_center(cell) for cell in self.path_nodes]
        self.tower_slots = self.make_tower_slots()

    def make_path_cells(self):
        cells = set()
        for start, end in zip(self.path_nodes, self.path_nodes[1:]):
            start_col, start_row = start
            end_col, end_row = end
            if start_col == end_col:
                step = 1 if end_row >= start_row else -1
                for row in range(start_row, end_row + step, step):
                    cells.add((start_col, row))
            elif start_row == end_row:
                step = 1 if end_col >= start_col else -1
                for col in range(start_col, end_col + step, step):
                    cells.add((col, start_row))
        return cells

    def make_tower_slots(self):
        return self.level_data["tower_slots"] - self.path_cells

    def cell_center(self, cell):
        col, row = cell
        x = MAP_OFFSET_X + col * TILE_SIZE + TILE_SIZE // 2
        y = MAP_OFFSET_Y + row * TILE_SIZE + TILE_SIZE // 2
        return x, y

    def get_cell_by_mouse(self, mouse_pos):
        x, y = mouse_pos
        col = (x - MAP_OFFSET_X) // TILE_SIZE
        row = (y - MAP_OFFSET_Y) // TILE_SIZE
        if 0 <= col < GRID_COLS and 0 <= row < GRID_ROWS:
            return int(col), int(row)
        return None

    def can_place_tower(self, cell, towers):
        if cell not in self.tower_slots:
            return False
        return all(tower.cell != cell for tower in towers)

    def draw(self, surface, mouse_cell, towers):
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

        occupied = {tower.cell for tower in towers}
        for cell in self.tower_slots:
            center = self.cell_center(cell)
            color = (54, 67, 91)
            width = 1
            if cell == mouse_cell and cell not in occupied:
                color = (92, 140, 190)
                width = 3
            pygame.draw.circle(surface, color, center, 15, width)

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
