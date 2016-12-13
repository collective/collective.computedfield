import calendar
import datetime
import json
import time

import pytz

try:
    import persistent
    from persistent.mapping import PersistentMapping
    HAS_ZODB = True
except ImportError:
    HAS_ZODB = False
try:
    from Aqcuisition import aq_base
    HAS_AQ = True
except ImportError:
    HAS_AQ = False


# Get __dict__ for object, if it has one, or empty dict:
_dict = lambda v: v.__dict__ if hasattr(v, '__dict__') else {}
# is object a PersistentMapping instance?
is_pmap = lambda v: HAS_ZODB and isinstance(v, PersistentMapping)
# is object a BTree
is_btree = lambda v: 'BTree' in v.__class__.__name__


def days_since_epoch(value):
    if not isinstance(value, datetime.datetime):
        dt = datetime.datetime(
            value.year,
            value.month,
            value.day,
            tzinfo=pytz.UTC,
            )
    else:
        dt = value
    if dt.tzinfo is None:
        # treat naive as UTC by reconstructing as much:
        dt = datetime.datetime(
            value.year,
            value.month,
            value.day,
            value.hour,
            value.minute,
            value.second,
            value.microsecond,
            tzinfo=pytz.UTC,
            )
    return calendar.timegm(dt.utctimetuple()) / 86400.0


def parse_datestamp(value):
    y = int(value[0:4])
    m = int(value[5:7])
    d = int(value[8:10])
    return datetime.datetime(y, m, d, tzinfo=pytz.UTC)


def normalize_value(value):
    """
    Normalize non-float value to floating-point.  Supports:

        * int -> float
        * Strings that look like numbers
        * ISO 8601 date stamps (not time components)
        * datetime.date objects
        * datetime.datetime (naive as UTC, or pytz.UTC) objects
    """
    if isinstance(value, int):
        value = float(value)
    if isinstance(value, basestring):
        try:
            # is it string that looks like a number?
            value = float(value)
        except ValueError:
            # if it looks like a datestamp, parse it:
            if len(value) == 10 and value.find('-') == 4:
                value = parse_datestamp(value)
    if any(
        [isinstance(value, cls) for cls in (datetime.date, datetime.datetime)]
            ):
        value = days_since_epoch(value)
    return value


def normalize_data(context):
    """Return a dict of context data; does not normalize values"""
    if isinstance(context, basestring):
        context = json.loads(context)
    if isinstance(context, dict):
        return context
    if HAS_ZODB and isinstance(context, persistent.Persistent):
        data = aq_base(context) if HAS_AQ else context
        if is_pmap(data) or is_btree(data):
            return dict(data)
        # unghost, if necessary to get __dict__ on object:
        v = getattr(data, 'BOGUS_ATTR_NAME', None)  # noqa
    else:
        data = context
    return _dict(data)  # attrs as mapping

