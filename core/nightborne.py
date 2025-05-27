"""
Módulo do inimigo **NightBorne**  guerreiro sombrio que corre pra cima
do player, desce a espadada e cai fora quando bate as botas.

Fluxo padrão dentro do jogo:
    nb = NightBorneEnemy((x, ground_y), "assets/enemies/nightborne.png")
    nb.update(player)
    nb.draw(screen)

"""

import pygame


class NightBorneEnemy(pygame.sprite.Sprite):
    """
    Inimigo NightBorne: corre, ataca, toma dano e morre.

    Parâmetros
    ----------
    pos : tuple[int, int]
        Posição inicial (x, y) onde o pé deve encostar no chão.
    sprite_sheet_path : str
        Caminho para o sprite-sheet que contém todas as animações.
    """

    def __init__(self, pos, sprite_sheet_path):
        super().__init__()

        self.sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
        self.frame_width = 80
        self.frame_height = 80

        # dicionário de animações (linha → nº de frames)
        self.animations = {
            "idle": self.load_animation(0, 9),
            "run": self.load_animation(1, 6),
            "attack": self.load_animation(2, 12),
            "hurt": self.load_animation(3, 5),
            "death": self.load_animation(4, 18),
        }

        self.state = "idle"
        self.frame_index = 0
        self.animation_speed = 0.2
        self.image = self.animations[self.state][int(self.frame_index)]

        # ✅ midbottom pra alinhar certinho no chão
        self.rect = self.image.get_rect(midbottom=(pos[0], pos[1]))

        self.speed = 4
        self.health = 100
        self.damage = 20
        self.attack_cooldown = 1000
        self.last_attack_time = pygame.time.get_ticks()

        self.facing_right = True
        self.recently_hit = False
        self.attacking = False
        self.hurt = False

    # ------------------------------------------------------------------
    # utilitário pra cortar as animações do sheet
    # ------------------------------------------------------------------
    def load_animation(self, row, num_frames):
        """
        Extrai `num_frames` da linha `row` do sprite-sheet.

        Retorna
        -------
        list[pygame.Surface]
            Frames redimensionados (2×) prontos pra usar.
        """
        frames = []
        for i in range(num_frames):
            frame = self.sprite_sheet.subsurface(
                pygame.Rect(
                    i * self.frame_width,
                    row * self.frame_height,
                    self.frame_width,
                    self.frame_height,
                )
            )
            # ✅ Escalona pra ficar do mesmo tamanho dos outros mobs
            frame = pygame.transform.scale(frame, (self.frame_width * 2, self.frame_height * 2))
            frames.append(frame)
        return frames

    # ------------------------------------------------------------------
    # loop de lógica
    # ------------------------------------------------------------------
    def update(self, player):
        """
        Decide estado (idle/run/attack…), move e chama animação.

        Parameters
        ----------
        player : Player
            Referência ao jogador pra calcular distância e dano.
        """
        if self.health <= 0:
            self.state = "death"
        elif self.hurt:
            self.state = "hurt"
        elif self.attacking:
            self.state = "attack"
        else:
            distance = player.rect.centerx - self.rect.centerx
            if abs(distance) < 400:
                self.state = "run"
                direction = 1 if distance > 0 else -1
                self.facing_right = direction > 0
                self.rect.x += direction * self.speed
                if abs(distance) < 50:
                    now = pygame.time.get_ticks()
                    if now - self.last_attack_time > self.attack_cooldown:
                        self.attacking = True
                        self.last_attack_time = now
                        self.attack(player)
            else:
                self.state = "idle"

        self.animate()

    # ------------------------------------------------------------------
    # ações
    # ------------------------------------------------------------------
    def attack(self, player):
        """Aplica dano direto no player."""
        player.take_damage(self.damage)

    def take_damage(self, amount):
        """Recebe dano e troca pra animação de machucado ou morte."""
        self.health -= amount
        if self.health <= 0:
            self.state = "death"
        else:
            self.hurt = True
            self.frame_index = 0

    # ------------------------------------------------------------------
    # animação e renderização
    # ------------------------------------------------------------------
    def animate(self):
        """
        Avança frames da animação atual e trata transições
        (fim de ataque, fim de hurt, morte).
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

        # ✅ mantém midbottom pra não deslizar verticalmente
        bottom = self.rect.bottom
        centerx = self.rect.centerx
        self.image = image
        self.rect = self.image.get_rect(midbottom=(centerx, bottom))

        # ✅ se quiser um hitbox menor, descomenta:
        # self.rect.inflate_ip(-20, -20)

    def draw(self, surface):
        """Desenha o frame atual na tela."""
        surface.blit(self.image, self.rect)
