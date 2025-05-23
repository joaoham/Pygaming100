import pygame

class NightBorneEnemy(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()

        self.animation_data = {
            "idle": ("assets/enemies/nightborne/NightBorne_Idle.png", 9),
            "run": ("assets/enemies/nightborne/NightBorne_Run.png", 6),
            "attack": ("assets/enemies/nightborne/NightBorne_Attack.png", 12),
            "hurt": ("assets/enemies/nightborne/NightBorne_Hurt.png", 5),
            "death": ("assets/enemies/nightborne/NightBorne_Death.png", 23),
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

        self.speed = 7  # Mais rápido que o player
        self.health = 150
        self.damage = 20
        self.attack_cooldown = 1000  # ms
        self.last_attack_time = pygame.time.get_ticks()

        self.facing_right = True

    def load_animation(self, sheet_path, num_frames):
        sheet = pygame.image.load(sheet_path).convert_alpha()
        sheet_width, sheet_height = sheet.get_size()
        frame_width = sheet_width // num_frames
        frames = []

        for i in range(num_frames):
            frame = sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, sheet_height))
            frames.append(pygame.transform.scale(frame, (80, 80)))  # Tamanho fixo
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
