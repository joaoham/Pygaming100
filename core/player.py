"""
Módulo que define o **Player** (nosso herói Mooni).

Funções principais:
-------------------
- Recebe input do teclado pra andar, pular e atacar.  
- Gerencia física simples (gravidade e colisão com o chão).  
- Controla animações e toca efeitos de som dos golpes.  

Uso típico no jogo:
    player = Player((x_inicial, y_inicial))
    player.update(keys, ground_y, SCREEN_WIDTH)
    player.draw(screen)
"""

import pygame
import os  # ainda não usamos, mas deixo por consistência

class Player(pygame.sprite.Sprite):
    """
    Classe que representa o personagem jogável Mooni.

    Parâmetros
    ----------
    pos : tuple[int, int]
        Posição inicial (topleft) no mapa.
    """

    def __init__(self, pos):
        super().__init__()

        # sons de ataque
        self.sword_thrust_sound = pygame.mixer.Sound("assets/sounds/thrust.mp3")
        self.sword_smash_sound = pygame.mixer.Sound("assets/sounds/smash.mp3")

        # sprite-sheets + nº de frames
        self.animation_data = {
            "idle": ("assets/player/Little Mooni-Idle.png", 8),
            "run": ("assets/player/Little Mooni-Run.png", 8),
            "smash": ("assets/player/Little Mooni-Smash.png", 17),
            "thrust": ("assets/player/Little Mooni-Thrust.png", 13),
            "heal": ("assets/player/Little Mooni-Heal.png", 18),
            "death": ("assets/player/Little Mooni-Death.png", 29),
        }

        # dicionário final de animações
        self.animations = {
            key: self.load_animation(path, count)
            for key, (path, count) in self.animation_data.items()
        }

        self.state = "idle"
        self.frame_index = 0
        self.animation_speed = 0.15
        self.image = self.animations[self.state][self.frame_index]

        # ✅ usa primeira frame do idle pra setar rect
        self.rect = self.animations["idle"][0].get_rect(topleft=pos)

        # movimento / física
        self.vel = pygame.math.Vector2(0, 0)
        self.speed = 3
        self.gravity = 1.5
        self.jump_speed = -25
        self.on_ground = True
        self.facing_right = True

        # vida
        self.max_health = 125
        self.health = self.max_health
        self.alive = True

        self.ground_offset = 0  # gambi pra ajustar se precisar

        # dano dos ataques
        self.attack_damage = {"smash": 15, "thrust": 10}

    # ------------------------------------------------------------------
    def load_animation(self, sheet_path, num_frames):
        """
        Carrega `num_frames` de um sprite-sheet horizontal.

        Returns
        -------
        list[pygame.Surface]
            Frames já escalonados (2×) p/ inserir no dicionário.
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
    def input(self, keys):
        """Processa teclas WASD/ESPAÇO/Q/R pra definir estado e velocidade."""
        if keys[pygame.K_a]:
            self.vel.x = -self.speed
            self.state = "run"
            self.facing_right = False
        elif keys[pygame.K_d]:
            self.vel.x = self.speed
            self.state = "run"
            self.facing_right = True
        else:
            self.vel.x = 0
            if self.on_ground:
                self.state = "idle"

        # ataques
        if keys[pygame.K_r]:
            self.state = "smash"
            self.sword_smash_sound.play()
        if keys[pygame.K_q]:
            self.state = "thrust"
            self.sword_thrust_sound.play()

        # pulo
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel.y = self.jump_speed
            self.on_ground = False

    # ------------------------------------------------------------------
    def apply_gravity(self, ground_level):
        """Aplica gravidade e impede que Mooni atravesse o chão."""
        self.vel.y += self.gravity
        self.rect.y += self.vel.y
        if self.rect.bottom >= ground_level - self.ground_offset:
            self.rect.bottom = ground_level - self.ground_offset
            self.on_ground = True
            self.vel.y = 0

    # ------------------------------------------------------------------
    def animate(self):
        """Avança frame da animação atual (velocidade extra no smash)."""
        frames = self.animations[self.state]
        speed = self.animation_speed * 2 if self.state == "smash" else self.animation_speed
        self.frame_index += speed
        if self.frame_index >= len(frames):
            self.frame_index = 0
            if self.state in ["smash", "thrust", "heal"]:
                self.state = "idle"

        image = frames[int(self.frame_index)]
        if not self.facing_right:
            image = pygame.transform.flip(image, True, False)
        self.image = image

    # ------------------------------------------------------------------
    def take_damage(self, amount):
        """Reduz HP e muda pro estado de morte se zerar."""
        self.health -= amount
        if self.health <= 0:
            self.alive = False
            self.state = "death"

    # ------------------------------------------------------------------
    def update(self, keys, ground_level, screen_width):
        """
        Loop principal do player: movimento, física, animação e limites.

        Parameters
        ----------
        keys : pygame.key.ScancodeWrapper
            Resultado de `pygame.key.get_pressed()`.
        ground_level : int
            Y do chão pra colisão vertical.
        screen_width : int
            Limite horizontal da tela (0 à direita).
        """
        if not self.alive:
            self.state = "death"
            self.animate()
            return

        self.input(keys)
        self.animate()

        # move horizontal
        self.rect.x += self.vel.x
        self.rect.left = max(self.rect.left, 0)
        self.rect.right = min(self.rect.right, screen_width)

        # aplica gravidade
        self.apply_gravity(ground_level)

    # ------------------------------------------------------------------
    def draw(self, surface):
        """Renderiza o frame atual na tela."""
        surface.blit(self.image, self.rect)
