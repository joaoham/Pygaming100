import pygame
from core.player import Player
from core.room_manager import RoomManager

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
# ✅ AJUSTE: GROUND_LEVEL mais alto (para alinhar com a grama da imagem)
GROUND_LEVEL = 690  # <<<<< AQUI O AJUSTE CRÍTICO! (se ainda flutuar, testa 670 ou 680)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Hollow Mooni - Room System")

clock = pygame.time.Clock()

# ✅ AJUSTE: Spawn coladinho ao chão, descontando a altura aproximada da sprite (~80px)
player = Player((SCREEN_WIDTH // 2 - 50, GROUND_LEVEL - 80))

room_manager = RoomManager(SCREEN_WIDTH, SCREEN_HEIGHT)

# ✅ Função para desenhar textos
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

    if room_manager.can_move():
        player.update(keys, GROUND_LEVEL, SCREEN_WIDTH)
    else:
        player.animate()
        player.apply_gravity(GROUND_LEVEL)

    # ✅ Interação com a porta
    if room_manager.current_room == 0 and room_manager.player_at_door(player):
        if keys[pygame.K_e]:
            room_manager.next_room()
            player.rect.topleft = (50, GROUND_LEVEL - 80)

    room_manager.draw_room(screen)

    player.draw(screen)

    # ✅ Mostra mensagem se estiver na porta
    if room_manager.current_room == 0 and room_manager.player_at_door(player):
        draw_text(
            screen,
            "Pressione E para entrar no castelo",
            (SCREEN_WIDTH // 2 - 200, GROUND_LEVEL - 0),
            color=(255, 255, 0),  # Amarelinho para destacar
            size=36
        )

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
