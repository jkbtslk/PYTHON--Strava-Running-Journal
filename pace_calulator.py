#!/usr/bin/python
def calculator(distance, total_time):
    total_seconds = (int(total_time))
    seconds_per_km = float(total_seconds) / (float(distance)/1000)

    minutes_per_km = int(seconds_per_km / 60)
    seconds_remainder = int(seconds_per_km - (minutes_per_km * 60))
    return '{}:{:0=2d} min/km'.format(minutes_per_km, seconds_remainder)