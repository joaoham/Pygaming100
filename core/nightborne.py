import pygame
import os

class NightBorneEnemy(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()

        self.speed = 7
        self.health = 150
        self.damage = 20
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = pygame.time.get_ticks()
        self.facing_right = True

        # ✅ Carrega a spritesheet
        self.sheet = pygame.image.load('assets/enemies/nightborne/NightBorne.png').convert_alpha()

        self.sheet_width, self.sheet_height = self.sheet.get_size()
        self.frame_width = self.sheet_width // 32
        self.frame_height = self.sheet_height // 5

        # ✅ Animações: linha, num_frames
        self.animation_data = {
            "idle": (0, 9),
            "run": (1, 6),
            "attack": (2, 12),
            "hurt": (3, 5),
            "death": (4, 23),
        }

        self.animations = {
            key: self.load_animation_from_spritesheet(row, frames)
            for key, (row, frames) in self.animation_data.items()
        }

        self.state = "idle"
        self.frame_index = 0
        self.animation_speed = 0.15
        self.image = self.animations[self.state][int(self.frame_index)]
        self.rect = self.image.get_rect(topleft=pos)

    def load_animation_from_spritesheet(self, row, num_frames):
        frames = []
        for i in range(num_frames):
            x = i * self.frame_width
            y = row * self.frame_height
            frame = self.sheet.subsurface(pygame.Rect(x, y, self.frame_width, self.frame_height))
            frame = pygame.transform.scale(frame, (self.frame_width * 2, self.frame_height * 2))
            frames.append(frame)
        return frames

    def update(self, player):
        distance = player.rect.centerx - self.rect.centerx

        if abs(distance) < 300 and self.health > 0:
            self.state = "run"
            direction = 1 if distance > 0 else -1
            self.facing_right = direction > 0
            self.rect.x += direction * self.speed

            if abs(distance) < 50:
                now = pygame.time.get_ticks()
                if now - self.last_attack_time > self.attack_cooldown:
                    self.state = "attack"
                    self.attack(player)
                    self.last_attack_time = now
        else:
            self.state = "idle"

        self.animate()

    def attack(self, player):
        player.take_damage(self.damage)

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
            if self.state in ["attack", "hurt"]:
                self.state = "idle"
            if self.state == "death":
                self.kill()

        image = frames[int(self.frame_index)]
        if not self.facing_right:
            image = pygame.transform.flip(image, True, False)
        self.image = image

    def draw(self, surface):
        surface.blit(self.image, self.rect)
