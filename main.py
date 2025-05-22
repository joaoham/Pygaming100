import pygame
from core.player import Player
from core.room_manager import RoomManager

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Hollow Mooni - Room System")

clock = pygame.time.Clock()

room_manager = RoomManager(SCREEN_WIDTH, SCREEN_HEIGHT)
current_ground_level = room_manager.get_ground_level()

player = Player((SCREEN_WIDTH // 2 - 50, current_ground_level - 80))

def draw_text(surface, text, pos, color=(255, 255, 255), size=36):
    font = pygame.font.SysFont(None, size)
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, pos)

running = True
while running:
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    current_ground_level = room_manager.get_ground_level()

    if room_manager.can_move():
        player.update(keys, current_ground_level, SCREEN_WIDTH)
    else:
        player.animate()
        player.apply_gravity(current_ground_level)

    # ✅ Transição automática ao alcançar o limite direito da tela:
    if player.rect.right >= SCREEN_WIDTH - 10:  # Pode ajustar esse "10" para sensibilidade
        if room_manager.current_room in [1, 2]:  # Se estiver na sala 2 ou 3
            room_manager.next_room()
            current_ground_level = room_manager.get_ground_level()
            player.rect.topleft = (50, current_ground_level - 80)

    # ✅ Transição via porta apenas na primeira sala
    if room_manager.current_room == 0 and room_manager.player_at_door(player):
        if keys[pygame.K_e]:
            room_manager.next_room()
            current_ground_level = room_manager.get_ground_level()
            player.rect.topleft = (50, current_ground_level - 80)

    # ✅ Desenha em ordem: fundo → player → foreground
    room_manager.draw_room(screen)
    player.draw(screen)
    room_manager.draw_foreground(screen)

    # ✅ Mostra mensagem apenas na sala 0
    if room_manager.current_room == 0 and room_manager.player_at_door(player):
        draw_text(
            screen,
            "Pressione E para entrar no castelo",
            (SCREEN_WIDTH // 2 - 200, current_ground_level - 150),
            color=(255, 255, 0),
            size=36
        )

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
