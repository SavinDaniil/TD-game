import pygame
from src.constants import (GRID_COLS, GRID_LINE, GRID_ROWS, LEVEL_DATA, MAP_OFFSET_X, MAP_OFFSET_Y, ROAD, ROAD_EDGE,
                           TILE_SIZE, ROAD_EDGE_WIDTH, ROAD_WIDTH, TOWER_SLOT_RADIUS, START_POINT_RADIUS,
                           END_POINT_RADIUS, START_COLOR, END_COLOR)
from src.map_generator import MapGenerator


class GameMap:
    def __init__(self, level_id=1, random_map=False):
        self.random_map = random_map
        if random_map:
            gen = MapGenerator()
            data = gen.generate()
            self.path_nodes = data["path_nodes"]
            self.path_cells = self.make_path_cells()
            self.tower_slots = data["tower_slots"]
        else:
            self.level_data = LEVEL_DATA[level_id]
            self.path_nodes = self.level_data["path_nodes"]
            self.path_cells = self.make_path_cells()
            self.tower_slots = self.make_tower_slots()

        self.path_points = [self.cell_center(cell) for cell in self.path_nodes]

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
        return MAP_OFFSET_X + col * TILE_SIZE + TILE_SIZE // 2, \
               MAP_OFFSET_Y + row * TILE_SIZE + TILE_SIZE // 2

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
                rect = pygame.Rect(MAP_OFFSET_X + col * TILE_SIZE, MAP_OFFSET_Y + row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(surface, GRID_LINE, rect, 1)

        self.draw_road(surface, ROAD_EDGE, ROAD_EDGE_WIDTH)
        self.draw_road(surface, ROAD, ROAD_WIDTH)

        occupied = {tower.cell for tower in towers}
        for cell in self.tower_slots:
            center = self.cell_center(cell)
            color = (54, 67, 91)
            width = 1
            if cell == mouse_cell and cell not in occupied:
                color = (92, 140, 190)
                width = 3
            pygame.draw.circle(surface, color, center, TOWER_SLOT_RADIUS, width)

        pygame.draw.circle(surface, START_COLOR, self.path_points[0], START_POINT_RADIUS)
        pygame.draw.circle(surface, END_COLOR, self.path_points[-1], END_POINT_RADIUS)

    def draw_road(self, surface, color, width):
        radius = width // 2
        for start, end in zip(self.path_points, self.path_points[1:]):
            pygame.draw.line(surface, color, start, end, width)
        for point in self.path_points:
            pygame.draw.circle(surface, color, point, radius)
