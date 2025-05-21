import pygame
from core.player import Player
from core.tilemap import TileMap
from core.camera import Camera

if __name__ == "__main__":
    pygame.init()
    SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Hollow Mooni")
    clock = pygame.time.Clock()

    # Player
    player = Player((100, 500))
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)

    # TileMap
    map_data = [
    [-1]*40,
    [-1, -1, -1, -1, -1, -1,  2, -1, -1, -1,  2, -1, -1, -1,  2, -1, -1, -1,  2, -1, -1, -1, -1,  2, -1, -1, -1,  2, -1, -1, -1,  2, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1,  2, -1, -1, -1,  2, -1, -1, -1,  2, -1, -1, -1,  2, -1, -1, -1,  2, -1, -1, -1,  2, -1, -1, -1,  2, -1, -1, -1, -1, -1, -1],
    [-1]*40,
    [0]*40,
    [1]*40,
]

    tilemap = TileMap("assets/Dungeon Tile Set.png", 32, map_data)

    # Camera
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

    running = True
    while running:
        screen.fill((30, 30, 30))
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        all_sprites.update(keys)
        camera.update(player)

        tilemap.draw(screen, camera)

        for sprite in all_sprites:
            sprite.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
