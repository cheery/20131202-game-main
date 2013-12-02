import struct

class TileMap(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.data = [0 for i in range(width*height)]

    def save(self, path):
        fd = open(path, 'w')
        for tile in self.data:
            fd.write( struct.pack('B', tile) )
        fd.close()

    def load(self, path):
        fd = open(path, 'r')
        for index in range(len(self)):
            tile = struct.unpack('B', fd.read(1))[0]
            self[index] = tile

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.data[index]

    def __setitem__(self, index, value):
        self.data[index] = value

    def get_xy(self, x, y):
        if not (0 <= x < self.width and 0 <= y < self.height):
            return -2
        index = self.width * y + x
        return self[index]

    def set_xy(self, x, y, tile):
        if 0 <= x < self.width and 0 <= y < self.height:
            index = self.width * y + x
            self[index] = tile
