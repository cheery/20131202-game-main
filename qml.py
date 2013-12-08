import re

header = re.compile(r"^import QtQuick 1.1\n\nRectangle {\n *width: (\d*)\n *height: (\d*)\n(.*)}$", re.DOTALL)
image = re.compile(r"Image {(.*?)}", re.DOTALL)
key_value_pair = re.compile(r"^ *(\w+): (.*)$", re.MULTILINE)

def parse_file(path):
    with open(path) as fd:
        match = header.match(fd.read())
        if match is not None:
            width, height, layers = match.groups()
            return width, height, list(parse_layers(layers))

def parse_layers(layers):
    for layer in image.findall(layers):
        out = {}
        for key, value in key_value_pair.findall(layer):
            if value.isdigit() or value.startswith('-'):
                out[key] = int(value)
            else:
                out[key] = value.strip('"')
        yield out
