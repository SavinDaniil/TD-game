import pygame

from src.utils import distance


class Enemy:
    def __init__(self, path_points, wave=1):
        self.path_points = path_points
        self.position = [float(path_points[0][0]), float(path_points[0][1])]
        self.path_index = 1
        self.max_hp = 35 + wave * 8
        self.hp = self.max_hp
        self.speed = 55 + wave * 2
        self.reward = 10 + wave
        self.alive = True
        self.reached_base = False
        self.is_flying = False

    def update(self, dt):
        if self.path_index >= len(self.path_points):
            self.reached_base = True
            self.alive = False
            return

        target = self.path_points[self.path_index]
        dist = distance(self.position, target)
        move = self.speed * dt
        if dist <= move:
            self.position[0], self.position[1] = target
            self.path_index += 1
        else:
            self.position[0] += (target[0] - self.position[0]) / dist * move
            self.position[1] += (target[1] - self.position[1]) / dist * move

    def draw(self, surface):
        pos = (int(self.position[0]), int(self.position[1]))
        pygame.draw.circle(surface, (220, 225, 235), pos, 15)
        width = 34
        ratio = max(0, self.hp / self.max_hp)
        back = pygame.Rect(pos[0] - width // 2, pos[1] - 27, width, 5)
        front = pygame.Rect(pos[0] - width // 2, pos[1] - 27, int(width * ratio), 5)
        pygame.draw.rect(surface, (45, 47, 60), back)
        pygame.draw.rect(surface, (245, 248, 255), front)
