#!/usr/bin/env python3

from gtatime import GTATime #all others should be modeled after this one
from time import time as now
import json
import subprocess
import random

def getTruth(wanted_time):
	return GTATime(wanted_time).__dict__

def getPHP(wanted_time):
	return json.loads( subprocess.check_output(["php", "./gtatime.php", str(wanted_time)]) )

def getJS(wanted_time):
	return json.loads( subprocess.check_output(["nodejs", "./gtatime.js", str(wanted_time)]) )

edge_cases = [0,46080,92160] #should equal the same
def checkEdgeCases(func, name="?"):
	results = []
	for x in edge_cases:
		current = func(x)
		del current["unix_time"] #will be the only changes in serialisation
		results.append(current)

	compare_to = str(results[0])
	for x in results[1:]:
		if str(x) != compare_to:
			print(f"{name} has failed")
			print(f"{x} != {compare_to}")
			return False
	return True


unix_time = now()

print("Edge Cases:")
if checkEdgeCases(getTruth, "Python GTATime"):
	print("- Truth passed")
if checkEdgeCases(getPHP, "PHP GTATime"):
	print("- PHP passed")
if checkEdgeCases(getJS, "JS GTATime"):
	print("- JS passed")

print("Comparing output:")
for _ in range(5):
	random_time = random.randint(0, 0x7fffffff)
	truth = getTruth(random_time)
	php = getPHP(random_time)
	js = getJS(random_time)
	if str(php) != str(truth):
		print("- PHP Failed")
		print("PHP:", php)
		print("TRUTH:", truth)
	else:
		print("- PHP Passed")

	if str(js) != str(truth):
		print("- JS Failed")
		print("JS:", js)
		print("TRUTH:", truth)
	else:
		print("- JS Passed")
