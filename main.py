import pygame
from core.player import Player
from core.room_manager import RoomManager
from core.wave_manager import WaveManager
from core.skeleton import SkeletonEnemy
from core.nightborne import NightBorneEnemy
from core.bringer import BringerOfDeathEnemy
from core.spell_effect import SpellEffect
from core.knight_boss import KnightBoss

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Hollow Mooni - Room System")
clock = pygame.time.Clock()

room_manager = RoomManager(SCREEN_WIDTH, SCREEN_HEIGHT)
current_ground_level = room_manager.get_ground_level()

player = Player((SCREEN_WIDTH - 250, current_ground_level - 100))
player.rect.bottom = current_ground_level
player.attack_damage = {"smash": 15, "thrust": 10}

all_enemies = pygame.sprite.Group()
spells = pygame.sprite.Group()

wave_definitions = [
    [(SkeletonEnemy, 3)],
    [(SkeletonEnemy, 2), (BringerOfDeathEnemy, 1)],
    [(NightBorneEnemy, 1), (SkeletonEnemy, 2)],
]

wave_manager = None
waves_completed = False
boss = None
boss_group = None
boss_intro_time = None
player_can_move = True

boss_dialogue = [
    "Este reino... foi amaldiçoado...",
    "Eu era o melhor amigo do rei... minha missão era salvá-lo...",
    "Mas eu falhei... e me amaldiçoei a guardar este castelo pela eternidade...",
    "Mas você... eu reconheço...",
    "Meu rei... mesmo em outra forma...",
    "Por favor... salve-nos desta maldição... e me conceda seu perdão...",
]
current_dialogue_index = 0
dialogue_start_time = None

def draw_text(surface, text, pos, color=(255, 255, 255), size=36):
    font = pygame.font.SysFont(None, size)
    surface.blit(font.render(text, True, color), pos)

def draw_health_bar(surface, player, pos=(20, 20), size=(200, 20)):
    pygame.draw.rect(surface, (255, 0, 0), (*pos, *size))
    current_width = size[0] * (player.health / player.max_health)
    pygame.draw.rect(surface, (0, 255, 0), (*pos, current_width, size[1]))
    pygame.draw.rect(surface, (255, 255, 255), (*pos, *size), 2)

def draw_boss_health_bar(surface, boss, pos=(SCREEN_WIDTH // 2 - 150, 20), size=(300, 20)):
    pygame.draw.rect(surface, (255, 0, 0), (*pos, *size))
    current_width = size[0] * (boss.hp / 200)
    pygame.draw.rect(surface, (0, 255, 0), (*pos, current_width, size[1]))
    pygame.draw.rect(surface, (255, 255, 255), (*pos, *size), 2)

def create_hitbox_thrust(player, length, height, offset_y=0):
    if player.facing_right:
        return pygame.Rect(player.rect.centerx, player.rect.centery - height // 2 + offset_y, length, height)
    return pygame.Rect(player.rect.centerx - length, player.rect.centery - height // 2 + offset_y, length, height)

def create_hitbox_smash(player, width, height, offset_y=0):
    if player.facing_right:
        return pygame.Rect(player.rect.centerx, player.rect.top + offset_y, width, height)
    return pygame.Rect(player.rect.centerx - width, player.rect.top + offset_y, width, height)

def _apply_damage(hitbox, enemies, damage):
    for enemy in enemies:
        if hitbox.colliderect(enemy.rect) and not enemy.recently_hit:
            enemy.take_damage(damage)
            enemy.recently_hit = True

def check_player_attack(player, enemies):
    if player.state in ["smash", "thrust"]:
        damage = player.attack_damage[player.state]
        current_frame = int(player.frame_index)

        if player.state == "smash" and 8 <= current_frame <= 12:
            hitbox = create_hitbox_smash(player, width=96, height=80, offset_y=20)
            _apply_damage(hitbox, enemies, damage)
        elif player.state == "thrust" and current_frame == 6:
            hitbox = create_hitbox_thrust(player, length=100, height=10, offset_y=0)
            _apply_damage(hitbox, enemies, damage)

running = True
while running:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    current_ground_level = room_manager.get_ground_level()

    if player_can_move:
        player.update(keys, current_ground_level, SCREEN_WIDTH)

    check_player_attack(player, all_enemies)

    if boss and player.state in ["smash", "thrust"]:
        damage = player.attack_damage[player.state]
        current_frame = int(player.frame_index)

        if player.state == "smash" and 8 <= current_frame <= 12:
            if create_hitbox_smash(player, 96, 80, 20).colliderect(boss.rect):
                boss.take_damage(damage)
        elif player.state == "thrust" and current_frame == 6:
            if create_hitbox_thrust(player, 100, 10).colliderect(boss.rect):
                boss.take_damage(damage)

    if player.state not in ["smash", "thrust"]:
        for enemy in all_enemies:
            enemy.recently_hit = False

    if room_manager.current_room == 1 and wave_manager is None:
        wave_manager = WaveManager(wave_definitions, all_enemies, SCREEN_WIDTH, current_ground_level, room_manager)
        wave_manager.start_next_wave()
        waves_completed = False

    if wave_manager:
        if len(all_enemies) > 0 or wave_manager.wave_in_progress:
            wave_manager.update()

        if (not wave_manager.wave_in_progress and len(all_enemies) == 0 and wave_manager.current_wave <= len(wave_definitions)):
            wave_manager.start_next_wave()

        if (not waves_completed and wave_manager.current_wave > len(wave_definitions) and len(all_enemies) == 0):
            print("✅ Todas as waves concluídas!")
            waves_completed = True

    for enemy in all_enemies:
        enemy.speed = 3 if room_manager.current_room == 2 else 2

    if wave_manager and wave_manager.current_wave > len(wave_definitions):
        draw_text(screen, "Pressione E para avançar para o pátio", (SCREEN_WIDTH // 2 - 200, current_ground_level - 100), (255, 255, 0), 36)

        if keys[pygame.K_e]:
            room_manager.next_room()
            current_ground_level = room_manager.get_ground_level()
            player.rect.bottom = current_ground_level
            player.health = player.max_health
            wave_manager = None
            all_enemies.empty()

            if room_manager.current_room == 2:
                boss = KnightBoss((SCREEN_WIDTH // 2 - 100, current_ground_level - 100), current_ground_level)
                boss.rect.bottom = current_ground_level
                boss.rect.y = player.rect.y
                boss.state = "pray"
                boss.passive = True
                boss.animation_index = 3
                boss_group = pygame.sprite.GroupSingle(boss)
                boss_intro_time = pygame.time.get_ticks()
                dialogue_start_time = boss_intro_time
                player_can_move, current_dialogue_index = False, 0

    if room_manager.current_room == 0 and room_manager.player_at_door(player):
        if keys[pygame.K_e]:
            room_manager.next_room()
            player.rect.bottom = room_manager.get_ground_level()

    room_manager.draw_room(screen)
    player.draw(screen)
    room_manager.draw_foreground(screen)

    for enemy in all_enemies:
        if isinstance(enemy, BringerOfDeathEnemy):
            enemy.update(player, spells)
        else:
            enemy.update(player)
        enemy.draw(screen)

    for spell in spells:
        spell.update(player)
        spell.draw(screen)

    if room_manager.current_room == 0 and room_manager.player_at_door(player):
        draw_text(screen, "Pressione E para entrar no castelo", (SCREEN_WIDTH // 2 - 200, current_ground_level - 100), (255, 255, 0), 36)

    if room_manager.current_room == 2 and boss:
        current_time = pygame.time.get_ticks()

        if boss.passive:
            boss.state, boss.animation_index = "pray", 3
            boss.image = boss.animations[boss.state][boss.animation_index]

            if current_dialogue_index < len(boss_dialogue):
                draw_text(screen, boss_dialogue[current_dialogue_index], (SCREEN_WIDTH // 2 - 300, current_ground_level - 150), color=(255, 255, 255), size=30)
                if current_time - dialogue_start_time > 2000:
                    current_dialogue_index += 1
                    dialogue_start_time = current_time
            else:
                boss.passive, boss.state, boss.dialogue_done = False, "idle", True
                player_can_move = True
        else:
            boss_group.update(player, clock.get_time())
            boss.check_attack_collision(player)

        boss.draw(screen)
        draw_boss_health_bar(screen, boss)

        if boss.hp <= 0 and boss.state == "death":
            draw_text(screen, "Você venceu o Boss! Parabéns!", (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2), (0, 255, 0), 40)
            draw_text(screen, "Pressione E para encerrar", (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50), (255, 255, 255), 30)
            if keys[pygame.K_e]:
                running = False

    draw_health_bar(screen, player)

    if not player.alive:
        draw_text(screen, "Você morreu! Pressione R para reiniciar", (SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2), (255, 0, 0), 40)
        if keys[pygame.K_r]:
            player = Player((SCREEN_WIDTH - 250, current_ground_level - 100))
            player.rect.bottom = current_ground_level
            player.attack_damage = {"smash": 15, "thrust": 10}
            player.health, player.alive = player.max_health, True
            wave_manager = None
            all_enemies.empty()
            spells.empty()
            room_manager.current_room = 0
            boss, boss_group, boss_intro_time = None, None, None
            player_can_move, current_dialogue_index, waves_completed = True, 0, False

    pygame.display.flip()

    clock.tick(90 if room_manager.current_room == 2 else 60)

pygame.quit()