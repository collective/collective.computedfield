
sum = sum

difference = lambda s: reduce(lambda a, b: a - b, s)

product = lambda s: reduce(lambda a, b: a * b, s)

ratio = lambda s: reduce(lambda a, b: a / float(b), s)

average = lambda s: sum(s) / float(len(s))


def count(s):
    """
    Accumulative count of values from one or more field, wrapped
    in iterable s.  If field(s) are multiple-choice (collection) field
    then this is count of selected choices in data.  If fields contain
    string data, then this is accumulative string length.
    """
    return sum([(len(v) if hasattr(v, '__len__') else 0) for v in s])

