import pygame

class RoomManager:
    def __init__(self, screen_width, screen_height):
        self.rooms = [
            {
                "background": "assets/background/tela1.png",
                "movement": True,
                "ground_level": 690
            },
            {
                "background": "assets/background/background_passarela.png",
                "foreground": "assets/background/frente_passarela.png",
                "movement": False,  # ✅ Inicialmente travado
                "waves_completed": False,
                "ground_level": 750
            },
            {
                "background": "assets/background/boss_arena.png",
                "movement": True,
                "ground_level": 650
            }
        ]
        self.current_room = 0
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.door_rect = pygame.Rect(screen_width // 2 - 50, screen_height // 2 + 50, 100, 200)

    def next_room(self):
        if self.current_room < len(self.rooms) - 1:
            self.current_room += 1

    def draw_room(self, surface):
        room = self.rooms[self.current_room]
        if "background" in room:
            bg = pygame.image.load(room["background"]).convert()
            bg = pygame.transform.scale(bg, (self.screen_width, self.screen_height))
            surface.blit(bg, (0, 0))
        else:
            surface.fill(room["color"])

    def draw_foreground(self, surface):
        room = self.rooms[self.current_room]
        if "foreground" in room:
            fg = pygame.image.load(room["foreground"]).convert_alpha()
            fg = pygame.transform.scale(fg, (self.screen_width, self.screen_height))
            surface.blit(fg, (0, 0))

    def can_move(self):
        # ✅ Bloqueia movimento se ondas não completadas na passarela
        if self.current_room == 1 and not self.rooms[1]["waves_completed"]:
            return False
        return self.rooms[self.current_room]["movement"]

    def player_at_door(self, player):
        return self.door_rect.colliderect(player.rect)

    def get_ground_level(self):
        return self.rooms[self.current_room].get("ground_level", 690)

    def complete_waves(self):
        if self.current_room == 1:
            self.rooms[1]["waves_completed"] = True
            self.rooms[1]["movement"] = True
