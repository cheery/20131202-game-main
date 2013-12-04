from pygame.locals import *
import frontend
from math import sin, cos, sqrt
from tileset import TileSet
from tilemap import TileMap
from random import randint
from level import Level
from actor import Actor, Player, Enemy

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
def mousemotion(mouse):
    xi, yi = level.mapview.get_xy(mouse.x, mouse.y)
    level.tilemap.set_xy(xi, yi, 1)

@frontend.hooks
def mousedown(mouse, button):
    print 'mousedown', mouse, button

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
