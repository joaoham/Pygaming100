import pygame
from core.player import Player
from core.room_manager import RoomManager

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Hollow Mooni - Room System")

clock = pygame.time.Clock()

player = Player((50, 400))  # Posição inicial mais alta para "cair" no chão
room_manager = RoomManager(SCREEN_WIDTH, SCREEN_HEIGHT)

running = True
while running:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    player.update(keys)

    if room_manager.is_at_door(player):
        room_manager.next_room()
        player.rect.topleft = (50, 400)  # Resetar posição ao trocar de sala

    room_manager.draw_room(screen)

    # Chão visível
    pygame.draw.rect(screen, (100, 100, 100), pygame.Rect(0, 700, SCREEN_WIDTH, 100))

    player.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
