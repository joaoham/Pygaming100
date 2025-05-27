"""
Módulo que define o inimigo **SkeletonEnemy**.

O esqueleto patrulha, persegue Mooni a longa distância, ataca quando
chega perto, pode ser machucado (hurt) e, claro, morre quando o HP
zera.
"""

import pygame


class SkeletonEnemy(pygame.sprite.Sprite):
    """
    Inimigo Esqueleto: IA simples de perseguição + ataque corpo-a-corpo.

    Parâmetros
    ----------
    pos : tuple[int, int]
        Posição (x, y) onde o esqueleto nasce no mapa.
    """

    def __init__(self, pos):
        super().__init__()

        # sprite-sheets + nº de quadros
        self.animation_data = {
            "idle": ("assets/enemies/skeleton/Skeleton Idle.png", 11),
            "walk": ("assets/enemies/skeleton/Skeleton Walk.png", 13),
            "attack": ("assets/enemies/skeleton/Skeleton Attack.png", 18),
            "hurt": ("assets/enemies/skeleton/Skeleton Hit.png", 8),
            "death": ("assets/enemies/skeleton/Skeleton Dead.png", 15),
        }

        # carrega cada animação em um dict
        self.animations = {
            key: self.load_animation(path, frames)
            for key, (path, frames) in self.animation_data.items()
        }

        self.state = "idle"
        self.frame_index = 0
        self.animation_speed = 0.15
        self.image = self.animations[self.state][self.frame_index]

        self.rect = self.image.get_rect(topleft=pos)

        # atributos de combate/movimento
        self.speed = 4
        self.vision_range = 900
        self.health = 30
        self.damage = 5
        self.attack_cooldown = 1000
        self.last_attack_time = pygame.time.get_ticks()

        self.facing_right = False
        self.recently_hit = False
        self.attacking = False
        self.hurt = False  # ✅ flag de animação de dano

    # ------------------------------------------------------------------
    # utilitário pra cortar sprite-sheet horizontal
    # ------------------------------------------------------------------
    def load_animation(self, sheet_path, num_frames):
        """
        Retorna lista de frames (escala 2×) de um sprite-sheet horizontal.
        """
        sheet = pygame.image.load(sheet_path).convert_alpha()
        frame_width = sheet.get_width() // num_frames
        frames = [
            pygame.transform.scale(
                sheet.subsurface(i * frame_width, 0, frame_width, sheet.get_height()),
                (frame_width * 2, sheet.get_height() * 2),
            )
            for i in range(num_frames)
        ]
        return frames

    # ------------------------------------------------------------------
    # lógica principal
    # ------------------------------------------------------------------
    def update(self, player):
        """
        Decide estado (idle, walk, attack, etc.) e move o esqueleto.
        """
        if self.health <= 0:
            self.state = "death"
        elif self.hurt:
            self.state = "hurt"
        elif self.attacking:
            self.state = "attack"
        else:
            distance = player.rect.centerx - self.rect.centerx
            if abs(distance) < self.vision_range and self.health > 0:
                self.state = "walk"
                direction = 1 if distance > 0 else -1
                self.facing_right = direction > 0
                self.rect.x += direction * self.speed

                # se grudou no player → ataca
                if abs(distance) < 40:
                    now = pygame.time.get_ticks()
                    if now - self.last_attack_time > self.attack_cooldown:
                        self.attacking = True
                        self.last_attack_time = now
                        self.attack(player)
            else:
                if self.health > 0:
                    self.state = "idle"

        self.animate()

    # ------------------------------------------------------------------
    # ações
    # ------------------------------------------------------------------
    def attack(self, player):
        """Aplica dano direto no player."""
        player.take_damage(self.damage)

    def take_damage(self, amount):
        """Recebe dano e troca pra animação de hurt ou death."""
        self.health -= amount
        print(f"Skeleton took {amount} damage! Remaining health: {self.health}")
        if self.health <= 0:
            self.state = "death"
        else:
            self.hurt = True
            self.frame_index = 0  # ✅ reseta animação de hurt

    # ------------------------------------------------------------------
    # animação/frame control
    # ------------------------------------------------------------------
    def animate(self):
        """
        Avança frames da animação atual e trata resets/hurt/death.
        """
        frames = self.animations[self.state]
        self.frame_index += self.animation_speed
        if self.frame_index >= len(frames):
            self.frame_index = 0
            if self.state == "attack":
                self.attacking = False
            if self.state == "hurt":
                self.hurt = False
            if self.state == "death":
                self.kill()

        image = frames[int(self.frame_index)]
        if not self.facing_right:
            image = pygame.transform.flip(image, True, False)

        bottom = self.rect.bottom
        self.image = image
        self.rect = self.image.get_rect(midbottom=(self.rect.centerx, bottom))

    # ------------------------------------------------------------------
    def draw(self, surface):
        """Renderiza o esqueleto na tela."""
        surface.blit(self.image, self.rect)
