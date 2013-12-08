from pygame.locals import *
import frontend
from math import sin, cos, sqrt
from tileset import TileSet
from tilemap import TileMap
from random import randint
from level import Level
from actor import Actor, Player, Enemy
from mappainter import MapPainter
import pygame

level = Level(
    tileset = TileSet('graphics/level.png', 16, 16),
    tilemap = TileMap(256, 256),
    actors  = [],
)

class Rectangle(object):
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width  = width
        self.height = height

    def __iter__(self):
        return iter((self.x, self.y, self.width, self.height))

    def inside(self, (x, y)):
        inside  = (0 <= x - self.x < self.width)
        inside &= (0 <= y - self.y < self.height) 
        return inside

class TilePalette(object):
    def __init__(self, pencil, rect):
        self.pencil = pencil
        self.rect = rect
        self.palette = []
        tileset = level.tileset

        row = 10
        rect.width  = 10 + tileset.width *  (len(tileset) % row)
        rect.height = 10 + tileset.height * (len(tileset) / row + 1)
        for index, tile in enumerate(tileset):
            xi = index % row
            yi = index / row
            self.palette.append((
                Rectangle(rect.x+5+xi*tileset.width, rect.y+5+yi*tileset.height, tileset.width, tileset.height),
                index,
                tile
            ))

    def draw_to(self, screen):
        screen.fill((128, 128, 128), tuple(self.rect))
        for rect, tile, surface in self.palette:
            screen.blit(surface, tuple(rect))

    def down(self, mouse, button):
        for rect, tile, surface in self.palette:
            if rect.inside(mouse.pos):
                if button == 1:
                    self.pencil.major_tile = tile
                if button == 2:
                    self.pencil.minor_tile = tile

class Tool(object):
    def motion(self, mouse):
        pass

    def down(self, mouse, button):
        pass

    def up(self, mouse, button):
        pass

class TilePencil(Tool):
    def __init__(self):
        tileset = level.tileset
        self.rect = Rectangle(0, 0, 2*tileset.width+10, tileset.height+10)
        self.major_tile = 1
        self.minor_tile = 0
        self.menus = []

    def draw_to(self, screen):
        tileset = level.tileset
        rect = self.rect
        screen.fill((128, 128, 128), tuple(rect))
        #screen.fill((128,128,128), (0,0,tileset.width+20, tileset.height+20)) 
        screen.blit(tileset[self.major_tile], (rect.x+5, rect.y+5))
        screen.blit(tileset[self.minor_tile], (rect.x+5+tileset.width, rect.y+5))
        for menu in self.menus:
            menu.draw_to(screen)

    def pen_plot(self, mouse):
        tile = None
        if mouse.get(1):
            tile = self.major_tile
        if mouse.get(2):
            tile = self.minor_tile
        if tile is not None:
            xi, yi = level.mapview.get_xy(mouse.x, mouse.y)
            level.tilemap.set_xy(xi, yi, tile)

    def motion(self, mouse):
        self.pen_plot(mouse)

    def down(self, mouse, button):
        for menu in self.menus:
            if menu.rect.inside(mouse.pos):
                menu.down(mouse, button)
                self.menus = []
                return
        self.menus = []
        if self.rect.inside(mouse.pos):
            x, y = mouse.pos
            self.menus.append(TilePalette(self, Rectangle(x, y, 256, 256)))
        else:
            self.pen_plot(mouse)

class TileStamp(Tool):
    def __init__(self, pos, off, tilemap):
        self.pos = pos
        self.off = off
        self.tilemap = tilemap
        self.mapview = MapPainter(level.tileset, tilemap)

    def draw_to(self, screen):
        mapview = self.mapview
        tileset = mapview.tileset
        mapview.offset_x = level.mapview.offset_x + self.pos[0] * mapview.tileset.width
        mapview.offset_y = level.mapview.offset_y + self.pos[1] * mapview.tileset.height
        mapview.width  = level.mapview.width
        mapview.height = level.mapview.height
        mapview.draw_to(screen)
        wi = self.tilemap.width
        hi = self.tilemap.height
        x = mapview.offset_x
        y = mapview.offset_y
        width  = wi*tileset.width
        height = hi*tileset.height
        pygame.draw.rect(screen, (255, 255, 0), (x, y, width, height), 1)

    def motion(self, mouse):
        x = mouse.x + self.off[0]
        y = mouse.y + self.off[1]
        self.pos = level.mapview.get_xy(x, y)

    def down(self, pos, button):
        if button == 1:
            x, y = self.pos
            for xi in range(self.tilemap.width):
                for yi in range(self.tilemap.height):
                    tile = self.tilemap.get_xy(xi, yi)
                    level.tilemap.set_xy(x+xi, y+yi, tile)
        if button == 2:
            global tool
            tool = tools[1]
            tool.active = False

class GridSelection(Tool):
    def __init__(self):
        self.start = 0, 0
        self.end   = 0, 0
        self.active = False

    def draw_to(self, screen):
        mapview = level.mapview
        tileset = mapview.tileset
        if self.active:
            xi, yi, wi, hi = to_gridrect(self.start, self.end)
            x = mapview.offset_x + xi*tileset.width
            y = mapview.offset_y + yi*tileset.height
            width  = wi*tileset.width
            height = hi*tileset.height
            pygame.draw.rect(screen, (0, 255, 0), (x, y, width, height), 1)
            screen.fill((0, 255, 0), (0, 0, 10, 10))
        else:
            screen.fill((0, 0, 255), (0, 0, 10, 10))

    def expand_selection(self, mouse):
        if mouse.get(1):
            self.end = level.mapview.get_xy(mouse.x, mouse.y)

    def motion(self, mouse):
        self.expand_selection(mouse)

    def down(self, mouse, button):
        global tool
        if button == 1 and self.active:
            mapview = level.mapview
            tileset = mapview.tileset
            tilemap = mapview.tilemap
            xi, yi, wi, hi = to_gridrect(self.start, self.end)
            x = mapview.offset_x + xi*tileset.width
            y = mapview.offset_y + yi*tileset.height
            ox = x - mouse.x
            oy = y - mouse.y
            data = []
            for i in range(hi):
                for j in range(wi):
                    data.append(tilemap.get_xy(j+xi, i+yi))
            stamp = TileMap(wi, hi, data)
            tool = TileStamp((xi,yi), (ox,oy), stamp)
            self.active = False
        if button == 1:
            self.active = True
            self.end = self.start = level.mapview.get_xy(mouse.x, mouse.y)
        if button == 2:
            self.active = False

def to_gridrect(first, second):
    x0, y0 = first
    x1, y1 = second
    low_x = min(x0, x1)
    low_y = min(y0, y1)
    width  = 1 + max(x0, x1) - low_x
    height = 1 + max(y0, y1) - low_y
    return low_x, low_y, width, height

class ActorDropper(Tool):
    def __init__(self):
        pass

    def draw_to(self, screen):
        mapview = level.mapview
        tileset = mapview.tileset
        mouse = frontend.mouse
        screen.fill((255, 255, 0), (mouse.x-4, mouse.y-4, 8, 8))

    def down(self, mouse, button):
        x = mouse.x - level.mapview.offset_x
        y = mouse.y - level.mapview.offset_y
        if button == 1:
            level.actors.append(Player(level, x, y))
        if button == 2:
            level.actors.append(Enemy(level, x, y))

tools = [TilePencil(), GridSelection(), ActorDropper()]
tool = tools[0]

@frontend.hooks
def init(screen):
    width, height = screen.get_size()
    mapview = level.mapview
    mapview.width  = width
    mapview.height = height

#    mapview.offset_x = -player.x + mapview.width/2
#    mapview.offset_y = -player.y + mapview.height/2

@frontend.hooks
def animation_frame(screen, now):
    screen.fill((0,0,0))
    level.mapview.draw_to(screen)
    for actor in level.actors:
        actor.paint(screen, now)
    tool.draw_to(screen)

@frontend.hooks
def game_frame():
    pass

@frontend.hooks
def mousemotion(mouse):
    tool.motion(mouse)
    if mouse.get(3):
        level.mapview.offset_x += mouse.rx
        level.mapview.offset_y += mouse.ry

@frontend.hooks
def mousedown(mouse, button):
    tool.down(mouse, button)

@frontend.hooks
def mouseup(mouse, button):
    tool.up(mouse, button)

@frontend.hooks
def keydown(key, text):
    if key == K_ESCAPE:
        frontend.sys.exit(0)
    global tool
    if key == K_1:
        tool = tools[0]
    if key == K_2:
        tool = tools[1]
    if key == K_3:
        tool = tools[2]
    if key == K_4:
        tool = tools[3]
    if key == K_5:
        tool = tools[4]
    if key == K_6:
        tool = tools[5]

frontend.run()
