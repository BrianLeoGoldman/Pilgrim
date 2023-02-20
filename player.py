import pygame
from settings import *


class Player(pygame.sprite.Sprite):

    def __init__(self, pos, groups):
        super().__init__(groups)
        self.image = pygame.image.load('./graphics/test/frog.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)

        self.direction = pygame.math.Vector2()  # it has position x=0 and y=0
        self.speed = 5

    def input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.direction.y = -1
        elif keys[pygame.K_DOWN]:
            self.direction.y = 1
        else:
            self.direction.y = 0

        if keys[pygame.K_RIGHT]:
            self.direction.x = 1
        elif keys[pygame.K_LEFT]:
            self.direction.x = -1
        else:
            self.direction.x = 0

    def move(self, speed):  # speed is given as a parameter via dependency injection
        # first we normalize the direction vector in case we move in two directions at once
        if self.direction.magnitude() != 0:  # magnitude is the length of the vector
            self.direction = self.direction.normalize()  # we set the length of the vector to 1
        self.rect.center += self.direction * speed

    def update(self):
        self.input()
        self.move(self.speed)
