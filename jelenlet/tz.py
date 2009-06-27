from datetime import datetime, tzinfo, timedelta

class CEST(tzinfo):
    """CET timezone with DST"""
    def utcoffset(self, dt):
        return timedelta(hours=1) + self.dst(dt)
    def dst(self, dt):
        return timedelta(hours=1)
    def tzname(self, dt):
        return "CEST"

class UTC(tzinfo):
    """UTC timezone"""
    def utcoffset(self, dt):
        return timedelta(0)

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return timedelta(0)
class EREP(tzinfo):
    """eRepublik timezone"""
    def utcoffset(self, dt):
        return - timedelta(hours=7)
    def dst(self, dt):
        return timedelta(0)
    def tzname(self, dt):
        return "EREP"

cest = CEST()
utc = UTC()
erep = EREP()
erepstart = datetime(2007, 11, 20)
