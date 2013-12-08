import qml
import os
import pygame

def load(path):
    width, height, data = qml.parse_file(path)
    base_x = 0
    base_y = 0
    base_width  = 0
    base_height = 0
    frames = {}
    for layer in data:
        print layer
        layer_id = layer['id']
        if layer_id == 'collider':
            base_x = layer['x']
            base_y = layer['y']
            base_width  = layer['width']
            base_height = layer['height']
        else:
            name, num = layer_id.split('_', 1)
            duration = 1000
            if '_' in num:
                num, duration = num.split('_', 1)
                duration = int(duration)
            x = layer['x'] - base_x
            y = layer['y'] - base_x
            width  = layer['width']
            height = layer['height']
            source = os.path.join(os.path.dirname(path), layer['source'])
            frame = pygame.image.load(source)
            duration = duration / 1000.0
            record = (duration, x, y, frame)
            if name in frames:
                frames[name].append(record)
            else:
                frames[name] = [record]
    return (base_x, base_y, base_width, base_height), frames

class Animation(object):
    def __init__(self, sprite, state, frame=0, speed=1.0):
        self.sprite = sprite
        self.state  = state
        self.frame  = frame
        self.tick   = sprite[1][state][frame][0]
        self.last   = None
        self.speed  = speed

    def paint(self, screen, now, x, y):
        frames = self.sprite[1][self.state]
        if self.last is None:
            self.last = now
        else:
            dt = (now - self.last) * self.speed
            while self.tick < dt:
                dt -= self.tick
                self.frame = (self.frame+1)%len(frames)
                self.tick = frames[self.frame][0]
            self.tick -= dt
            self.last = now
        self.frame = self.frame%len(frames)
        current = frames[self.frame]
        x += current[1]
        y += current[2]
        screen.blit(current[3], (x, y))
