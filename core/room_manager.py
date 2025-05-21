import pygame

class RoomManager:
    def __init__(self, screen_width, screen_height):
        self.rooms = [
            (50, 50, 50),   # Exterior do castelo
            (100, 0, 0),    # Chamber 1
            (0, 0, 100),    # Chamber 2
            (0, 100, 0)     # Boss room
        ]
        self.current_room = 0
        self.screen_width = screen_width
        self.screen_height = screen_height

    def next_room(self):
        if self.current_room < len(self.rooms) - 1:
            self.current_room += 1

    def draw_room(self, surface):
        surface.fill(self.rooms[self.current_room])

    def is_at_door(self, player):
        return player.rect.right >= self.screen_width - 50
