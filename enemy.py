import pygame
from settings import *
from entity import Entity


class Enemy(Entity):

    def __init__(self, monster_name, position, groups):

        # general setup
        super().__init__(groups)
        self.sprite_type = 'enemy'

        # graphics setup
        self.image = pygame.Surface((64, 64))
        self.rect =