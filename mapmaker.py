#!/usr/bin/env python3
"""Usage: ./mapmaker.py > mapdata.js"""
import dataset
import json

table = dataset.connect("sqlite:///clink.db")['addresses']
markers = []
center = [0, 0]
for address in table:
    markers.append(dict(address))
    center[0] = (address.get('lat') + center[0])/2
    center[1] = (address.get('lon') + center[1])/2
print("var mapdata = %s" % json.dumps({"center": center, "markers": markers}))
