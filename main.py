import pygame

from src.constants import HEIGHT, WIDTH
from src.game import Game


def main():
    pygame.init()
    pygame.display.set_caption("Tower Defense")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    Game(screen).run()
    pygame.quit()


if __name__ == "__main__":
    main()
