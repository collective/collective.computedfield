from zope import schema
from zope.component import queryAdapter
from zope.interface import implements

import functions
from interfaces import IComputedField, IComputedValueFactory
from utils import normalize_data

try:
    from plone.supermodel.exportimport import BaseHandler
    HAS_SUPERMODEL = True
except ImportError:
    HAS_SUPERMODEL = False


class ComputedField(schema.Float):
    """Computed floating point field"""

    implements(IComputedField)

    def __init__(self, *args, **kwargs):
        for name in ('function', 'fields', 'factory'):
            value = kwargs.get(name)
            field = IComputedField[name]
            if value is None and field.required:
                raise ValueError('Required value not provided, %s' % name)
            if value:
                field.validate(value)
            if isinstance(value, basestring):
                value = value.strip()
            setattr(self, name, value)
            del(kwargs[name])
        self._factory = None
        super(ComputedField, self).__init__(*args, **kwargs)

    def compute(self, context):
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
        return fn([data.get(field) for field in self.fields])


# plone.supermodel handler
if HAS_SUPERMODEL:
    ComputedFieldHandler = BaseHandler(ComputedField)

