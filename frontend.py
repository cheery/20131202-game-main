import pygame, time, sys

class EventHooks(object):
    def __init__(self):
        self.table = {}

    def __call__(self, fn):
        self.table[fn.__name__] = fn
        return fn

    def call(self, name, *args, **kw):
        if name in self.table:
            return self.table[name](*args, **kw)

hooks = EventHooks()

def run():
    tickrate = 1.0 / 30
    pygame.display.init()
    screen = pygame.display.set_mode((640, 480))
    hooks.call('init', screen)
    last = time.time() - tickrate
    while 1:
        for event in pygame.event.get():
            dispatch(event)

        now = time.time()
        hooks.call('animation_frame', screen, now)
        pygame.display.flip()
        if last + tickrate <= now:
            hooks.call('game_frame')
            last = now

def dispatch(event):
    if event.type == pygame.QUIT:
        sys.exit(0)
    if event.type == pygame.MOUSEBUTTONDOWN:
        mouse.x, mouse.y = event.pos
        mouse.buttons[event.button] = True
        hooks.call('mousedown', mouse, event.button)
    if event.type == pygame.MOUSEBUTTONUP:
        mouse.x, mouse.y = event.pos
        mouse.buttons[event.button] = False
        hooks.call('mouseup', mouse, event.button)
    if event.type == pygame.MOUSEMOTION:
        mouse.x, mouse.y = event.pos
        mouse.rx, mouse.ry = event.rel
        hooks.call('mousemotion', mouse)
    if event.type == pygame.KEYDOWN:
        hooks.call('keydown', event.key, event.unicode)
    if event.type == pygame.KEYUP:
        hooks.call('keyup', event.key)

class Mouse(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rx = 0
        self.ry = 0
        self.buttons = {}

    @property
    def pos(self):
        return (self.x, self.y)

    def get(self, button):
        return self.buttons.get(button, False)

mouse = Mouse(0, 0)

#def clear(screen, color):
#    if isinstance(color, basestring):
#        color = rgba(color)
#    screen.fill(color)
#
#def rgba(string):
#    return map(ord, string.decode('hex'))
