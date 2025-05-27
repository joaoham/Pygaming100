import pygame
import random

class KnightBoss(pygame.sprite.Sprite):
    def __init__(self, pos, ground_y):
        super().__init__()
        self.SCALE = 2
        self.frame_width  = 128
        self.frame_height = 64
        self.animations   = {}

        self.animation_data = {
            "idle":   ("assets/enemies/knight/Idle.png",   8, 2),
            "run":    ("assets/enemies/knight/Run.png",    8, 2),
            "death":  ("assets/enemies/knight/Death.png",  4, 2),
            "hurt":   ("assets/enemies/knight/Hurt.png",   3, 2),
            "jump":   ("assets/enemies/knight/Jump.png",   8, 2),
            "pray":   ("assets/enemies/knight/Pray.png",  12, 4),
            "roll":   ("assets/enemies/knight/Roll.png",   4, 2),
            "slide":  ("assets/enemies/knight/Slide.png", 10, 4),
            "crouch_idle":    ("assets/enemies/knight/crouch_idle.png",    8, 2),
            "crouch_attacks": ("assets/enemies/knight/crouch_attacks.png", 7, 2),
            "attack_from_air":("assets/enemies/knight/attack_from_air.png",7, 2),
        }

        for state, (path, n, cols) in self.animation_data.items():
            sheet = pygame.image.load(path).convert_alpha()
            self.animations[state] = self.load_from_sheet_grid(sheet, n, cols)

        # dois ataques corpo-a-corpo no mesmo sprite-sheet
        attack_sheet = pygame.image.load("assets/enemies/knight/Attacks.png").convert_alpha()
        for i in range(2):
            key = f"attack_{i+1}"
            self.animations[key] = self.load_from_sheet_grid(attack_sheet, 8, 8, row=i)

        self.attack_data = {
            "attack_1": {"hitbox": pygame.Rect(0, 0, 100, 60), "damage": 20},
            "attack_2": {"hitbox": pygame.Rect(0, 0, 100, 60), "damage": 25},
        }

        # -------- estado inicial --------
        self.state = "pray"
        self.passive = True
        self.dialogue_done = False
        self.animation_index = 0
        self.image = self.animations[self.state][self.animation_index]

        self.rect = self.animations["pray"][3].get_rect(topleft=pos)
        self.rect.y = 362                   # ajuste manual
        self.rect.bottom = ground_y

        self.hp = 200                       # vida total
        self.speed = 2
        self.attack_range = 100
        self.last_attack_time = 0
        self.attack_cooldown = 2000

        self.current_hitbox = None
        self.has_hit_player = False
        self.facing_right = False

        # ---------- NOVO: invulnerabilidade curta ----------
        self.hit_cooldown = 300             # ms sem levar dano de novo
        self.last_hit_time = 0

    # -------------------------------------------------------

    def load_from_sheet_grid(self, sheet, num_frames, cols, row=0):
        frames = []
        for i in range(num_frames):
            col = i % cols
            r   = row + (i // cols)
            x, y = col*self.frame_width, r*self.frame_height
            frame = sheet.subsurface((x, y, self.frame_width, self.frame_height))
            frame = pygame.transform.scale(
                frame, (self.frame_width*self.SCALE, self.frame_height*self.SCALE))
            frames.append(frame)
        return frames

    def update(self, player, dt):
        if self.state != "death" and not self.passive:
            self.move_towards_player(player)
            self.try_attack(player)
        self.animate()
        self.update_hitbox_position()

    def animate(self):
        if self.passive:
            self.state = "pray"
            self.animation_index = 3
            self.image = self.animations[self.state][self.animation_index]
            return

        self.animation_index += 0.15
        if self.state == "death":
            if self.animation_index >= len(self.animations[self.state]):
                self.animation_index = len(self.animations[self.state]) - 1
        else:
            if self.animation_index >= len(self.animations[self.state]):
                self.animation_index = 0
                if self.state in list(self.attack_data.keys()) + ["hurt"]:
                    self.state = "idle"
                    self.has_hit_player = False

        self.image = self.animations[self.state][int(self.animation_index)]

    def move_towards_player(self, player):
        if self.state in list(self.attack_data.keys()) + ["hurt", "death"]:
            return
        if abs(player.rect.centerx - self.rect.centerx) > self.attack_range:
            if player.rect.centerx > self.rect.centerx:
                self.rect.x += self.speed
                self.facing_right = True
            else:
                self.rect.x -= self.speed
                self.facing_right = False
            self.state = "run"
        else:
            self.state = "idle"

    def try_attack(self, player):
        now = pygame.time.get_ticks()
        if abs(self.rect.centerx - player.rect.centerx) < self.attack_range:
            if now - self.last_attack_time > self.attack_cooldown:
                atk = random.choice(list(self.attack_data.keys()))
                self.state = atk
                self.current_hitbox = self.attack_data[atk]["hitbox"].copy()
                self.has_hit_player = False
                self.last_attack_time = now

    def update_hitbox_position(self):
        if self.current_hitbox and self.state in self.attack_data:
            if self.facing_right:
                self.current_hitbox.topleft = (
                    self.rect.centerx + 30,
                    self.rect.centery - self.current_hitbox.height//2 + 20)
            else:
                self.current_hitbox.topleft = (
                    self.rect.centerx - self.current_hitbox.width - 30,
                    self.rect.centery - self.current_hitbox.height//2 + 20)
        else:
            self.current_hitbox = None

    def check_attack_collision(self, player):
        if self.state in self.attack_data and self.current_hitbox:
            if self.current_hitbox.colliderect(player.rect) and not self.has_hit_player:
                player.take_damage(self.attack_data[self.state]["damage"])
                self.has_hit_player = True

    # -------------- AJUSTE AQUI -----------------
    def take_damage(self, amount):
        if self.state == "death":
            return
        now = pygame.time.get_ticks()
        if now - self.last_hit_time < self.hit_cooldown:
            return               # ainda na janela de invulnerabilidade
        self.last_hit_time = now

        self.hp -= amount
        self.state = "hurt"
        if self.hp <= 0:
            self.state = "death"
    # -------------------------------------------

    def draw(self, surface):
        img = pygame.transform.flip(self.image, True, False) if not self.facing_right else self.image
        surface.blit(img, self.rect.topleft)
        # DEBUG: hitbox em vermelho
        if self.current_hitbox:
            pygame.draw.rect(surface, (255, 0, 0), self.current_hitbox, 2)
