import pygame
import os
from core.spell_effect import SpellEffect

class BringerOfDeathEnemy(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()

        self.speed = 1
        self.health = 100
        self.damage = 15
        self.attack_cooldown = 5000  # ms
        self.last_attack_time = pygame.time.get_ticks()
        self.facing_right = True

        # ✅ Carregar todas as animações a partir das pastas!
        base_path = "assets/enemies/bringer"

        self.animations = {
            "idle": self.load_animation_from_folder(os.path.join(base_path, "Idle")),
            "walk": self.load_animation_from_folder(os.path.join(base_path, "Walk")),
            "attack": self.load_animation_from_folder(os.path.join(base_path, "Attack")),
            "hurt": self.load_animation_from_folder(os.path.join(base_path, "Hurt")),
            "death": self.load_animation_from_folder(os.path.join(base_path, "Death")),
            "cast": self.load_animation_from_folder(os.path.join(base_path, "Cast")),
            "spell": self.load_animation_from_folder(os.path.join(base_path, "Spell"))
        }

        self.state = "idle"
        self.frame_index = 0
        self.animation_speed = 0.15
        self.image = self.animations[self.state][int(self.frame_index)]
        self.rect = self.image.get_rect(topleft=pos)

    # ✅ Função para carregar todos os frames de uma pasta
    def load_animation_from_folder(self, folder_path):
        frames = []
        for filename in sorted(os.listdir(folder_path)):
            if filename.endswith('.png'):
                image = pygame.image.load(os.path.join(folder_path, filename)).convert_alpha()
                image = pygame.transform.scale(image, (image.get_width() * 2, image.get_height() * 2))
                frames.append(image)
        return frames

    def update(self, player, spell_group):
        distance = player.rect.centerx - self.rect.centerx

        if abs(distance) < 200 and self.health > 0:
            self.state = "walk"
            direction = 1 if distance > 0 else -1
            self.facing_right = direction > 0
            self.rect.x += direction * self.speed

            now = pygame.time.get_ticks()

            if abs(distance) < 50:
                if now - self.last_attack_time > self.attack_cooldown:
                    self.state = "attack"
                    self.attack(player)
                    self.last_attack_time = now
            elif abs(distance) < 200:
                if now - self.last_attack_time > self.attack_cooldown:
                    self.state = "cast"
                    self.cast_spell(player, spell_group)
                    self.last_attack_time = now
        else:
            self.state = "idle"

        self.animate()

    def attack(self, player):
        player.take_damage(self.damage)

    def cast_spell(self, player, spell_group):
        spell = SpellEffect(player.rect.center, self.animations["spell"])
        spell_group.add(spell)
        print("Bringer lançou feitiço no player!")

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.state = "death"
        else:
            self.state = "hurt"

    def animate(self):
        frames = self.animations[self.state]
        self.frame_index += self.animation_speed
        if self.frame_index >= len(frames):
            self.frame_index = 0
            if self.state in ["attack", "hurt", "cast"]:
                self.state = "idle"
            if self.state == "death":
                self.kill()

        image = frames[int(self.frame_index)]
        if not self.facing_right:
            image = pygame.transform.flip(image, True, False)
        self.image = image

    def draw(self, surface):
        surface.blit(self.image, self.rect)
