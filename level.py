import pygame

class Level:
    def __init__(self):

        # Sprite group setup
        self.visible_sprites = pygame.sprite.Group()
        self.obstacle_sprites = pygame.sprite.Group()

    def run(self):
        # Update and draw the game
        pass