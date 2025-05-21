import pygame

class RoomManager:
    def __init__(self, screen_width, screen_height):
        self.rooms = [
            {"background": "assets/background/tela1.png", "movement": True},
            {"color": (100, 0, 0), "movement": True},
            {"color": (0, 0, 100), "movement": True},
            {"color": (0, 100, 0), "movement": True}
        ]
        self.current_room = 0
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Porta na base do castelo (ajuste se necessário)
        self.door_rect = pygame.Rect(screen_width // 2 - 50, screen_height // 2 + 50, 100, 200)

    def next_room(self):
        if self.current_room < len(self.rooms) - 1:
            self.current_room += 1

    def draw_room(self, surface):
        if self.current_room == 0:
            bg = pygame.image.load(self.rooms[0]["background"]).convert()
            bg = pygame.transform.scale(bg, (self.screen_width, self.screen_height))
            surface.blit(bg, (0, 0))
            # Porta já está na imagem, não precisa desenhar
        else:
            surface.fill(self.rooms[self.current_room]["color"])

    def can_move(self):
        return self.rooms[self.current_room]["movement"]

    def player_at_door(self, player):
        return self.door_rect.colliderect(player.rect)
