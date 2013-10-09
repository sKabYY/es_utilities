from datetime import datetime, timedelta, tzinfo
import calendar


class UTC(tzinfo):
    '''
    UTC Time
    '''
    def utcoffset(self, dt):
        return timedelta(0)

    def dst(self, dt):
        return timedelta(0)

    def tzname(self, dt):
        return 'UTC'


class GMT7(tzinfo):
    '''
    GMT+7, Mountain Time Zone.
    '''
    UTC_OFFSET = timedelta(hours=-7)

    def utcoffset(self, dt):
        return self.UTC_OFFSET + self.dst(dt)

    def dst(self, dt):
        return timedelta(0)

    def tzname(self, dt):
        return 'GMT+7'


class GMTn8(tzinfo):
    '''
    GMT-8, Beijing/Shanghai Time Zone
    '''
    UTC_OFFSET = timedelta(hours=8)

    def utcoffset(self, dt):
        return self.UTC_OFFSET + self.dst(dt)

    def dst(self, dt):
        return timedelta(0)

    def tzname(self, dt):
        return 'GMT-8'


def get_now(tz=UTC()):
    return datetime.now(tz)


def get_current_day(dt):
    return datetime(year=dt.year, month=dt.month, day=dt.day,
                    tzinfo=dt.tzinfo)


def get_today(tz=UTC()):
    now = get_now(tz)
    return get_current_day(now)


def to_utc(dt):
    return dt.astimezone(UTC())


def from_utc(dt, tz):
    return dt.astimezone(tz)


def dt_to_ts(dt):
    '''
    Get timestamp from datetime. The unit of timestamp is second.
    '''
    utc_dt = to_utc(dt)
    return calendar.timegm(utc_dt.timetuple())


def ts_to_dt(ts, tz=UTC()):
    '''
    Get datetime from timestamp. The unit of timestamp is second.
    Need a tzinfo for the returned datetime. The default tzinfo is UTC.
    '''
    return datetime.fromtimestamp(ts, tz)
