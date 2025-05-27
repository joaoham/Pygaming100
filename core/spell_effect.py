"""
Efeito de feitiço (**SpellEffect**) disparado pelo Bringer of Death.

Funciona assim:
---------------
- Recebe lista de `spell_frames` (animação) e posição inicial.  
- Anda pelo `update()` e, se colidir com o player, aplica dano uma única vez.  
- Quando acaba a animação (ou sai da tela) o sprite se auto-destrói (`kill()`).
"""

import pygame


class SpellEffect(pygame.sprite.Sprite):
    """
    Sprite animado que representa um projétil ou feitiço.

    Parâmetros
    ----------
    pos : tuple[int, int]
        Posição inicial (center) onde o spell nasce.
    spell_frames : list[pygame.Surface]
        Frames da animação do feitiço.
    damage : int, opcional
        Dano aplicado ao player ao colidir (padrão = 10).
    """

    def __init__(self, pos, spell_frames, damage=10):
        super().__init__()
        self.frames = spell_frames
        self.frame_index = 0
        self.animation_speed = 0.2
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=pos)

        self.damage = damage
        self.has_hit = False  # ✅ garante que só causa dano 1x

        # ✅ hitbox um pouco menor pra evitar dano “fantasma”
        self.hitbox = self.rect.inflate(-20, -20)

    # ------------------------------------------------------------------
    def update(self, player):
        """
        Avança animação e aplica dano se encostar no player.
        """
        # colisão — usa hitbox reduzida
        if not self.has_hit and self.hitbox.colliderect(player.rect):
            player.take_damage(self.damage)
            self.has_hit = True

        # mantém hitbox centralizada no sprite
        self.hitbox.center = self.rect.center

        # animação
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.frames):
            self.kill()  # some quando animação termina
        else:
            self.image = self.frames[int(self.frame_index)]

    # ------------------------------------------------------------------
    def draw(self, surface):
        """Desenha o feitiço na tela."""
        surface.blit(self.image, self.rect)
