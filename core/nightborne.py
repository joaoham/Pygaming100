import pygame

class NightBorneEnemy(pygame.sprite.Sprite):
    def __init__(self, pos, sprite_sheet_path):
        super().__init__()

        self.sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
        self.frame_width = 80
        self.frame_height = 80

        self.animations = {
            "idle": self.load_animation(0, 9),
            "run": self.load_animation(1, 6),
            "attack": self.load_animation(2, 12),
            "hurt": self.load_animation(3, 5),
            "death": self.load_animation(4, 18)
        }

        self.state = "idle"
        self.frame_index = 0
        self.animation_speed = 0.15
        self.image = self.animations[self.state][int(self.frame_index)]

        # ✅ midbottom para alinhar corretamente com o chão
        self.rect = self.image.get_rect(midbottom=(pos[0], pos[1]))

        self.speed = 7
        self.health = 50
        self.damage = 20
        self.attack_cooldown = 1000
        self.last_attack_time = pygame.time.get_ticks()

        self.facing_right = True
        self.recently_hit = False
        self.attacking = False
        self.hurt = False

    def load_animation(self, row, num_frames):
        frames = []
        for i in range(num_frames):
            frame = self.sprite_sheet.subsurface(pygame.Rect(
                i * self.frame_width, 
                row * self.frame_height, 
                self.frame_width, 
                self.frame_height
            ))
            # ✅ Mantém a escala original OU ajusta aqui
            frame = pygame.transform.scale(frame, (self.frame_width * 2, self.frame_height * 2))
            frames.append(frame)
        return frames

    def update(self, player):
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

    def attack(self, player):
        player.take_damage(self.damage)

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.state = "death"
        else:
            self.hurt = True
            self.frame_index = 0

    def animate(self):
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

        # ✅ MANTÉM midbottom, não deixa mexer a posição
        bottom = self.rect.bottom
        centerx = self.rect.centerx
        self.image = image
        self.rect = self.image.get_rect(midbottom=(centerx, bottom))

        # ✅ (OPCIONAL) Encolhe a hitbox para não pegar de longe
        # self.rect.inflate_ip(-20, -20)

    def draw(self, surface):
        surface.blit(self.image, self.rect)
