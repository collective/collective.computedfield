import datetime

from plone.autoform.interfaces import OMITTED_KEY
from z3c.form.interfaces import IEditForm
from zope import schema
from zope.component import queryAdapter
from zope.interface import implements

from collective.computedfield import ComputedFieldMessageFactory as _
import functions
from interfaces import IComputedField, IComputedValueFactory
from utils import normalize_data, normalize_value

try:
    from plone.supermodel.exportimport import BaseHandler
    HAS_SUPERMODEL = True
except ImportError:
    HAS_SUPERMODEL = False

try:
    from plone.schemaeditor.fields import FieldFactory
    HAS_SCHEMAEDITOR = True
except ImportError:
    HAS_SCHEMAEDITOR = False


def usable_value(value):
    if value is None:
        return False
    if isinstance(value, basestring) and value.strip() == '':
        return False
    return True


is_date = lambda v: isinstance(v, datetime.date)


class ComputedField(schema.Float):
    """Computed floating point field"""

    implements(IComputedField)

    def __init__(self, *args, **kwargs):
        for name in ('function', 'fields', 'factory', 'multiplier'):
            value = kwargs.get(name)
            field = IComputedField[name]
            if value is None and field.required:
                raise ValueError('Required value not provided, %s' % name)
            if value:
                field.validate(value)
            if isinstance(value, basestring):
                value = value.strip()
            setattr(self, name, value)
            if name in kwargs:
                del(kwargs[name])
        self._defaultConstant = IComputedField['multiplier'].default
        self._factory = None
        super(ComputedField, self).__init__(*args, **kwargs)

    def hideFromInput(self):
        """
        Set plone.autoform omitted flag on schema tagged values for this
        field.
        Precondition: call only once self.interface and self.__name__
        are both set.
        """
        omitted = self.interface.queryTaggedValue(OMITTED_KEY)
        if omitted is None:
            omitted = []
            self.interface.setTaggedValue(OMITTED_KEY, omitted)
        omitted.append((IEditForm, self.__name__, 'true'))

    def __setattr__(self, name, value):
        super(ComputedField, self).__setattr__(name, value)
        if name in ('interface', '__name__'):
            if self.__name__ and self.interface:
                self.hideFromInput()

    def compute(self, context):
        c = getattr(self, 'multiplier', None)
        if c is None:
            c = self._defaultConstant
        data = normalize_data(context)
        if self.factory:
            if self._factory is None:
                self._factory = queryAdapter(
                    context,
                    IComputedValueFactory,
                    name=self.factory,
                    )
            if self._factory:
                return self._factory(data)
        fn = getattr(functions, self.function)
        values = [data.get(name) for name in self.fields]
        normalized_values = filter(
            usable_value,
            map(
                lambda v: v if isinstance(v, float) else normalize_value(v),
                values,
                )
            )
        if fn is functions.ratio and not all(normalized_values[1:]):
            return None  # avoid zero division
        if any(map(is_date, values)) and len(normalized_values) < 2:
            return None  # no date calculations on too-few values
        return c * fn(normalized_values)


# plone.supermodel handler
if HAS_SUPERMODEL:
    ComputedFieldHandler = BaseHandler(ComputedField)


# plone.schemaeditor factory
if HAS_SCHEMAEDITOR:
    ComputedFieldFactory = FieldFactory(
        ComputedField,
        _(u'label_computed_field', default=u'Computed field'),
        )


def computed_for_schema(iface):
    """Return list of field names of computed fields for schema"""
    fields = filter(
        lambda field: isinstance(field, ComputedField),
        list(zip(*schema.getFieldsInOrder(iface))[1])
        )
    return [f.__name__ for f in fields]


def save_value(context, fieldname, value):
    if hasattr(context, '__setitem__') and hasattr(context, '__delitem__'):
        # looks like mapping, treat as such
        context[fieldname] = value
    else:
        setattr(context, fieldname, value)


def complete(context, schema):
    """
    Given context, schema; compute all ComputedField in schema
    for context, save on context.
    """
    fields = computed_for_schema(schema)
    for fieldname in fields:
        field = schema[fieldname]
        if not field.factory and not field.function:
            continue
        value = field.compute(context)
        save_value(context, fieldname, value)

