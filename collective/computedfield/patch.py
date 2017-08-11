from plone.autoform import utils
from plone.autoform.interfaces import OMITTED_KEY

from field import ComputedField


try:
    from plone.schemaeditor.browser.schema.listing import SchemaListing

    orig_mergedTaggedValuesForForm = utils.mergedTaggedValuesForForm

    def mergedTaggedValuesForForm(schema, name, form):
        result = orig_mergedTaggedValuesForForm(schema, name, form)
        if issubclass(form.__class__, SchemaListing) and name == OMITTED_KEY:
            for fieldname in result.keys():
                field = schema[fieldname]
                if isinstance(field, ComputedField):
                    del(result[fieldname])
        return result

except ImportError:
    pass
