#!/usr/bin/env nodejs

const INGAME_HR_LEN = 120;

let WEATHER_NAME = [];
let WEEKDAY_NAME = [];
let WEATHER_PERIODS = [];

if(typeof(process) != "undefined") {
	WEATHER_NAME = require("./weather_names.json");
	WEEKDAY_NAME = require("./weekday_names.json");
	WEATHER_PERIODS = require("./weather_periods.json");
} else {
	window.initGTATime = async () => {
		WEATHER_NAME = await (await fetch("./weather_names.json")).json();
		WEEKDAY_NAME = await (await fetch("./weekday_names.json")).json();
		WEATHER_PERIODS = await (await fetch("./weather_periods.json")).json();
	}
}

class TimeSlice {
	constructor(timeslice) {
		this.duration = parseInt(timeslice["duration"] * INGAME_HR_LEN);
		this.left = parseInt(timeslice["left"] * INGAME_HR_LEN)+1;
	}
}

class Weather {
	constructor(time) {
		this.period = parseInt(time["total_hrs"] % WEATHER_PERIODS.length);
		this.id = WEATHER_PERIODS[this.period]
		this.name = WEATHER_NAME[this.id];

		const current_period = WEATHER_PERIODS[this.period];

		let end_period = this.period;
		while(WEATHER_PERIODS[end_period] == current_period) {
			end_period++;
			if(end_period >= WEATHER_PERIODS.length) end_period = 0;
		}

		let start_period = this.period;
		while(WEATHER_PERIODS[start_period] == current_period) {
			start_period--;
			if(start_period < 0) start_period = WEATHER_PERIODS.length-1;
		}
		start_period++;

		const gta_timeslice = {};

		gta_timeslice["duration"] = end_period - start_period;
		if(gta_timeslice["duration"] < 0) gta_timeslice["duration"] = WEATHER_PERIODS.length + gta_timeslice["duration"];

		const past_the_hour = time["current_hr"] - parseInt(time["current_hr"]);
		gta_timeslice["left"] = end_period - this.period - past_the_hour;
		if(gta_timeslice["left"] < 0) gta_timeslice["left"] = WEATHER_PERIODS.length + gta_timeslice["left"];

		this.timeslice = new TimeSlice(gta_timeslice);
	}
}

class GTATime {
	constructor(wanted_time) {
		if(typeof(wanted_time) == "undefined") wanted_time = (new Date()).getTime() / 1000;
		this.unix_time = wanted_time;

		const time = {};
		time["total_hrs"] = this.unix_time / INGAME_HR_LEN;
		time["current_hr"] = time["total_hrs"] % 24.0;
		time["current_day"] = parseInt(time["total_hrs"] / 24)+1

		this.weather = new Weather(time);

		this.weekday = WEEKDAY_NAME[time["current_day"] % WEEKDAY_NAME.length];
		this.day = parseInt(this.weather.period / WEATHER_PERIODS.length * 16) + 1;
		this.hour = parseInt(time["current_hr"]);
		this.minute = parseInt((time["current_hr"] - this.hour) * 60.0);
	}
}

//NodeJS
if(typeof(process) != "undefined") {
	unix_time = undefined;

	if(process.argv.length > 2) {
		const val = parseInt(process.argv[2]);
		if(!isNaN(val)) unix_time = val;
	}

	console.log(JSON.stringify(new GTATime(unix_time)));
}
