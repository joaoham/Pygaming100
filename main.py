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

player.attack_damage = {
    "smash": 15,
    "thrust": 10
}

all_enemies = pygame.sprite.Group()
spells = pygame.sprite.Group()

wave_definitions = [
    [(SkeletonEnemy, 3)],
    [(SkeletonEnemy, 3), (BringerOfDeathEnemy, 2)],
    [(NightBorneEnemy, 1), (SkeletonEnemy, 2)]
]

wave_manager = None

def draw_text(surface, text, pos, color=(255, 255, 255), size=36):
    font = pygame.font.SysFont(None, size)
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, pos)

def draw_health_bar(surface, player, pos=(20, 20), size=(200, 20)):
    pygame.draw.rect(surface, (255, 0, 0), (*pos, size[0], size[1]))
    current_width = size[0] * (player.health / player.max_health)
    pygame.draw.rect(surface, (0, 255, 0), (*pos, current_width, size[1]))
    pygame.draw.rect(surface, (255, 255, 255), (*pos, size[0], size[1]), 2)

# ✅ Cria hitbox para THRUST — começa no centro do player
def create_hitbox_thrust(player, length, height, offset_y=0):
    if player.facing_right:
        hitbox = pygame.Rect(
            player.rect.centerx,
            player.rect.centery - height // 2 + offset_y,
            length,
            height
        )
    else:
        hitbox = pygame.Rect(
            player.rect.centerx - length,
            player.rect.centery - height // 2 + offset_y,
            length,
            height
        )
    return hitbox

# ✅ Cria hitbox para SMASH — também começa no centro
def create_hitbox_smash(player, width, height, offset_y=0):
    if player.facing_right:
        hitbox = pygame.Rect(
            player.rect.centerx,
            player.rect.top + offset_y,
            width,
            height
        )
    else:
        hitbox = pygame.Rect(
            player.rect.centerx - width,
            player.rect.top + offset_y,
            width,
            height
        )
    return hitbox

# ✅ Aplica dano se colidir
def _apply_damage(hitbox, enemies, damage):
    for enemy in enemies:
        if hitbox.colliderect(enemy.rect):
            if not enemy.recently_hit:
                enemy.take_damage(damage)
                enemy.recently_hit = True

# ✅ Só causa dano se o golpe passar pela área real
def check_player_attack(player, enemies):
    if player.state in ["smash", "thrust"]:
        damage = player.attack_damage[player.state]
        current_frame = int(player.frame_index)

        print(f"{player.state.capitalize()} frame: {current_frame}")

        if player.state == "smash" and 8 <= current_frame <= 12:
            hitbox = create_hitbox_smash(player, width=96, height=80, offset_y=20)
            _apply_damage(hitbox, enemies, damage)
            pygame.draw.rect(screen, (255, 0, 0), hitbox, 2)

        elif player.state == "thrust" and current_frame == 6:
            hitbox = create_hitbox_thrust(player, length=100, height=10, offset_y=0)
            _apply_damage(hitbox, enemies, damage)
            pygame.draw.rect(screen, (255, 0, 0), hitbox, 2)

running = True
while running:
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    current_ground_level = room_manager.get_ground_level()

    if room_manager.current_room == 1:
        player.speed = 7
    elif room_manager.current_room == 2:
        player.speed = 9
    else:
        player.speed = 7

    player.update(keys, current_ground_level, SCREEN_WIDTH)

    check_player_attack(player, all_enemies)

    if player.state not in ["smash", "thrust"]:
        for enemy in all_enemies:
            enemy.recently_hit = False

    if room_manager.current_room == 1 and wave_manager is None:
        wave_manager = WaveManager(wave_definitions, all_enemies, SCREEN_WIDTH, current_ground_level, room_manager)
        wave_manager.start_next_wave()

    if wave_manager:
        if len(all_enemies) > 0 or wave_manager.wave_in_progress:
            wave_manager.update()

        if not wave_manager.wave_in_progress and len(all_enemies) == 0:
            wave_manager.start_next_wave()

    for enemy in all_enemies:
        if room_manager.current_room == 2:
            enemy.speed = 3
        else:
            enemy.speed = 2

    if player.rect.right >= SCREEN_WIDTH - 10:
        room_manager.next_room()
        current_ground_level = room_manager.get_ground_level()
        player.rect.topleft = (50, current_ground_level - 80)
        if room_manager.current_room != 1:
            wave_manager = None
            all_enemies.empty()

    if room_manager.current_room == 0 and room_manager.player_at_door(player):
        if keys[pygame.K_e]:
            room_manager.next_room()
            current_ground_level = room_manager.get_ground_level()
            player.rect.topleft = (50, current_ground_level - 80)

    room_manager.draw_room(screen)
    player.draw(screen)
    room_manager.draw_foreground(screen)

    for enemy in all_enemies:
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
            player.attack_damage = {"smash": 15, "thrust": 10}
            player.health = player.max_health
            player.alive = True
            wave_manager = None
            all_enemies.empty()
            spells.empty()
            room_manager.current_room = 0

    pygame.display.flip()

    if room_manager.current_room == 2:
        clock.tick(90)
    else:
        clock.tick(60)

pygame.quit()
