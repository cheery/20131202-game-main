import pygame
from math import sin, cos, sqrt
from random import randint
import sprite

class ActorDescriptor(object):
    def __init__(self, name, spritesheet, (state, frame, speed), **attributes):
        self.name = name
        self.spritesheet = spritesheet
        self.anim_args = (state, frame, speed)
        self.attributes = attributes
        self.game_frame = lambda actor: None

    def __call__(self, level, x, y, **attributes):
        return Actor(level, self, x, y, attributes)

    def behavior(self, game_frame):
        self.game_frame = game_frame
        return game_frame

class Actor(object):
    def __init__(self, level, desc, x, y, attributes):
        self.level = level
        self.desc  = desc
        self.x = x
        self.y = y
        self.attributes = attributes
        self.anim = sprite.Animation(desc.spritesheet, *desc.anim_args)
        self.anim.speed = 0
        b_x, b_y, self.width, self.height = desc.spritesheet[0]

    def game_frame(self):
        return self.desc.game_frame(self)

    def move(self, x, y):
        bad_y = self.level.map_collision(self, (self.x,y))
        bad_x = self.level.map_collision(self, (x,self.y))
        bad_xy = self.level.map_collision(self, (x,y))
        if not bad_xy:
            self.x = x
            self.y = y
            return False
        elif not bad_y:
            self.y = y
        elif not bad_x:
            self.x = x
        return True

#class Actor(object):
#    img = pygame.image.load('graphics/actor.png')
#    anim = None
#    def __init__(self, level, x, y):
#        self.level = level
#        self.x = x
#        self.y = y
#        self.control_x = 0
#        self.control_y = 0
#        self.width  = 8
#        self.height = 8
#        self.hit_wall = False
#        self.is_moving = False
#        self.direction = 0
#
#    def game_frame(self):
#        if self.control_x > 0:
#            self.direction = 1
#        elif self.control_x < 0:
#            self.direction = 3
#        elif self.control_y > 0:
#            self.direction = 0
#        elif self.control_y < 0:
#            self.direction = 2
#        self.game_logic()
#        x = self.x + self.control_x
#        y = self.y + self.control_y
#        self.is_moving = (self.x != x) or (self.y != y)
#        self.hit_wall  = self.motion(self.x + self.control_x, self.y + self.control_y)
#        if self.hit_wall:
#            self.is_moving = False
#
    def paint(self, screen, now):
        bx = self.x + self.level.mapview.offset_x
        by = self.y + self.level.mapview.offset_y
        return self.anim.paint(screen, now, bx, by)
#        rect = bx-4, by-18+4, 8, 18 
#        if self.anim is None:
#            return screen.blit(self.img, rect)
#
#        speed = sqrt(self.control_x**2+self.control_y**2)
#        rate = 8.0/60
#        if speed > 0:
#            rate /= speed
#        direction = self.direction
#        frame = int(now/rate) % 3 if self.is_moving else 0
#        pick = direction*8, frame*18, 8, 18
#        screen.blit(self.anim.subsurface(pick), rect)
##
##    if actor.statusimg and int(now/0.05) % 2 == 0:
##        screen.blit(actor.statusimg, (bx-4, by-18+4-8, 8, 18))
#
#class Player(Actor):
#    anim = pygame.image.load('graphics/player.png')
#    run = False
#    axis_x = 0
#    axis_y = 0
#    stamina = 100
#    def game_logic(self):
#        stamina = self.stamina
#        if self.axis_x == 0 and self.axis_y == 0:
#            if stamina < 100:
#                stamina += 0.1
#        else:
#            if self.run and stamina > 0:
#                stamina -= 4
#        self.stamina = stamina
#        self.control_x = self.axis_x * (1, 10)[self.run and stamina > 0]
#        self.control_y = self.axis_y * (1, 10)[self.run and stamina > 0]
#
#class Enemy(Actor):
#    anim = pygame.image.load('graphics/enemy.png')
#    change_direction = 0
#    def game_logic(self):
#        if self.change_direction <= 0 or self.hit_wall:
#            self.control_x = randint(-1, 1)
#            self.control_y = randint(-1, 1)
#            self.change_direction = randint(10, 80)
#        else:
#            self.change_direction -= 1
