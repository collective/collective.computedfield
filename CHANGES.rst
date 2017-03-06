Changelog
=========

0.1 (unreleased)
----------------

- Filter out empty values in calculation, and in case of date fields,
  if the number of arguments that are non-empty (not None) is less than
  two, save None to computed field.
  [seanupton]

- Preempt any chance at division by zero in case of ratio function.
  [seanupton]

- Fix failure to default a non-filled-in constant multiplier.
  [seanupton]

- Support a constant multipler for the purpose of allowing a ratio to be
  expressed as a percentage.
  [seanupton]

- Hide min/max from schemaeditor editing; move factory name to bottom of
  form.
  [seanupton]

- Make plone.autoform a dependency.
  [seanupton]

- Detection method in utils, has_computed_fields() determines if an
  interface contains any computed fields.
  [seanupton]

- Omit ComputedField from edit forms, excepting (via monkey patch of
  plone.autoform) plone.schemaeditor listing.
  [seanupton]

- Completion methods for use by downstream callers.
  [seanupton]

- Tests for value and data normalization.
  [seanupton]

- Data normalization for non-float field sources.
  [seanupton]

- plone.schemaeditor support; requires this package be an installable add-on,
  with a GenericSetup profile.  The reason this is necessary is to include
  a JavaScript shim to support z3c.form multi-select widget JS when edit
  form for a field in schemaeditor is within Plone 4 overlays.
  [seanupton]

- Initial development, package scaffolding, interfaces, basic components.
  [seanupton]

