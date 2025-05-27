"""
Módulo que define o inimigo **Bringer of Death**.

Ele persegue o player, ataca corpo a corpo se chegar perto e,
caso contrário, lança um feitiço à distância. Usa animações
carregadas de subpastas em `assets/enemies/bringer/`.

Fluxo básico dentro do jogo:
----------------------------
1. `update()` calcula lógica de movimento/estado.  
2. `animate()` avança quadros, dispara ataque/dano ou feitiço.  
3. `draw()` renderiza o frame atual no `surface` recebido.
"""

import pygame
import os
from core.spell_effect import SpellEffect


class BringerOfDeathEnemy(pygame.sprite.Sprite):
    """
    Inimigo “Bringer of Death”.

    Parâmetros
    ----------
    pos : tuple[int, int]
        Posição inicial (x, y) no mapa.
    scale : float, opcional
        Fator de escala para as sprites (padrão = 1.0).
    """

    def __init__(self, pos, scale=1.0):
        super().__init__()

        self.speed = 1
        self.max_health = 100
        self.health = self.max_health
        self.damage = 15
        self.attack_cooldown = 1500  # ms entre ataques
        self.last_attack_time = pygame.time.get_ticks()
        self.facing_right = True
        self.has_cast_spell = False
        self.has_attacked = False
        self.scale = scale
        self.recently_hit = False

        base_path = "assets/enemies/bringer"

        # Carrega todas as animações em um dicionário
        self.animations = {
            "idle": self.load_animation_from_folder(os.path.join(base_path, "Idle")),
            "walk": self.load_animation_from_folder(os.path.join(base_path, "Walk")),
            "attack": self.load_animation_from_folder(os.path.join(base_path, "Attack")),
            "hurt": self.load_animation_from_folder(os.path.join(base_path, "Hurt")),
            "death": self.load_animation_from_folder(os.path.join(base_path, "Death")),
            "cast": self.load_animation_from_folder(os.path.join(base_path, "Cast")),
            "spell": self.load_animation_from_folder(os.path.join(base_path, "Spell")),
        }

        self.state = "idle"
        self.frame_index = 0
        self.animation_speed = 0.35
        self.death_animation_speed = 0.07
        self.hurt_animation_speed = 0.07
        self.image = self.animations[self.state][int(self.frame_index)]

        ajuste_altura = 40  # centraliza o pé da sprite com o chão
        self.rect = self.image.get_rect(midbottom=(pos[0], pos[1] - ajuste_altura))

        self.death_timer = None

    # ---------------------------------------------------------------------
    # Métodos auxiliares
    # ---------------------------------------------------------------------

    def load_animation_from_folder(self, folder_path):
        """
        Lê todos os `.png` de `folder_path` e devolve uma lista de frames.

        Retorna
        -------
        list[pygame.Surface]
            Quadros sequenciais já redimensionados (se `scale` ≠ 1.0).
        """
        frames = []
        for filename in sorted(os.listdir(folder_path)):
            if filename.endswith(".png"):
                image = pygame.image.load(os.path.join(folder_path, filename)).convert_alpha()
                if self.scale != 1.0:
                    new_size = (
                        int(image.get_width() * self.scale),
                        int(image.get_height() * self.scale),
                    )
                    image = pygame.transform.scale(image, new_size)
                frames.append(image)
        return frames

    # ---------------------------------------------------------------------
    # Loop principal do inimigo
    # ---------------------------------------------------------------------

    def update(self, player, spell_group):
        """
        Atualiza estado, movimento e decide se ataca/casta.

        Parameters
        ----------
        player : Player
            Instância do jogador (usada para distância e colisão).
        spell_group : pygame.sprite.Group
            Grupo onde novos feitiços serão inseridos.
        """
        if self.health > 0 and self.state not in ["cast", "attack", "hurt", "death"]:
            distance = player.rect.centerx - self.rect.centerx
            direction = 1 if distance > 0 else -1
            self.facing_right = direction > 0

            # Sempre anda em direção ao player
            self.state = "walk"
            self.rect.x += direction * self.speed

            now = pygame.time.get_ticks()

            if abs(distance) < 100:
                # Ataque corpo a corpo
                if now - self.last_attack_time > self.attack_cooldown:
                    self.state = "attack"
                    self.frame_index = 0
                    self.has_attacked = False
                    self.last_attack_time = now
            else:
                # Lança feitiço à distância
                if now - self.last_attack_time > self.attack_cooldown:
                    self.state = "cast"
                    self.frame_index = 0
                    self.has_cast_spell = False
                    self.last_attack_time = now

        self.animate(player, spell_group)

    # ---------------------------------------------------------------------
    # Ações
    # ---------------------------------------------------------------------

    def attack(self, player):
        """Causa dano direto ao player."""
        player.take_damage(self.damage)

    def cast_spell(self, player, spell_group):
        """Instancia um feitiço direcionado ao player."""
        spell_pos = (player.rect.centerx, player.rect.top - 20)
        spell = SpellEffect(spell_pos, self.animations["spell"])
        spell_group.add(spell)
        print("Bringer lançou feitiço no player!")  # debug maroto

    def take_damage(self, amount):
        """
        Recebe dano e troca para estado apropriado.

        Parameters
        ----------
        amount : int
            Quantidade de dano.
        """
        self.health -= amount
        print(f"Bringer HP: {self.health}")  # feedback rápido no console
        if self.health <= 0:
            self.state = "death"
            self.frame_index = 0
            self.death_timer = pygame.time.get_ticks()
        else:
            if self.state != "hurt":
                self.state = "hurt"
                self.frame_index = 0

    # ---------------------------------------------------------------------
    # Animação e renderização
    # ---------------------------------------------------------------------

    def animate(self, player, spell_group):
        """
        Controla avanço de quadros e transições de estado.

        Chamado a cada frame pelo `update()` do jogo.
        """
        frames = self.animations[self.state]

        # Velocidades diferentes pra cada estado
        if self.state == "death":
            self.frame_index += self.death_animation_speed
        elif self.state == "hurt":
            self.frame_index += self.hurt_animation_speed
        else:
            self.frame_index += self.animation_speed

        # Lógica específica de cada estado
        if self.state == "cast":
            if not self.has_cast_spell and int(self.frame_index) == 5:
                self.cast_spell(player, spell_group)
                self.has_cast_spell = True
            if self.frame_index >= len(frames):
                self.frame_index = 0
                self.state = "idle"

        elif self.state == "attack":
            if not self.has_attacked and int(self.frame_index) == 5:
                self.attack(player)
                self.has_attacked = True
            if self.frame_index >= len(frames):
                self.frame_index = 0
                self.state = "idle"
                self.has_attacked = False

        elif self.state == "hurt":
            if self.frame_index >= len(frames):
                self.frame_index = 0
                self.state = "idle"

        elif self.state == "death":
            if pygame.time.get_ticks() - self.death_timer > 1000:
                self.kill()

        else:  # idle, walk...
            if self.frame_index >= len(frames):
                self.frame_index = 0

        # Seleciona o frame e aplica flip se necessário
        image = frames[int(self.frame_index)]
        if self.facing_right:
            image = pygame.transform.flip(image, True, False)

        self.image = image

    def draw(self, surface):
        """Desenha o frame atual na tela."""
        surface.blit(self.image, self.rect)
