import pygame
from core.player import Player
from core.room_manager import RoomManager
from core.wave_manager import WaveManager
from core.skeleton import SkeletonEnemy
from core.nightborne import NightBorneEnemy
from core.bringer import BringerOfDeathEnemy
from core.spell_effect import SpellEffect

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Hollow Mooni - Room System")

clock = pygame.time.Clock()

room_manager = RoomManager(SCREEN_WIDTH, SCREEN_HEIGHT)
current_ground_level = room_manager.get_ground_level()

player = Player((SCREEN_WIDTH // 2 - 50, current_ground_level - 80))

all_enemies = pygame.sprite.Group()
spells = pygame.sprite.Group()

wave_definitions = [
    [(SkeletonEnemy, 3)],
    [(SkeletonEnemy, 3), (BringerOfDeathEnemy, 2)],
    [(NightBorneEnemy, 1), (SkeletonEnemy, 2)]
]

wave_manager = WaveManager(wave_definitions, all_enemies, SCREEN_WIDTH, current_ground_level, room_manager)

def draw_text(surface, text, pos, color=(255, 255, 255), size=36):
    font = pygame.font.SysFont(None, size)
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, pos)

def draw_health_bar(surface, player, pos=(20, 20), size=(200, 20)):
    pygame.draw.rect(surface, (255, 0, 0), (*pos, size[0], size[1]))
    current_width = size[0] * (player.health / player.max_health)
    pygame.draw.rect(surface, (0, 255, 0), (*pos, current_width, size[1]))
    pygame.draw.rect(surface, (255, 255, 255), (*pos, size[0], size[1]), 2)

running = True
while running:
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    current_ground_level = room_manager.get_ground_level()

    # ✅ Sempre permitir o player se mover
    player.update(keys, current_ground_level, SCREEN_WIDTH)

    # ✅ Atualizar waves sempre que houver inimigos ou uma wave em andamento
    if len(all_enemies) > 0 or wave_manager.wave_in_progress:
        wave_manager.update()

    # ✅ Iniciar próxima wave automaticamente na sala 1
    if not wave_manager.wave_in_progress and len(all_enemies) == 0 and room_manager.current_room == 1:
        wave_manager.start_next_wave()

    # ✅ Troca de salas
    if player.rect.right >= SCREEN_WIDTH - 10:
        if room_manager.current_room == 1:
            if wave_manager.current_wave > len(wave_definitions):
                room_manager.next_room()
                current_ground_level = room_manager.get_ground_level()
                player.rect.topleft = (50, current_ground_level - 80)
        elif room_manager.current_room == 2:
            room_manager.next_room()
            current_ground_level = room_manager.get_ground_level()
            player.rect.topleft = (50, current_ground_level - 80)

    if room_manager.current_room == 0 and room_manager.player_at_door(player):
        if keys[pygame.K_e]:
            room_manager.next_room()
            current_ground_level = room_manager.get_ground_level()
            player.rect.topleft = (50, current_ground_level - 80)

    room_manager.draw_room(screen)
    player.draw(screen)
    room_manager.draw_foreground(screen)

    for enemy in all_enemies:
        if isinstance(enemy, BringerOfDeathEnemy):
            enemy.update(player)
            now = pygame.time.get_ticks()
            if enemy.state == "cast" and now - enemy.last_attack_time < 500:
                spell = SpellEffect(player.rect.center, enemy.animations["spell"])
                spells.add(spell)
        else:
            enemy.update(player)
        enemy.draw(screen)

    for spell in spells:
        spell.update(player)
        spell.draw(screen)

    if room_manager.current_room == 0 and room_manager.player_at_door(player):
        draw_text(
            screen,
            "Pressione E para entrar no castelo",
            (SCREEN_WIDTH // 2 - 200, current_ground_level - 600),
            color=(255, 255, 0),
            size=36
        )

    draw_health_bar(screen, player)

    if not player.alive:
        draw_text(screen, "Você morreu! Pressione R para reiniciar", 
                  (SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2), (255, 0, 0), size=40)
        if keys[pygame.K_r]:
            player = Player((SCREEN_WIDTH // 2 - 50, current_ground_level - 80))
            player.health = player.max_health
            player.alive = True
            wave_manager = WaveManager(wave_definitions, all_enemies, SCREEN_WIDTH, current_ground_level, room_manager)
            all_enemies.empty()
            spells.empty()
            room_manager.current_room = 0

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
