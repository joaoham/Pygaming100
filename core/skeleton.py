import pygame

class SkeletonEnemy(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.animation_data = {
            "idle": ("assets/enemies/skeleton/Skeleton Idle.png", 11),
            "walk": ("assets/enemies/skeleton/Skeleton Walk.png", 13),
            "attack": ("assets/enemies/skeleton/Skeleton Attack.png", 18),
            "hurt": ("assets/enemies/skeleton/Skeleton Hit.png", 8),
            "death": ("assets/enemies/skeleton/Skeleton Dead.png", 15),
        }
        self.animations = {key: self.load_animation(path, frames) for key, (path, frames) in self.animation_data.items()}
        self.state = "idle"
        self.frame_index = 0
        self.animation_speed = 0.15
        self.image = self.animations[self.state][self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)
        self.speed = 2
        self.health = 30
        self.damage = 5
        self.attack_cooldown = 1000
        self.last_attack_time = pygame.time.get_ticks()
        self.facing_right = False

    def load_animation(self, sheet_path, num_frames):
        sheet = pygame.image.load(sheet_path).convert_alpha()
        frame_width = sheet.get_width() // num_frames
        frames = [pygame.transform.scale(sheet.subsurface(i * frame_width, 0, frame_width, sheet.get_height()), 
                    (frame_width * 2, sheet.get_height() * 2)) for i in range(num_frames)]
        return frames

    def update(self, player):
        distance = player.rect.centerx - self.rect.centerx
        if abs(distance) < 300 and self.health > 0:
            self.state = "walk"
            direction = 1 if distance > 0 else -1
            self.facing_right = direction > 0
            self.rect.x += direction * self.speed
            if abs(distance) < 40:
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
        self.state = "death" if self.health <= 0 else "hurt"

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
