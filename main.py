import pygame


WIDTH = 1280
HEIGHT = 720
FPS = 60
BACKGROUND = (13, 16, 29)


def main():
    pygame.init()
    pygame.display.set_caption("Tower Defense")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BACKGROUND)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
