class MapPainter(object):
    def __init__(self, tileset, tilemap):
        self.tileset = tileset
        self.tilemap = tilemap
        self.offset_x = 0
        self.offset_y = 0
        self.width  = 320
        self.height = 240

    def draw_to(self, screen):
        tileset = self.tileset
        tilemap = self.tilemap
        offset_x = int(self.offset_x)
        offset_y = int(self.offset_y)
        i_x = offset_x/tileset.width
        i_y = offset_y/tileset.height
        j_x = offset_x%tileset.width
        j_y = offset_y%tileset.height
        width, height = screen.get_size()
        for x in range(-1, self.width / tileset.width):
            for y in range(-1, self.height / tileset.height):
                tile = tilemap.get_xy(x-i_x, y-i_y)
                if tile < 0:
                    continue
                screen.blit(tileset[tile], (x*tileset.width+j_x, y*tileset.height+j_y))

    def get_xy(self, x, y):
        xi = int((x-self.offset_x) / self.tileset.width)
        yi = int((y-self.offset_y) / self.tileset.height)
        return xi, yi
