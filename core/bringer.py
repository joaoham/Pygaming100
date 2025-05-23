import pygame
from core.spell_effect import SpellEffect

class BringerOfDeathEnemy(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()

        # Animações
        self.animation_data = {
            "idle": ("assets/enemies/bringer/Bringer Idle.png", 8),
            "walk": ("assets/enemies/bringer/Bringer Walk.png", 8),
            "attack": ("assets/enemies/bringer/Bringer Attack.png", 10),
            "hurt": ("assets/enemies/bringer/Bringer Hurt.png", 3),
            "death": ("assets/enemies/bringer/Bringer Death.png", 10),
            "cast": ("assets/enemies/bringer/Bringer Cast.png", 9),
            "spell": ("assets/enemies/bringer/Bringer Spell.png", 16),
        }

        self.animations = {
            key: self.load_animation(path, frames)
            for key, (path, frames) in self.animation_data.items()
        }

        self.state = "idle"
        self.frame_index = 0
        self.animation_speed = 0.15
        self.image = self.animations[self.state][self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)

        self.speed = 1
        self.health = 100
        self.damage = 15
        self.attack_cooldown = 5000  # ms
        self.last_attack_time = pygame.time.get_ticks()

        self.facing_right = True

    def load_animation(self, sheet_path, num_frames):
        sheet = pygame.image.load(sheet_path).convert_alpha()
        sheet_width, sheet_height = sheet.get_size()
        frame_width = sheet_width // num_frames
        frames = []

        for i in range(num_frames):
            frame = sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, sheet_height))
            frames.append(pygame.transform.scale(frame, (frame.get_width() * 2, frame.get_height() * 2)))
        return frames

    def update(self, player):
        # Distância para aproximação
        distance = player.rect.centerx - self.rect.centerx

        if abs(distance) < 200 and self.health > 0:
            self.state = "walk"
            direction = 1 if distance > 0 else -1
            self.facing_right = direction > 0
            self.rect.x += direction * self.speed

            # Se muito perto, ataque melee
            if abs(distance) < 50:
                now = pygame.time.get_ticks()
                if now - self.last_attack_time > self.attack_cooldown:
                    self.state = "attack"
                    self.attack(player)
                    self.last_attack_time = now
            # Se longe, faz spell
            elif abs(distance) < 200:
                now = pygame.time.get_ticks()
                if now - self.last_attack_time > self.attack_cooldown:
                    self.state = "cast"
                    self.cast_spell(player)
                    self.last_attack_time = now
        else:
            self.state = "idle"

        self.animate()

    def attack(self, player):
        player.take_damage(self.damage)

    def cast_spell(self, player, spell_group):
    # Cria um spell na posição atual do player
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
