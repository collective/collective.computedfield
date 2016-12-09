import json

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


def normalize_data(context):
    """Return a dict of context data"""
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
    return getattr(context, '__dict__', {})  # attrs as mapping


