import argparse
import pathlib
from calendar import monthrange
from collections import namedtuple
from datetime import datetime, timezone
from itertools import accumulate

MAX_EPOCH = 253402300799 * 1000

DateTime = namedtuple(
    "DateTime",
    (
        "hour",
        "minute",
        "second",
        "microsecond",
        "day_of_month",
        "month",
        "year",
        "weekday",
        "day_of_year",
    ),
)


class UnixTime:
    # 1970 is non-leap, 1972 is leap
    # source: https://www.accuracyproject.org/leapyears.html
    DAYS_SINCE_JAN_1ST = [
        list(accumulate([0] + [monthrange(1970, i)[1] for i in range(1, 13)])),
        list(accumulate([0] + [monthrange(1972, i)[1] for i in range(1, 13)])),
    ]

    def __init__(self, epoch_millis):
        if epoch_millis > MAX_EPOCH:
            raise ValueError(f"timestamp overflow {epoch_millis}")

        self.epoch = int(epoch_millis / 1000)

    def datetime(self):
        # source: https://stackoverflow.com/a/11197532/6115820
        # re-bias from 1970 to 1601:
        # 1970 - 1601 = 369 = 3*100 + 17*4 + 1 years (incl. 89 leap days)
        # = (3*100*(365+24/100) + 17*4*(365+1/4) + 1*365)*24*3600 seconds
        second = self.epoch + 11644473600
        weekday = int((second / 86400 + 1) % 7)

        # remove multiples of 400 years (incl. 97 leap days)
        # = 400*365.2425*24*3600
        quadricentennials = int(second / 12622780800)
        second %= 12622780800

        # remove multiples of 100 years (incl. 24 leap days), can't be more
        # than 3 (because multiples of 4*100=400 years (incl. leap days)
        # have been removed)
        # = 100*(365+24/100)*24*3600
        centennials = min(3, int(second / 3155673600))
        second -= centennials * 3155673600

        # remove multiples of 4 years (incl. 1 leap day), can't be more
        # than 24 (because multiples of 25*4=100 years (incl. leap days)
        # have been removed)
        # = 4*(365+1/4)*24*3600
        quadrennials = min(24, int(second / 126230400))
        second -= quadrennials * 126230400

        # remove multiples of years (incl. 0 leap days), can't be more than 3
        # (because multiples of 4 years (incl. leap days) have been removed)
        # = 365*24*3600
        annuals = min(3, int(second / 31536000))
        second -= annuals * 31536000

        year = (
            1601
            + quadricentennials * 400
            + centennials * 100
            + quadrennials * 4
            + annuals
        )

        leap = (not (year % 4)) and (bool(year % 100) or (not (year % 400)))
        day_of_year = int(second / 86400)
        second %= 86400
        hour = int(second / 3600)
        second %= 3600
        minute = int(second / 60)
        second = second % 60
        microsecond = int(1000000 * (second % 1))

        day_of_month = 1
        for month in range(1, 13):
            if day_of_year < UnixTime.DAYS_SINCE_JAN_1ST[leap][month]:
                day_of_month += (
                    day_of_year - UnixTime.DAYS_SINCE_JAN_1ST[leap][month - 1]
                )
                break

        return DateTime(
            hour,
            minute,
            second,
            microsecond,
            day_of_month,
            month,
            year,
            weekday,
            day_of_year,
        )

    def get_human_readable(self, format="%b %-d, %Y %-I:%M:%S %p %z"):
        dt = self.datetime()
        utc_dt = datetime(
            dt.year,
            dt.month,
            dt.day_of_month,
            dt.hour,
            dt.minute,
            dt.second,
            dt.microsecond,
            timezone.utc,
        )
        local_timezone = datetime.now().astimezone().tzinfo
        return utc_dt.astimezone(local_timezone).strftime(format)


def unixtime_helper(timestamp):
    try:
        print(UnixTime(int(timestamp)).get_human_readable())
    except ValueError as ex:
        print(f"invalid epoch timestamp: {ex}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="epoch_parser",
        description="Converts Unix epoch time to human readable date"
        + " and time in local timezone",
    )

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "-ts",
        "--timestamp",
        action="store",
        type=int,
        help="Unix epoch timestamp in milliseconds",
    )

    group.add_argument(
        "-f",
        "--file",
        action="store",
        type=str,
        help="Path to file containing newline separated epoch timestamps",
        metavar="FILEPATH",
    )

    args = parser.parse_args()

    if args.file is not None:
        with pathlib.Path(args.file).open() as file:
            for timestamp in file:
                unixtime_helper(timestamp)
    elif args.timestamp is not None:
        unixtime_helper(args.timestamp)
    else:
        print("invalid argument provided")
