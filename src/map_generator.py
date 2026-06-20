import random
from src.constants import GRID_COLS, GRID_ROWS


class MapGenerator:
    def __init__(self, seed=None):
        if seed is not None:
            random.seed(seed)

    def generate(self):
        full_path = self._generate_path()
        tower_slots = self._generate_tower_slots(full_path)
        path_nodes = self._simplify_path(full_path)
        return {
            "path_nodes": path_nodes,
            "tower_slots": tower_slots,
        }

    def _generate_path(self):
        start_row = random.randint(1, GRID_ROWS - 2)

        path = [(0, start_row)]
        visited = {(0, start_row)}
        col, row = 0, start_row

        while col < GRID_COLS - 1:
            if random.random() < 0.4:
                if col + 1 < GRID_COLS and (col + 1, row) not in visited:
                    col += 1
                    path.append((col, row))
                    visited.add((col, row))
                    continue

            direction = random.choice([-1, 1])
            new_row = row + direction

            if 1 <= new_row < GRID_ROWS - 1 and (col, new_row) not in visited:
                row = new_row
                path.append((col, row))
                visited.add((col, row))
            elif col + 1 < GRID_COLS:
                col += 1
                path.append((col, row))
                visited.add((col, row))
            else:
                break

        while col < GRID_COLS - 1:
            col += 1
            path.append((col, row))

        return path

    def _simplify_path(self, path):
        if len(path) < 3:
            return path

        simplified = [path[0]]
        for i in range(1, len(path) - 1):
            prev_col, prev_row = path[i - 1]
            curr_col, curr_row = path[i]
            next_col, next_row = path[i + 1]

            if (prev_col == curr_col == next_col) or (prev_row == curr_row == next_row):
                continue

            simplified.append(path[i])

        simplified.append(path[-1])
        return simplified

    def _generate_tower_slots(self, path):
        path_set = set(path)
        valid_slots = []
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                if (col, row) in path_set:
                    continue

                for path_col, path_row in path_set:
                    dist = abs(col - path_col) + abs(row - path_row)
                    if 0 < dist <= 3:
                        valid_slots.append((col, row))
                        break

        valid_slots = list(set(valid_slots))
        count = min(random.randint(10, 20), len(valid_slots))
        return set(random.sample(valid_slots, count)) if valid_slots else set()