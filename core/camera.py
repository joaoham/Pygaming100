import pygame

class Camera:
    def __init__(self, width, height):
        self.offset = pygame.math.Vector2(0, 0)
        self.width = width
        self.height = height

    def update(self, target):
        self.offset.x = target.rect.centerx - self.width // 2
        self.offset.y = target.rect.centery - self.height // 2
