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
                "movement": False,          # travado até waves concluírem
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

        # pré-carrega e escala todas as superfícies
        for room in self.rooms:
            if "background" in room:
                img = pygame.image.load(room["background"]).convert()
                room["bg_surface"] = pygame.transform.scale(
                    img, (screen_width, screen_height)
                )
            if "foreground" in room:
                img = pygame.image.load(room["foreground"]).convert_alpha()
                room["fg_surface"] = pygame.transform.scale(
                    img, (screen_width, screen_height)
                )

        self.door_rect = pygame.Rect(
            screen_width // 2 - 50, screen_height // 2 + 50, 100, 200
        )

    def next_room(self):
        if self.current_room < len(self.rooms) - 1:
            self.current_room += 1

    def draw_room(self, surface):
        room = self.rooms[self.current_room]
        if "bg_surface" in room:
            surface.blit(room["bg_surface"], (0, 0))
        else:
            surface.fill(room.get("color", (0, 0, 0)))

    def draw_foreground(self, surface):
        room = self.rooms[self.current_room]
        if "fg_surface" in room:
            surface.blit(room["fg_surface"], (0, 0))

    def can_move(self):
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
