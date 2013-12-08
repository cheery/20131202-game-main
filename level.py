from mappainter import MapPainter

def is_wall(tile):
    return tile != 0

class Level(object):
    def __init__(self, tileset, tilemap, actors):
        self.tileset = tileset
        self.tilemap = tilemap
        self.actors  = actors
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
