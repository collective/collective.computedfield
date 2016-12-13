import datetime
import unittest

from BTrees.OOBTree import OOBTree
import persistent
import pytz

from collective.computedfield import utils


def has_remainder(v):
    v = float(v)
    return not v % 1 == 0.0


class TestSundry(unittest.TestCase):
    """Test sundry utils functions and implementation details"""

    def test_dict_getter(self):
        """Test dict getter function"""
        # object that has a dict, vs object that does not:
        class Foo(object):
            """Something"""
        data = Foo()
        data.this = 1
        data.that = 2
        from collective.computedfield.utils import _dict
        # assumed order presevation from contrived example:
        self.assertEqual(_dict(data).items(), [('this', 1), ('that', 2)])
        # object without dict (nonsense example: int)
        v = 1
        self.assertTrue(isinstance(_dict(v), dict))
        self.assertEqual(_dict(v).items(), [])

    def test_detection(self):
        """Test detection of persistent mapping data types"""
        # BTree:
        bt = OOBTree()
        self.assertTrue(utils.is_btree(bt))
        # PersistentMapping / PersistentDict:
        pmap = persistent.mapping.PersistentMapping()
        from persistent.dict import PersistentDict  # same game, deprecated name
        pd = PersistentDict()
        self.assertTrue(all(map(lambda v: utils.is_pmap(v), (pmap, pd))))

    def test_parse_datestamp(self):
        """Test ISO 8601 datestamp parsing"""
        stamp1 = '2016-12-02'
        stamp2 = '2016-11-15T11:15:00Z'
        expected = {
            # simple date stamp into datetime to datetime w/ 00:00 UTC
            stamp1: (2016, 12, 2),
            # date stamp with time info, ignored here deliberately, date
            # portion is used only, with time set to 00:00 UTC
            stamp2: (2016, 11, 15),
            }
        for stamp, result in expected.items():
            v = utils.parse_datestamp(stamp)
            self.assertTrue(isinstance(v, datetime.datetime))
            self.assertEqual((v.year, v.month, v.day), result)
            self.assertEqual((v.hour, v.minute), (0, 0))
            self.assertEqual(v.tzinfo, pytz.UTC)

    def test_days_since_epoch(self):
        """Test days_since_epoch() calculation"""
        # test datetime.date, should return float with no remainder:
        v1 = datetime.date(2016, 12, 2)
        v2 = datetime.date(2016, 12, 4)
        d1 = utils.days_since_epoch(v1)
        self.assertTrue(not has_remainder(d1))
        self.assertEqual(d1, 17137.0)
        d2 = utils.days_since_epoch(v2)
        self.assertTrue(not has_remainder(d2))
        self.assertEqual(d2, 17139.0)
        self.assertEqual(d2 - d1, 2)
        # test datetime.datetime, should return float with remainder:
        v3 = datetime.datetime(2016, 12, 2, 3, 30, tzinfo=pytz.UTC)
        d3 = utils.days_since_epoch(v3)
        self.assertTrue(has_remainder(d3))
        self.assertTrue(d3 > 17137.0 and d3 < 17138.0)


class TestNormalization(unittest.TestCase):
    """
    Test for data and value normalization, which are respectively
    addressing distinct problems (that is, data normalization is about
    containment format, and value normalization is about data value types.
    """

    # value normalization:

    def test_normalize_value_int(self):
        """
        Test normalization of int to float.
        """
        normalized = utils.normalize_value(10)
        self.assertTrue(isinstance(normalized, float))
        self.assertEqual(normalized, 10.0)

    def test_normalize_value_iso8601(self):
        """
        Test normalization of ISO 8601 datestamps to days since epoch float.
        """
        stamp = '2016-12-02'
        normalized = utils.normalize_value(stamp)
        self.assertTrue(isinstance(normalized, float))
        self.assertEqual(normalized, 17137.0)

    def test_normalize_value_date(self):
        """
        Test normalization of date to days since epoch float.
        """
        d = datetime.date(2016, 12, 2)
        normalized = utils.normalize_value(d)
        self.assertTrue(isinstance(normalized, float))
        self.assertEqual(normalized, 17137.0)

    def test_normalize_value_datetime_utc(self):
        """
        Test normalization of UTC datetime.datetime to days since epoch float.
        """
        d = datetime.datetime(2016, 12, 2, 0, 0, tzinfo=pytz.UTC)
        normalized = utils.normalize_value(d)
        self.assertTrue(isinstance(normalized, float))
        self.assertEqual(normalized, 17137.0)
        # try with specified time, explicit UTC tzinfo:
        d = datetime.datetime(2016, 12, 2, 6, 0, tzinfo=pytz.UTC)
        normalized = utils.normalize_value(d)
        self.assertTrue(isinstance(normalized, float))
        self.assertEqual(normalized, 17137.25)

    def test_normalize_value_datetime_naive(self):
        """
        Test normalization of naive datetime.datetime to days since epoch
        float.
        """
        # midnight == no time info implied:
        d = datetime.datetime(2016, 12, 2, 0, 0)
        normalized = utils.normalize_value(d)
        self.assertTrue(isinstance(normalized, float))
        self.assertEqual(normalized, 17137.0)
        # specify a time, we need it treated as UTC!
        d = datetime.datetime(2016, 12, 2, 6, 0)
        normalized = utils.normalize_value(d)
        self.assertTrue(isinstance(normalized, float))
        self.assertEqual(normalized, 17137.25)

    # data (container) normalization:

    def test_normalize_data_dict(self):
        """
        Test container normalization of dict.
        """
        v = {
            'a': 1,
            'b': 2
            }
        normalized = utils.normalize_data(v)
        self.assertTrue(v is normalized)  # returns same dict obj

    def test_normalize_data_json(self):
        """
        Test container normalization of json containing mapping of key/values.
        """
        v = """{
            "a": 1,
            "b": 2
            }"""
        normalized = utils.normalize_data(v)
        self.assertTrue(isinstance(normalized, dict))
        self.assertIn('a', normalized.keys())
        self.assertIn('b', normalized.keys())
        self.assertEqual(normalized.values(), [1, 2])  # assumed order

    def test_normalize_data_persistentmapping(self):
        """
        Test container normalization of dict.
        """
        v = persistent.mapping.PersistentMapping({
            'a': 1,
            'b': 2
            })
        normalized = utils.normalize_data(v)
        self.assertTrue(isinstance(normalized, dict))
        self.assertIn('a', normalized.keys())
        self.assertIn('b', normalized.keys())
        self.assertEqual(normalized.values(), [1, 2])  # assumed order

    def test_normalize_data_btree(self):
        """
        Test container normalization of dict.
        """
        v = OOBTree({
            'a': 1,
            'b': 2
            })
        normalized = utils.normalize_data(v)
        self.assertTrue(isinstance(normalized, dict))
        self.assertIn('a', normalized.keys())
        self.assertIn('b', normalized.keys())
        self.assertEqual(normalized.values(), [1, 2])  # assumed order

    def test_normalize_data_record(self):
        """
        Test container normalization of an attribute-containing record object.
        """
        class MockRecord(object):
            """A mock record class"""
            pass

        mock = MockRecord()  # empty, let's add some attributes...
        mock.a = 1
        mock.b = 2
        normalized = utils.normalize_data(mock)
        self.assertTrue(isinstance(normalized, dict))
        self.assertIn('a', normalized.keys())
        self.assertIn('b', normalized.keys())
        self.assertEqual(
            set(normalized.values()), set([1, 2])
            )  # test without presumed value via cast to set

