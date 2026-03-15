# [BUG] `return_fields` filtering sets non-nullable fields to None, breaking output validation

## Summary

When `list_documents` or `get_document` is called with a `return_fields` parameter, the `_filter_fields` helper sets all non-listed fields to `None`. However, some fields on the `Document` Pydantic model (e.g. `tags`) are non-nullable types (e.g. `list[int]`). FastMCP validates the return value against the model schema and raises `Output validation error: None is not of type 'array'`, making the tool unusable whenever `return_fields` is specified.

---

## Environment

- **Version / Release:** current `master` (commit `9834663`)
- **Python Version:** unspecified
- **Paperless-ngx Version:** unspecified
- **Platform / OS:** unspecified
- **Browser / Client (if applicable):** Claude Desktop with easypaperless-mcp configured
- **Other relevant context:** Triggered any time `return_fields` omits a non-nullable `Document` field (e.g. `tags`, `notes`, `custom_fields`)

---

## Steps to Reproduce

1. Configure the easypaperless-mcp server in Claude Desktop.
2. Ask Claude to list documents with a restricted field set, e.g.:
   ```json
   {
     "max_results": 10,
     "ordering": "-added",
     "return_fields": ["id", "title", "tags", "added"]
   }
   ```
3. Observe the error returned by the MCP server.

---

## Expected Behavior

`list_documents` returns a list of `Document` objects containing only the requested fields. Fields not in `return_fields` are represented with a type-appropriate empty value (empty list for list fields, empty string for string fields, etc.) so that the Pydantic model remains valid and FastMCP output validation passes.

---

## Actual Behavior

FastMCP raises an output validation error:

```
Output validation error: None is not of type 'array'
```

This occurs because `_filter_fields` unconditionally sets excluded fields to `None`, including fields whose Pydantic type does not permit `None` (e.g. `tags: list[int]`).

---

## Root Cause

`_filter_fields` in `tools/documents.py` (line 49) builds a dict of all non-listed fields mapped to `None` and applies it via `model_copy(update=to_null)`. It does not inspect the field's type annotation to determine whether `None` is a legal value for that field.

Fields like `tags`, `notes`, and `custom_fields` on the `Document` model are typed as plain lists (not `Optional[list[...]]`), so setting them to `None` produces an invalid model that fails FastMCP's schema-based output validation.

---

## Impact

- **Severity:** `High`
- **Affected Users / Systems:** All users of the `list_documents` and `get_document` MCP tools whenever `return_fields` excludes any non-nullable field; this is the typical use-case since `return_fields` defaults omit many fields.

---

## Acceptance Criteria

- [ ] `_filter_fields` uses type-appropriate empty values for non-nullable fields instead of `None`: empty list (`[]`) for list fields, empty string (`""`) for string fields, and `None` only for fields typed as `Optional` / `X | None`.
- [ ] `list_documents` called with `return_fields=["id", "title", "tags", "added"]` returns successfully without validation errors.
- [ ] `get_document` called with a restricted `return_fields` list returns successfully without validation errors.
- [ ] Fields that genuinely accept `None` (Optional fields) continue to be set to `None` when excluded from `return_fields`.
- [ ] Regression test covers the scenario of calling `list_documents` with a `return_fields` subset that excludes non-nullable list fields.
- [ ] All existing unit tests continue to pass.

---

## Additional Notes

- The `Document` model is defined in the `easypaperless` package. Field nullability should be inferred from `model_fields` annotations (check if `NoneType` is in the union args, or if the field has `is_required=False` with a non-None default).
- A straightforward approach: for each field to null out, check `field.is_required` and the annotation — if `None` is not in the allowed types, substitute the field's `default` or `default_factory` result; fall back to `[]` for lists and `""` for `str`.
- Related implementation: `src/easypaperless_mcp/tools/documents.py`, function `_filter_fields` (line 38–52).
