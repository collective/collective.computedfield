from zope import schema
from zope.interface import Interface, implements
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

try:
    from plone.schemaeditor.schema import IFloat
except ImportError:
    from zope.schema.interfaces import IFloat


class IComputedFieldProductLayer(Interface):
    """Marker interface for browser layer"""


# computation stock function names;
# Terms are unicode since plone.supermodel handlers treat string values of
# field attributes accordingly; ensures repeatable round-trip serialization.
FN_CHOICES = SimpleVocabulary(
    [SimpleTerm(t[0], title=t[1]) for t in (
        (u'sum', u'Sum of values'),
        (u'difference', u'Difference of values'),
        (u'product', u'Product of values'),
        (u'ratio', u'Ratio (division) of values'),
        (u'average', u'Average (mean) of values'),
        (u'count', u'Count of selected values'),
        )]
    )


class FieldChoiceBinder(object):
    """Source binder for computed field choices of other fields"""

    implements(IContextSourceBinder)

    def __call__(self, context):
        iface = context.interface
        # other fields in the schema
        fields = filter(
            lambda field: field.__name__ != context.__name__,
            list(zip(*schema.getFieldsInOrder(iface))[1]),
            )
        return SimpleVocabulary([
            SimpleTerm(
                field.__name__,
                title=field.title
                )
            for field in fields
            ])

    def __contains__(self, value):
        """Permissive containment hack for validation"""
        return True


class IComputedField(IFloat):
    """Computed field schema"""

    factory = schema.TextLine(
        title=u'Factory name',
        description=u'Name of factory function (registered adapter), which '
                    u'given data context, will return computed value.  '
                    u'A valid identifier here will override any stock '
                    u'function chosen.',
        required=False,
        )

    function = schema.Choice(
        title=u'Function name',
        description=u'Choose a stock computation function.',
        vocabulary=FN_CHOICES,
        required=False,
        )

    fields = schema.List(
        title=u'Field sources',
        description=u'Choose fields used by function, in order.',
        value_type=schema.Choice(
            source=FieldChoiceBinder(),
            ),
        required=False,
        )

    def compute(context):
        """
        Given context as either mapping/dict, or attribute-containing
        object, compute field value based upon data, given rules
        configured on field (either function/fields pairing, or
        delegate computation to a named, registered factory adapter,
        if provided.
        """


class IComputedValueFactory(Interface):
    """
    Marker interface for factory callable/function registration: value
    factory functions take a single context (as either mapping/dict) or
    as an attribute-containing object containing data/content, and
    return a calculation for that object.
    """

