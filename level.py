import pygame

from enemy import Enemy
from magic import MagicPlayer
from particles import AnimationPlayer
from settings import *
from support import *
from tile import Tile
from player import Player
from debug import debug
from random import choice, randint

from ui import UI
from weapon import Weapon


class Level:
    def __init__(self):
        # get the display surface from anywhere in the code
        self.display_surface = pygame.display.get_surface()

        # sprite group setup
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()

        # attack sprites
        self.current_attack = None
        self.attack_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()

        # sprite setup
        self.create_map()

        # user interface
        self.ui = UI()

        # particles
        self.animation_player = AnimationPlayer()  # this will run a particle effect
        self.magic_player = MagicPlayer(self.animation_player)

    def create_map(self):
        layouts = {
            'boundary': import_csv_layout('./map/map_FloorBlocks.csv'),
            'grass': import_csv_layout('./map/map_Grass.csv'),
            'object': import_csv_layout('./map/map_Objects.csv'),
            'entities': import_csv_layout('./map/map_Entities.csv')
        }
        graphics = {
            'grass': import_folder('./graphics/Grass'),
            'objects': import_folder('./graphics/objects')
        }
        for style, layout in layouts.items():
            for row_index, row in enumerate(layout):
                for col_index, col in enumerate(row):
                    if col != '-1':
                        x = col_index * TILESIZE
                        y = row_index * TILESIZE
                        if style == 'boundary':
                            Tile((x, y), [self.obstacle_sprites], 'invisible')
                        if style == 'grass':
                            #  create a grass tile
                            random_grass_image = choice(graphics['grass'])
                            Tile(
                                (x, y),
                                [self.visible_sprites, self.obstacle_sprites, self.attackable_sprites],
                                'grass',
                                random_grass_image)
                            # TODO: remove self.obstacle_sprites so the grass does not have collision
                        if style == 'object':
                            #  create an object tile
                            surf = graphics['objects'][int(col)]
                            Tile((x, y), [self.visible_sprites, self.obstacle_sprites], 'object', surf)
                        if style == 'entities':
                            # this works for enemies and the player
                            if col == '394':  # this is the player
                                self.player = Player(
                                    (x, y),
                                    [self.visible_sprites],
                                    self.obstacle_sprites,
                                    self.create_attack,
                                    self.destroy_attack,
                                    self.create_magic)
                            else:
                                # TODO create function to determine enemy based on code
                                if col == '390':
                                    monster_name = 'bamboo'
                                elif col == '391':
                                    monster_name = 'spirit'
                                elif col == '392':
                                    monster_name = 'raccoon'
                                else:
                                    monster_name = 'squid'
                                Enemy(
                                    monster_name,
                                    (x, y),
                                    [self.visible_sprites, self.attackable_sprites],
                                    self.obstacle_sprites, self.damage_player,
                                    self.trigger_death_particles)

    def create_attack(self):
        self.current_attack = Weapon(self.player, [self.visible_sprites, self.attack_sprites])

    def create_magic(self, style, strength, cost):
        if style == 'heal':
            self.magic_player.heal(self.player, strength, cost, [self.visible_sprites])
        if style == 'flame':
            pass

    def destroy_attack(self):
        if self.current_attack:
            self.current_attack.kill()
        self.current_attack = None

    def player_attack_logic(self):
        if self.attack_sprites:
            for attack_sprite in self.attack_sprites:
                collision_sprites = pygame.sprite.spritecollide(attack_sprite, self.attackable_sprites, False)
                if collision_sprites:
                    for target_sprite in collision_sprites:
                        if target_sprite.sprite_type == 'grass':
                            pos = target_sprite.rect.center
                            offset = pygame.math.Vector2(0, 70)
                            for leaf in range(randint(3, 6)):
                                self.animation_player.create_grass_particles(pos - offset, [self.visible_sprites])
                            target_sprite.kill()
                        else:
                            target_sprite.get_damage(self.player, attack_sprite.sprite_type)

    def damage_player(self, amount, attack_type):  # This method is in level and not in enemy because of the particle effects
        if self.player.vulnerable:
            self.player.health -= amount
            self.player.vulnerable = False
            self.player.hurt_time = pygame.time.get_ticks()
            self.animation_player.create_particles(attack_type, self.player.rect.center, [self.visible_sprites])

    def trigger_death_particles(self, pos, particle_type):
        self.animation_player.create_particles(particle_type, pos, [self.visible_sprites])


    def run(self):
        # update and draw the game
        self.visible_sprites.custom_draw(self.player)
        self.visible_sprites.update()
        self.visible_sprites.enemy_update(self.player)
        # debug(self.player.direction)
        # debug(self.player.status)
        self.player_attack_logic()
        self.ui.display(self.player)


class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):

        # general setup
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2  # half of the screen width
        self.half_height = self.display_surface.get_size()[1] // 2  # half of the screen height
        self.offset = pygame.math.Vector2()  # starts as (0,0)

        # creating the floor
        self.floor_surf = pygame.image.load('./graphics/tilemaps/ground.png').convert()  # image of the floor
        self.floor_rect = self.floor_surf.get_rect(topleft=(0, 0))  # floor rectangle

    def custom_draw(self, player):

        # getting the offset
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        # drawing the floor
        floor_offset_pos = self.floor_rect.topleft - self.offset
        self.display_surface.blit(self.floor_surf, floor_offset_pos)

        # for sprite in self.sprites():
        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            offset_position = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_position)

    def enemy_update(self, player):
        enemy_sprites = [sprite for sprite in self.sprites() if
                         hasattr(sprite, 'sprite_type') and sprite.sprite_type == 'enemy']
        for enemy in enemy_sprites:
            enemy.enemy_update(player)  # TODO: couldn't we call update instead? (passing player as argument)
