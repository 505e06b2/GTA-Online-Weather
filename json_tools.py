#!/usr/bin/env python3

# Fill in gaps between start points
import re

x = {}

with open("raw_table.txt") as f:
	for [key, value] in re.findall(r"\[(\d+?),\s+weatherState.(\w+)\],?", f.read()):
		x[key] = value


WEATHER_NAME = [
	"clear",
    "rain",
    "drizzle",
    "mist",
    "fog",
    "haze",
    "cloudy",
    "mostlyCloudy",
    "partlyCloudy",
    "mostlyClear"
]

out = []

items = list(x.items())
for i in range(len(items)):
	current = items[i]
	try:
		next = items[i+1]
	except:
		next = (384, "None")
	until = int(next[0])
	while len(out) < until:
		out.append(WEATHER_NAME.index(current[1]))

print(out)
