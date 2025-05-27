"""
Módulo principal do jogo **Hollow Mooni**.

Aqui rola todo o fluxo do game: inicialização do Pygame, estados de tela
(menu inicial, lore e gameplay), gerenciamento de salas (`RoomManager`),
ondas de inimigos (`WaveManager`) e o combate contra o chefe final
(`KnightBoss`).  
Execução típica (a partir da raiz do projeto):

    $ python main.py

Requisitos:
-----------
- Estrutura de diretórios descrita no README (assets/, core/, etc.).
- Pygame instalado (`pip install pygame`).
"""

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
pygame.mixer.init()

# ================== CONFIG GLOBAL ==================
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
BOSS_Y_OFFSET = -125            # deixa os pés do boss nivelados com o player
PLAYER_CENTER_OFFSET = 50       # metade da largura do player (~) para sala 0

# ================== ÁUDIO ==========================
pygame.mixer.music.load('assets/sounds/backgroundprinci.mp3')
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

# ================== JANELA =========================
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Hollow Mooni - Room System")
clock = pygame.time.Clock()


# =============== POSICIONAMENTO ====================
def position_player_for_room(room_id, player):
    """
    Posiciona o jogador na coordenada X correta ao entrar em cada sala.

    Parâmetros
    ----------
    room_id : int
        ID numérico da sala (0, 1, 2…).
    player : Player
        Instância do jogador cuja posição será modificada.
    """
    if room_id == 0:
        player.rect.centerx = SCREEN_WIDTH // 2 - PLAYER_CENTER_OFFSET
    else:                      # salas 1 e 2
        player.rect.left = 50


# =============== TELA INICIAL ======================
game_state = -2  # -2: start screen | -1: lore | 0+: jogo

start_screen = pygame.image.load('assets/background/telainicial.png')
start_screen = pygame.transform.scale(start_screen, (SCREEN_WIDTH, SCREEN_HEIGHT))
font_ui = pygame.font.SysFont(None, 60)
button_text = font_ui.render('INICIAR', True, (255, 255, 255))
button_rect = button_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))

# =============== INTRODUÇÃO ========================
intro_image = pygame.image.load('assets/background/introducao1.png')
intro_image = pygame.transform.scale(intro_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
intro_font = pygame.font.SysFont('timesnewroman', 36)
lore_lines = [
    "Em um reino outrora próspero,",
    "uma terrível maldição selou seu destino.",
    "O Rei Mooni pereceu de forma misteriosa,",
    "enquanto seus súditos, amaldiçoados,",
    "foram condenados a proteger eternamente",
    "um rei que já não existe mais.",
    "",
    "Agora, renascido em outra forma,",
    "Rei Mooni busca quebrar a maldição,",
    "e libertar seus amados súditos,",
    "sobretudo seu melhor amigo,",
    "antes que tudo se perca para sempre.",
    "Pressione ENTER para continuar..."
]

# =============== SETUP DE JOGO =====================
room_manager = RoomManager(SCREEN_WIDTH, SCREEN_HEIGHT)
current_ground_level = room_manager.get_ground_level()

player = Player((0, 0))
player.rect.bottom = current_ground_level
position_player_for_room(room_manager.current_room, player)
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
boss_dialogue = [
    "Então é você mais um a perecer para essa maldição...",
    "Eu era o melhor amigo do rei... minha missão era salvá-lo...",
    "Mas eu falhei... e falharei novamente agora que mais um inocente cairá",
    "Mas você... eu reconheço...",
    "Meu rei... mesmo em outra forma...",
    "Por favor... salve-nos desta maldição... e me conceda seu perdão...",
]
current_dialogue_index = 0
dialogue_start_time = None


# =============== FUNÇÕES AUXILIARES ================
def draw_text(surface, text, pos, color=(255, 255, 255), size=36):
    """
    Desenha texto simples na tela.

    Parameters
    ----------
    surface : pygame.Surface
        Onde o texto será renderizado.
    text : str
        Conteúdo a ser exibido.
    pos : tuple[int, int]
        Coordenadas (x, y) no `surface`.
    color : tuple[int, int, int], opcional
        Cor RGB do texto.
    size : int, opcional
        Tamanho da fonte.
    """
    surface.blit(pygame.font.SysFont(None, size).render(text, True, color), pos)


def draw_health_bar(surface, player, pos=(20, 20), size=(200, 20)):
    """
    Desenha a barra de vida do jogador.

    Parameters
    ----------
    surface : pygame.Surface
        Tela ou subsuperfície de destino.
    player : Player
        Instância do jogador (precisa ter `health` e `max_health`).
    pos : tuple[int, int], opcional
        Posição da barra.
    size : tuple[int, int], opcional
        Largura e altura da barra.
    """
    pygame.draw.rect(surface, (255, 0, 0), (*pos, *size))
    pygame.draw.rect(
        surface,
        (0, 255, 0),
        (*pos, size[0] * (player.health / player.max_health), size[1]),
    )
    pygame.draw.rect(surface, (255, 255, 255), (*pos, *size), 2)


def draw_boss_health_bar(surface, boss, pos=(SCREEN_WIDTH // 2 - 150, 20), size=(300, 20)):
    """
    Desenha a barra de vida do chefe.

    Parameters
    ----------
    surface : pygame.Surface
        Tela ou subsuperfície de destino.
    boss : KnightBoss
        Instância do chefe (precisa ter `hp`).
    pos : tuple[int, int], opcional
        Posição da barra.
    size : tuple[int, int], opcional
        Largura e altura da barra.
    """
    pygame.draw.rect(surface, (255, 0, 0), (*pos, *size))
    pygame.draw.rect(
        surface,
        (0, 255, 0),
        (*pos, size[0] * (boss.hp / 200), size[1]),
    )
    pygame.draw.rect(surface, (255, 255, 255), (*pos, *size), 2)


def hitbox_thrust(player, length, height, offset_y=0):
    """
    Retorna um `pygame.Rect` representando a área de dano do ataque *thrust*.

    Parameters
    ----------
    player : Player
        Jogador executando o ataque.
    length : int
        Comprimento horizontal do hitbox.
    height : int
        Altura vertical do hitbox.
    offset_y : int, opcional
        Deslocamento vertical adicional.

    Returns
    -------
    pygame.Rect
        Retângulo de colisão do ataque.
    """
    if player.facing_right:
        return pygame.Rect(
            player.rect.centerx,
            player.rect.centery - height // 2 + offset_y,
            length,
            height,
        )
    return pygame.Rect(
        player.rect.centerx - length,
        player.rect.centery - height // 2 + offset_y,
        length,
        height,
    )


def hitbox_smash(player, width, height, offset_y=0):
    """
    Retorna um `pygame.Rect` representando a área de dano do ataque *smash*.

    Parameters
    ----------
    player : Player
        Jogador executando o ataque.
    width : int
        Largura do hitbox.
    height : int
        Altura do hitbox.
    offset_y : int, opcional
        Deslocamento vertical adicional.

    Returns
    -------
    pygame.Rect
        Retângulo de colisão do ataque.
    """
    if player.facing_right:
        return pygame.Rect(player.rect.centerx, player.rect.top + offset_y, width, height)
    return pygame.Rect(
        player.rect.centerx - width, player.rect.top + offset_y, width, height
    )


def apply_damage(hitbox, enemies, damage):
    """
    Aplica dano aos inimigos que colidem com o `hitbox`.

    Parameters
    ----------
    hitbox : pygame.Rect
        Retângulo de colisão do ataque.
    enemies : pygame.sprite.Group
        Grupo com instâncias de inimigos.
    damage : int
        Quantidade de dano a ser aplicada.
    """
    for enemy in enemies:
        if hitbox.colliderect(enemy.rect) and not enemy.recently_hit:
            enemy.take_damage(damage)
            enemy.recently_hit = True


def check_player_attack(player, enemies):
    """
    Verifica se o jogador acertou algum inimigo no frame atual.

    Deve ser chamada uma vez por frame após `player.update()`.

    Parameters
    ----------
    player : Player
        Jogador em ação.
    enemies : pygame.sprite.Group
        Grupo de inimigos suscetíveis a levar dano.
    """
    if player.state in ("smash", "thrust"):
        dmg = player.attack_damage[player.state]
        frame = int(player.frame_index)

        if player.state == "smash" and 8 <= frame <= 12:
            apply_damage(hitbox_smash(player, 96, 80, 20), enemies, dmg)

        elif player.state == "thrust" and frame == 6:
            apply_damage(hitbox_thrust(player, 100, 10), enemies, dmg)


# ================= LOOP PRINCIPAL ==================
running = True
while running:
    keys = pygame.key.get_pressed()

    # ---------- EVENTOS ----------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if game_state == -2 and event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos):
                game_state = -1
        elif game_state == -1 and event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            game_state = 0

    # ---------- TELAS ----------
    if game_state == -2:  # Start screen
        screen.blit(start_screen, (0, 0))
        hover = button_rect.collidepoint(pygame.mouse.get_pos())
        col = (50, 80, 80) if hover else (30, 60, 60)
        pygame.draw.rect(screen, col, button_rect.inflate(30, 15), border_radius=10)
        screen.blit(button_text, button_rect)

    elif game_state == -1:  # Lore
        screen.blit(intro_image, (0, 0))
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        for i, line in enumerate(lore_lines):
            screen.blit(intro_font.render(line, True, (255, 255, 255)), (50, 50 + i * 50))

    else:  # ============ JOGO ============
        current_ground_level = room_manager.get_ground_level()

        # Flags para prompts
        show_castle_prompt = False
        show_patio_prompt = False

        # ----- Permitir movimento? -----
        if room_manager.current_room == 0:
            player_can_move = False
        elif room_manager.current_room == 2 and boss and boss.passive:
            player_can_move = False
        else:
            player_can_move = True

        if player_can_move:
            player.update(keys, current_ground_level, SCREEN_WIDTH)

        check_player_attack(player, all_enemies)

        # ----- Boss recebe dano -----
        if boss and player.state in ("smash", "thrust"):
            dmg = player.attack_damage[player.state]
            frame = int(player.frame_index)
            if player.state == "smash" and 8 <= frame <= 12:
                if hitbox_smash(player, 96, 80, 20).colliderect(boss.rect):
                    boss.take_damage(dmg)
            elif player.state == "thrust" and frame == 6:
                if hitbox_thrust(player, 100, 10).colliderect(boss.rect):
                    boss.take_damage(dmg)

        # ----- Reset flag de recently_hit -----
        if player.state not in ("smash", "thrust"):
            for e in all_enemies:
                e.recently_hit = False

        # ----- Spawning de waves -----
        if room_manager.current_room == 1 and wave_manager is None:
            wave_manager = WaveManager(
                wave_definitions, all_enemies, SCREEN_WIDTH, current_ground_level, room_manager
            )
            wave_manager.start_next_wave()

        if wave_manager:
            if len(all_enemies) > 0 or wave_manager.wave_in_progress:
                wave_manager.update()
            if (
                not wave_manager.wave_in_progress
                and len(all_enemies) == 0
                and wave_manager.current_wave <= len(wave_definitions)
            ):
                wave_manager.start_next_wave()

        # ----- Mensagem pós-waves (sala 1) -----
        if (
            wave_manager
            and wave_manager.current_wave > len(wave_definitions)
            and len(all_enemies) == 0
        ):
            show_patio_prompt = True
            if keys[pygame.K_e]:
                room_manager.next_room()
                current_ground_level = room_manager.get_ground_level()
                player.rect.bottom = current_ground_level
                position_player_for_room(room_manager.current_room, player)
                player.health = player.max_health
                wave_manager = None
                all_enemies.empty()

                if room_manager.current_room == 2:
                    boss = KnightBoss(
                        (SCREEN_WIDTH // 2 - 100, current_ground_level - 100), current_ground_level
                    )
                    boss.rect.bottom = current_ground_level
                    boss.rect.y += BOSS_Y_OFFSET  # alinhamento vertical
                    boss.state = "pray"
                    boss.passive = True
                    boss.animation_index = 3
                    boss_group = pygame.sprite.GroupSingle(boss)
                    boss_intro_time = pygame.time.get_ticks()
                    dialogue_start_time = boss_intro_time
                    current_dialogue_index = 0

        # ----- Porta do castelo (0→1) -----
        if room_manager.current_room == 0:
            show_castle_prompt = True
            if keys[pygame.K_e]:
                room_manager.next_room()
                player.rect.bottom = room_manager.get_ground_level()
                position_player_for_room(room_manager.current_room, player)

        # ----- Desenho de cenário e entidades -----
        room_manager.draw_room(screen)
        player.draw(screen)
        room_manager.draw_foreground(screen)

        for enemy in all_enemies:
            if isinstance(enemy, BringerOfDeathEnemy):
                enemy.update(player, spells)
            else:
                enemy.update(player)
            enemy.draw(screen)

        for sp in spells:
            sp.update(player)
            sp.draw(screen)

        # ----- Boss room (diálogo / luta) -----
        if room_manager.current_room == 2 and boss:
            if boss.passive:
                boss.state, boss.animation_index = "pray", 3
                boss.image = boss.animations["pray"][boss.animation_index]
                now = pygame.time.get_ticks()
                if current_dialogue_index < len(boss_dialogue):
                    draw_text(
                        screen,
                        boss_dialogue[current_dialogue_index],
                        (SCREEN_WIDTH // 2 - 300, current_ground_level - 75),
                        (255, 255, 255),
                        30,
                    )
                    if now - dialogue_start_time > 3000:
                        current_dialogue_index += 1
                        dialogue_start_time = now
                else:
                    boss.passive, boss.state = False, "idle"
            else:
                boss_group.update(player, clock.get_time())
                boss.check_attack_collision(player)

            boss.draw(screen)
            draw_boss_health_bar(screen, boss)

            if boss.hp <= 0 and boss.state == "death":
                draw_text(
                    screen,
                    "Você libertou o seu povo!",
                    (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2),
                    (0, 255, 0),
                    40,
                )
                draw_text(
                    screen,
                    "Pressione E para finalmente descansar em paz.",
                    (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 50),
                    (255, 255, 255),
                    30,
                )
                if keys[pygame.K_e]:
                    running = False

        draw_health_bar(screen, player)

        # ----- Reinício (tecla R) -----
        if not player.alive:
            draw_text(
                screen,
                "Você morreu! Pressione R para reiniciar",
                (SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2),
                (255, 0, 0),
                40,
            )
            if keys[pygame.K_r]:
                room_manager.current_room = 0
                current_ground_level = room_manager.get_ground_level()

                player = Player((0, 0))
                player.rect.bottom = current_ground_level
                position_player_for_room(0, player)
                player.attack_damage = {"smash": 15, "thrust": 10}
                player.health, player.alive = player.max_health, True

                wave_manager = None
                all_enemies.empty()
                spells.empty()
                boss, boss_group, boss_intro_time = None, None, None
                current_dialogue_index, waves_completed = 0, False

        # ----- DESENHA PROMPTS POR CIMA -----
        if show_castle_prompt:
            draw_text(
                screen,
                "Pressione E para entrar no castelo",
                (SCREEN_WIDTH // 2 - 200, current_ground_level - 300),
                (255, 255, 0),
                36,
            )

        if show_patio_prompt:
            draw_text(
                screen,
                "Pressione E para avançar para o pátio e encontrar um velho conhecido",
                (SCREEN_WIDTH // 2 - 340, current_ground_level - 100),
                (255, 255, 0),
                28,
            )

    # ========== FLIP & FPS ==========
    pygame.display.flip()
    clock.tick(90 if game_state == 0 and room_manager.current_room == 2 else 60)

pygame.quit()
