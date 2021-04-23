<?php
//would use shebang for cli, but will interfere with web use

$unix_time = time();

//commandline arg passed
if(isset($argv[1])) {
	$val = intval($argv[1]);
	if($val) $unix_time = $val;
	else if($val == 0 && $argv[1] == "0") $unix_time = 0;
}

//web get arg passed
if(isset($_GET["unix_time"])) {
	$val = intval($_GET["unix_time"]);
	if($val) $unix_time = $val;
	else if($val == 0 && $_GET["unix_time"] == "0") $unix_time = 0;
}

$GLOBALS["ingame_hr_len"] = 120;

$GLOBALS["weather_name"] = [
	"Clear",
    "Rainy",
    "Drizzling",
    "Misty",
    "Foggy",
    "Hazy",
    "Cloudy",
    "Mostly Cloudy",
    "Partly Cloudy",
    "Mostly Clear"
];

$GLOBALS["weather_periods"] = json_decode(file_get_contents("weather_periods.json"));

class TimeSlice {
	function __construct($timeslice) {
        $this->duration = intval($timeslice["duration"] * $GLOBALS["ingame_hr_len"]);
		$this->left = intval($timeslice["left"] * $GLOBALS["ingame_hr_len"])+1;
    }
}

class Weather {
	function __construct($time) {
		$this->period = intval(fmod($time["total_hrs"], count($GLOBALS["weather_periods"])));
		$this->name = $GLOBALS["weather_name"][ $GLOBALS["weather_periods"][$this->period] ];

		$current_period = $GLOBALS["weather_periods"][$this->period];

		$end_period = $this->period;
		while($GLOBALS["weather_periods"][$end_period] == $current_period) {
			$end_period++;
			if($end_period >= count($GLOBALS["weather_periods"])) $end_period = 0;
		}

		$start_period = $this->period;
		while($GLOBALS["weather_periods"][$start_period] == $current_period) {
			$start_period--;
			if($start_period < 0) $start_period = count($GLOBALS["weather_periods"]) -1;
		}
		$start_period++;

		$gta_timeslice = [];

		$gta_timeslice["duration"] = $end_period - $start_period;
		if($gta_timeslice["duration"] < 0) $gta_timeslice["duration"] = count($GLOBALS["weather_periods"]) + $gta_timeslice["duration"];

		$past_the_hour = $time["current_hr"] - intval($time["current_hr"]);
		$gta_timeslice["left"] = $end_period - $this->period - $past_the_hour;
		if($gta_timeslice["left"] < 0) $gta_timeslice["left"] = count($GLOBALS["weather_periods"]) + $gta_timeslice["left"];

		$this->timeslice = new TimeSlice($gta_timeslice);
	}
}

class GTATime {
	function __construct($wanted_time) {
		$this->unix_time = $wanted_time;

		$time = [];
		$time["total_hrs"] = $this->unix_time / $GLOBALS["ingame_hr_len"];
		$time["current_hr"] = fmod($time["total_hrs"], 24.0);

		$this->weather = new Weather($time);

		$this->day = intval($this->weather->period / count($GLOBALS["weather_periods"]) * 16) + 1;
		$this->hour = intval($time["current_hr"]);
		$this->minute = intval(($time["current_hr"] - $this->hour) * 60.0);
	}
}

echo json_encode(get_object_vars(new GTATime($unix_time))) . "\n";
?>
