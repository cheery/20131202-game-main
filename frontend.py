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
        hooks.call('mousedown', event.pos, event.button)
    if event.type == pygame.MOUSEBUTTONUP:
        hooks.call('mouseup', event.pos, event.button)
    if event.type == pygame.MOUSEMOTION:
        hooks.call('mousemotion', event.pos)
    if event.type == pygame.KEYDOWN:
        hooks.call('keydown', event.key, event.unicode)
    if event.type == pygame.KEYUP:
        hooks.call('keyup', event.key)


#def clear(screen, color):
#    if isinstance(color, basestring):
#        color = rgba(color)
#    screen.fill(color)
#
#def rgba(string):
#    return map(ord, string.decode('hex'))
