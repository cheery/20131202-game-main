from pygame.locals import *
import frontend
from math import sin, cos, sqrt
from tileset import TileSet
from tilemap import TileMap
from mappainter import MapPainter
from random import randint
import pygame

def is_wall(tile):
    return tile != 0

class Level(object):
    def __init__(self, tileset, tilemap):
        self.tileset = tileset
        self.tilemap = tilemap
        self.mapview = MapPainter(tileset, tilemap)

    def get_xy(self, x, y):
        return self.tilemap.get_xy(x / self.tileset.width, y / self.tileset.height)

    def hit_wall_test(self, x, y):
        return is_wall(self.get_xy(x, y))

    def map_collision(self, obj, (x,y)):
        half_width  = obj.width  / 2
        half_height = obj.height / 2
        lo_x, hi_x = x - half_width,  x + half_width  - 1
        lo_y, hi_y = y - half_height, y + half_height - 1
        resp  = self.hit_wall_test(lo_x, lo_y)
        resp |= self.hit_wall_test(hi_x, lo_y)
        resp |= self.hit_wall_test(hi_x, hi_y)
        resp |= self.hit_wall_test(lo_x, hi_y)
        return resp

class Actor(object):
    img = pygame.image.load('graphics/actor.png')
    anim = None
    def __init__(self, level, x, y):
        self.level = level
        self.x = x
        self.y = y
        self.control_x = 0
        self.control_y = 0
        self.width  = 8
        self.height = 8
        self.hit_wall = False
        self.is_moving = False
        self.direction = 0

    def game_frame(self):
        if self.control_x > 0:
            self.direction = 1
        elif self.control_x < 0:
            self.direction = 3
        elif self.control_y > 0:
            self.direction = 0
        elif self.control_y < 0:
            self.direction = 2
        self.game_logic()
        x = self.x + self.control_x
        y = self.y + self.control_y
        self.is_moving = (self.x != x) or (self.y != y)
        self.hit_wall  = self.motion(self.x + self.control_x, self.y + self.control_y)
        if self.hit_wall:
            self.is_moving = False

    def motion(self, x, y):
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

    def paint(self, screen, now):
        bx = self.x + self.level.mapview.offset_x
        by = self.y + self.level.mapview.offset_y
        rect = bx-4, by-18+4, 8, 18 
        if self.anim is None:
            return screen.blit(self.img, rect)

        speed = sqrt(self.control_x**2+self.control_y**2)
        rate = 8.0/60
        if speed > 0:
            rate /= speed
        direction = self.direction
        frame = int(now/rate) % 3 if self.is_moving else 0
        pick = direction*8, frame*18, 8, 18
        screen.blit(self.anim.subsurface(pick), rect)
#
#    if actor.statusimg and int(now/0.05) % 2 == 0:
#        screen.blit(actor.statusimg, (bx-4, by-18+4-8, 8, 18))


class Player(Actor):
    anim = pygame.image.load('graphics/player.png')
    run = False
    axis_x = 0
    axis_y = 0
    stamina = 100
    def game_logic(self):
        stamina = self.stamina
        if self.axis_x == 0 and self.axis_y == 0:
            if stamina < 100:
                stamina += 0.1
        else:
            if self.run and stamina > 0:
                stamina -= 4
        self.stamina = stamina
        self.control_x = self.axis_x * (1, 10)[self.run and stamina > 0]
        self.control_y = self.axis_y * (1, 10)[self.run and stamina > 0]

class Enemy(Actor):
    anim = pygame.image.load('graphics/enemy.png')
    change_direction = 0
    def game_logic(self):
        if self.change_direction <= 0 or self.hit_wall:
            self.control_x = randint(-1, 1)
            self.control_y = randint(-1, 1)
            self.change_direction = randint(10, 80)
        else:
            self.change_direction -= 1
        

level = Level(
    tileset = TileSet('graphics/level.png', 16, 16),
    tilemap = TileMap(256, 256),
)

player = Player(level, 10, 10)

actors = [player]
for i in range(200):
    x = randint(4, level.tilemap.width*16 - 4)
    y = randint(4, level.tilemap.height*16 - 4)
    actors.append( Enemy(level, x,y) )

@frontend.hooks
def init(screen):
    width, height = screen.get_size()
    mapview = level.mapview
    mapview.width  = width
    mapview.height = height

    mapview.offset_x = -player.x + mapview.width/2
    mapview.offset_y = -player.y + mapview.height/2

def spring_scroll():
    mapview = level.mapview
    t = 0.9
    x  = mapview.offset_x * t
    y  = mapview.offset_y * t
    x += (1-t)*(-player.x + mapview.width/2 )
    y += (1-t)*(-player.y + mapview.height/2)
    mapview.offset_x = x
    mapview.offset_y = y

@frontend.hooks
def animation_frame(screen, now):
    screen.fill((0,0,0))
    spring_scroll()
    level.mapview.draw_to(screen)
    for enemy in actors:
        enemy.paint(screen, now)

    stamina = 10, 10, player.stamina+1, 10 
    screen.fill((255, 255, 128), stamina)

@frontend.hooks
def game_frame():
    for enemy in actors:
        enemy.game_frame()

@frontend.hooks
def mousemotion((x, y)):
    xi, yi = level.mapview.get_xy(x, y)
    level.tilemap.set_xy(xi, yi, 1)

@frontend.hooks
def mousedown(pos, button):
    print 'mousedown', pos, button

@frontend.hooks
def keydown(key, text):
    if key == K_ESCAPE:
        frontend.sys.exit(0)
    if key in (K_RSHIFT, K_LSHIFT):
        player.run = True
    if key == K_UP:
        player.axis_y = -1
    if key == K_DOWN:
        player.axis_y = +1
    if key == K_LEFT:
        player.axis_x = -1
    if key == K_RIGHT:
        player.axis_x = +1
    print 'keydown', key, repr(text)

@frontend.hooks
def keyup(key):
    if key in (K_RSHIFT, K_LSHIFT):
        player.run = False
    if key == K_UP:
        player.axis_y = -0
    if key == K_DOWN:
        player.axis_y = +0
    if key == K_LEFT:
        player.axis_x = -0
    if key == K_RIGHT:
        player.axis_x = +0
    

frontend.run()
