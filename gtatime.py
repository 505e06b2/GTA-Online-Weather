#!/usr/bin/env python3

from time import time as now #naming my variable time seemed like a good idea lol
import json
import sys

INGAME_HR_LEN = 120 #1 in-game hour in seconds

WEATHER_PERIODS = json.load(open("weather_periods.json")) #this was generated with the data from gtaweather.js
#considered parity with https://wiki.gtanet.work/index.php?title=Weather, but didn't seem useful
WEATHER_NAME = json.load(open("weather_names.json"))

WEEKDAY_NAME = json.load(open("weekday_names.json"))

#This class is for turning GTA hrs (as a float) to irl seconds - the weather only changes on the hour, so it doesn't seem as useful to return the GTA hrs
class TimeSlice:
	def __init__(self, timeslice):
		self.duration = int(timeslice["duration"] * INGAME_HR_LEN)
		self.left = int(timeslice["left"] * INGAME_HR_LEN)+1 #could keep as float if needed, but are < s useful?
		#self.passed = int(timeslice["duration"] - timeslice["left"]) #can be easily calculated by the user

	def __repr__(self): #serialisation
		return str(self.__dict__)

#This class will get the current weather, while optionally (just delete the rest) getting the duration / time left
class Weather:
	def __init__(self, time):
		self.period = int(time["total_hrs"] % len(WEATHER_PERIODS)) #1 period is 1hr in game
		self.id = WEATHER_PERIODS[self.period]
		self.name = WEATHER_NAME[self.id]

		#if you don't need timeslice info, just remove the rest of this
		current_period = WEATHER_PERIODS[self.period]

		end_period = self.period
		while(WEATHER_PERIODS[end_period] == current_period):
			end_period = (end_period + 1) % len(WEATHER_PERIODS)
		#exclusive

		start_period = self.period
		while(WEATHER_PERIODS[start_period] == current_period):
			start_period = (start_period - 1) % len(WEATHER_PERIODS)
		start_period += 1 #inclusive

		gta_timeslice = {}
		gta_timeslice["duration"] = (end_period - start_period) % len(WEATHER_PERIODS)
		past_the_hour = time["current_hr"] - int(time["current_hr"])
		gta_timeslice["left"] = (end_period - self.period - past_the_hour) % len(WEATHER_PERIODS) #need modulo, for wrapping round properly
		self.timeslice = TimeSlice(gta_timeslice) #save this as irl seconds

	def __repr__(self): #serialisation
		return str(self.__dict__)

#This class will convert a UNIX timestamp (in seconds), to GTA hrs as a float, passing this to the weather class for info
class GTATime:
	def __init__(self, wanted_time=None): #time as unix epoch in s (float)
		if wanted_time == None: #could just do this as default param, but not portable to other languages
			wanted_time = now()
		self.unix_time = wanted_time

		time = {} #protected vars - no initialiser, since current_hr depends on total_hrs - Weather needs these to work, and modulo is an expensive op
		time["total_hrs"] = self.unix_time / INGAME_HR_LEN
		time["current_hr"] = time["total_hrs"] % 24.0 #modulo returns float (fmod)
		time["current_day"] = int(time["total_hrs"] / 24)+1

		self.weather = Weather(time)

		self.weekday = WEEKDAY_NAME[time["current_day"] % len(WEEKDAY_NAME)]
		self.day = int(self.weather.period / len(WEATHER_PERIODS) * 16) + 1 #+1 to make it 1-indexed
		self.hour = int(time["current_hr"])
		self.minute = int((time["current_hr"] - self.hour) * 60.0) #remove whole number with -self.hours, *60 for hrs to mins

	def __repr__(self): #serialisation
		return str(self.__dict__)



if __name__ == "__main__":
	import time
	def printCentredLine(l): print(l.center(30))
	def secondsToMMSS(s): return time.strftime("[%M:%S]", time.gmtime(s))

	current_gtatime = GTATime()
	print(current_gtatime)
	print("")
	printCentredLine(f"[ {current_gtatime.hour:02} : {current_gtatime.minute:02} ]")
	printCentredLine("_Weather_")
	print(f"1. {secondsToMMSS(current_gtatime.weather.timeslice.left)} {current_gtatime.weather.name}")
	for i in range(2, 5):
		current_gtatime = GTATime(current_gtatime.unix_time + current_gtatime.weather.timeslice.left)
		print(f"{i}. {secondsToMMSS(current_gtatime.weather.timeslice.left)} {current_gtatime.weather.name}")
	print("")
