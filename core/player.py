import pygame
import os

class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()

        # Dicionário de animações com número de frames por sheet
        self.animation_data = {
            "idle": ("assets/player/Little Mooni-Idle.png", 8),
            "run": ("assets/player/Little Mooni-Run.png", 8),
            "smash": ("assets/player/Little Mooni-Smash.png", 17),
            "thrust": ("assets/player/Little Mooni-Thrust.png", 13),
            "heal": ("assets/player/Little Mooni-Heal.png", 18),
            "death": ("assets/player/Little Mooni-Death.png", 29),
        }

        self.animations = {
            key: self.load_animation(path, count)
            for key, (path, count) in self.animation_data.items()
        }

        self.state = "idle"
        self.frame_index = 0
        self.animation_speed = 0.15
        self.image = self.animations[self.state][self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)
        self.vel = pygame.math.Vector2(0, 0)
        self.speed = 5
        self.gravity = 1
        self.jump_speed = -15
        self.on_ground = True
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

    def input(self, keys):
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

        if keys[pygame.K_r]:
            self.state = "smash"
        if keys[pygame.K_q]:
            self.state = "thrust"
        if keys[pygame.K_f]:
            self.state = "heal"
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel.y = self.jump_speed
            self.on_ground = False

    def apply_gravity(self):
        self.vel.y += self.gravity
        self.rect.y += self.vel.y
        if self.rect.bottom >= 500:
            self.rect.bottom = 500
            self.on_ground = True
            self.vel.y = 0

    def animate(self):
        frames = self.animations[self.state]
        self.frame_index += self.animation_speed
        if self.frame_index >= len(frames):
            self.frame_index = 0
            if self.state in ["smash", "thrust", "heal"]:
                self.state = "idle"

        image = frames[int(self.frame_index)]
        if not self.facing_right:
            image = pygame.transform.flip(image, True, False)
        self.image = image

    def update(self, keys):
        self.input(keys)
        self.animate()
        self.rect.x += self.vel.x
        self.apply_gravity()

    def draw(self, surface):
        surface.blit(self.image, self.rect)