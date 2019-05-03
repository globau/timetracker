# macOS Time Tracker

Automatically track hours worked; based on macOS's idle time.

## Requirements

* macOS
* Python 3.5+

## Installation

1. Clone this repo
2. Run `./tt configure`
```
$ ./tt configure
configuring python
configuring timetracker
Hours of work per week (38): 38
Auto-away idle time [minutes] (30): 30
Run timetracker on login? (n): y
updating database
installing timetracker daemon
starting timetracker daemon
done
```

## Usage

* timetracker will automatically start tracking your time
* run `tt -h` to show available commands
* run `tt` or `tt week` to show your weekly summary

```
33:33 WEEK      ⦗-04:27⦘ 29th Apr - 5th May
08:12 Monday    ⦗+00:36⦘
09:42 Tuesday   ⦗+02:06⦘
08:01 Wednesday ⦗+00:25⦘
07:38 Thursday  ⦗+00:02⦘
```

* This shows:
  * I've worked 33 hours 33 minutes so far this week.
  * I have 4 hours 27 minutes left before I hit my hours for the week.
  * On Monday I worked for 8 hours 12 minutes, which is 36 minutes over the hours for that day.

## Uninstall

1. `./tt configure` and select `n` to `Run timetracker on login?`
```
$ ./tt configure
configuring python
configuring timetracker
Hours of work per week (38): 38
Auto-away idle time [minutes] (30): 30
Run timetracker on login? (y): n
updating database
uninstalling timetracker daemon
done
timetracker daemon is not running
```
