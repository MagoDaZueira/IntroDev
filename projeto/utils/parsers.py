from datetime import timedelta


def seconds_to_time(seconds):
    return str(timedelta(seconds=round(seconds)))