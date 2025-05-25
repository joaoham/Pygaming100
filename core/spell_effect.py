import pygame

class SpellEffect(pygame.sprite.Sprite):
    def __init__(self, pos, spell_frames, damage=10):
        super().__init__()
        self.frames = spell_frames
        self.frame_index = 0
        self.animation_speed = 0.2
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=pos)
        
        self.damage = damage
        self.has_hit = False  # ✅ Controle se já causou dano

        # ✅ Ajuste: hitbox menor para evitar dano "invisível"
        self.hitbox = self.rect.inflate(-20, -20)  # Ajusta conforme necessário

    def update(self, player):
        # ✅ Colisão com hitbox ajustada
        if not self.has_hit and self.hitbox.colliderect(player.rect):
            player.take_damage(self.damage)
            self.has_hit = True  # ✅ Evita dano repetido

        # ✅ Mantém a hitbox acompanhando a posição
        self.hitbox.center = self.rect.center

        # Animação
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.frames):
            self.kill()
        else:
            self.image = self.frames[int(self.frame_index)]

    def draw(self, surface):
        surface.blit(self.image, self.rect)
