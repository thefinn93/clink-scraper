#!/usr/bin/env python3
"""Usage: ./mapmaker.py > mapdata.js"""
import dataset
import json

table = dataset.connect("sqlite:///clink.db")['addresses']
markers = []
center = [0, 0]
for address in table:
    markers.append(dict(address))
    if len(markers) == 0:
        center[0] = float(address.get('lat'))
        center[1] = float(address.get('lon'))
    center[0] = (float(address.get('lat')) + center[0])/2
    center[1] = (float(address.get('lon')) + center[1])/2
print("var mapdata = %s" % json.dumps({"center": center, "markers": markers}))
