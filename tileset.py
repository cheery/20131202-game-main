import pygame

class TileSet(object):
    def __init__(self, path, width, height):
        self.path = path
        self.surface = None
        self.width   = width
        self.height  = height

    def __iter__(self):
        self.load_on_demand()
        return iter(self.tilefaces)

    def __getitem__(self, index):
        self.load_on_demand()
        return self.faces[index]

    def __len__(self):
        self.load_on_demand()
        return len(self.tilefaces)

    def load_on_demand(self):
        if self.surface is not None:
            return
        surface = self.surface = pygame.image.load(self.path)
        width, height = surface.get_size()

        cols = width / self.width
        rows = height / self.height

        self.faces = []
        for row in range(rows):
            for col in range(cols):
                rect = col*self.width, row*self.height, self.width, self.height
                self.faces.append(surface.subsurface(rect))
