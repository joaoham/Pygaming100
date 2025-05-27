import pygame
import os

class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()

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
        self.animation_speed = 0.30
        self.image = self.animations[self.state][self.frame_index]

        # ✅ Ajustado: usa explicitamente a primeira frame do idle para setar o rect.
        self.rect = self.animations["idle"][0].get_rect(topleft=pos)

        self.vel = pygame.math.Vector2(0, 0)
        self.speed = 3
        self.gravity = 2.5
        self.jump_speed = -25
        self.on_ground = True
        self.facing_right = True

        self.max_health = 100
        self.health = self.max_health
        self.alive = True

        self.ground_offset = 0

        self.attack_damage = {
            "smash": 15,
            "thrust": 10
        }

    def load_animation(self, sheet_path, num_frames):
        sheet = pygame.image.load(sheet_path).convert_alpha()
        frame_width = sheet.get_width() // num_frames
        frames = [pygame.transform.scale(sheet.subsurface(i * frame_width, 0, frame_width, sheet.get_height()), 
                    (frame_width * 2, sheet.get_height() * 2)) for i in range(num_frames)]
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

    def apply_gravity(self, ground_level):
        self.vel.y += self.gravity
        self.rect.y += self.vel.y
        if self.rect.bottom >= ground_level - self.ground_offset:
            self.rect.bottom = ground_level - self.ground_offset
            self.on_ground = True
            self.vel.y = 0

    def animate(self):
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

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.alive = False
            self.state = "death"

    def update(self, keys, ground_level, screen_width):
        if not self.alive:
            self.state = "death"
            self.animate()
            return
        self.input(keys)
        self.animate()
        self.rect.x += self.vel.x
        self.rect.left = max(self.rect.left, 0)
        self.rect.right = min(self.rect.right, screen_width)
        self.apply_gravity(ground_level)

    def draw(self, surface):
        surface.blit(self.image, self.rect)
