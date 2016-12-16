from plone.autoform import utils
from plone.autoform.interfaces import OMITTED_KEY


orig_mergedTaggedValuesForForm = utils.mergedTaggedValuesForForm


def mergedTaggedValuesForForm(schema, name, form):
    if form.__class__.__name__ == 'SchemaListing' and name == OMITTED_KEY:
        return {}
    return orig_mergedTaggedValuesForForm(schema, name, form)

