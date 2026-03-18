# [BUG] `_filter_fields` sets required non-nullable fields to `None` when omitted from `return_fields`

## Summary

When `list_documents` or `get_document` is called with a `return_fields` list that omits `id` or `title`, the `_filter_fields` helper sets those fields to `None`. Because `id` (`int`) and `title` (`str`) are required non-nullable fields on the `Document` model, this produces an invalid model and causes a Pydantic validation error. The current implementation acknowledges this gap in a docstring comment but does not resolve it.

---

## Environment

- **Version / Release:** current `master`
- **Python Version:** unspecified
- **Paperless-ngx Version:** unspecified
- **Platform / OS:** unspecified
- **Other relevant context:** Follow-on from issue 0003 — the 0003 fix handles list fields and Optional fields, but required fields with no default still fall through to `None` (line 69 in `_filter_fields`).

---

## Steps to Reproduce

1. Configure the easypaperless-mcp server.
2. Call `list_documents` or `get_document` with a `return_fields` list that omits `id` or `title`, e.g.:
   ```json
   { "return_fields": ["created", "tags"] }
   ```
3. Observe the Pydantic validation error due to `id` being `None` (typed `int`) or `title` being `None` (typed `str`).

---

## Expected Behavior

Fields omitted from `return_fields` are represented with a type-appropriate empty/zero value so the `Document` model stays valid:
- `id` (`int`) → `0`
- `title` (`str`) → `""`

Additionally, `id` should always be included in the response regardless of `return_fields`, since it is the document's primary identifier and is needed for any follow-up tool call.

---

## Actual Behavior

`_filter_fields` sets required fields with no Pydantic default to `None` (fallback at line 69). This produces a `Document` where `id=None` or `title=None`, which is invalid and raises a validation error.

---

## Impact

- **Severity:** `Medium`
- **Affected Users / Systems:** Any caller of `list_documents` or `get_document` who omits `id` or `title` from `return_fields`. The default `return_fields` values always include both fields, so typical usage is not affected — but explicit customisation triggers the bug.

---

## Acceptance Criteria

- [ ] `_filter_fields` infers a type-appropriate zero/empty value for required fields with no Pydantic default: `0` for `int`, `""` for `str`, `False` for `bool`.
- [ ] `id` is always included in the output of `list_documents` and `get_document`, regardless of what is passed in `return_fields`. If the caller omits `id`, it is silently added back.
- [ ] Calling `list_documents` with `return_fields=["created", "tags"]` succeeds without a validation error and returns documents with `id` populated and `title=""`.
- [ ] Calling `get_document` with `return_fields=["created"]` succeeds without a validation error and returns a document with `id` populated and `title=""`.
- [ ] All existing unit and integration tests continue to pass.
- [ ] A regression test covers calling `list_documents` and `get_document` with `return_fields` that omits `id` and `title`.

---

## Additional Notes

- The gap is documented in the current `_filter_fields` docstring: *"Required fields with no default are set to `None` as a last resort (they should always be included in `return_fields`)"*.
- `PydanticUndefined` is not a valid field value — it signals the absence of a default at field definition time and cannot be used as a substitute here.
- Type-appropriate zero values should be inferred from the field's annotation using `get_args`/`get_origin` from the `typing` module, or by checking the outermost type directly from `field_info.annotation`.
- Related implementation: `src/easypaperless_mcp/tools/documents.py`, function `_filter_fields`.

---

## QA

**Tested by:** QA Engineer
**Date:** 2026-03-18
**Commit:** 4cb1d0f (working tree with uncommitted implementation)

### Test Results

| # | Test Case | Expected | Actual | Status |
|---|-----------|----------|--------|--------|
| 1 | AC1: `_filter_fields` uses `0` for required `int` fields | `id=0` when omitted | `id=0` — `_zero_value_for` maps `int→0` via `_ZERO_VALUES` dict | ✅ Pass |
| 2 | AC1: `_filter_fields` uses `""` for required `str` fields | `title=""` when omitted | `title=""` — `_zero_value_for` maps `str→""` via `_ZERO_VALUES` dict | ✅ Pass |
| 3 | AC1: `_filter_fields` uses `False` for required `bool` fields | `False` when omitted | `False` — `_zero_value_for` maps `bool→False` via `_ZERO_VALUES` dict | ✅ Pass (code path verified; no required bool fields in Document model) |
| 4 | AC2: `list_documents` silently adds `id` back when omitted from `return_fields` | `id` in result | `id` added back at `documents.py:228-229` | ✅ Pass |
| 5 | AC2: `get_document` silently adds `id` back when omitted from `return_fields` | `id` in result | `id` added back at `documents.py:336-337` | ✅ Pass |
| 6 | AC3: `list_documents(return_fields=["created","tags"])` — no validation error, `id` populated, `title=""` | No exception; `id=3`, `title=""` | As expected — unit test `test_list_documents_return_fields_omitting_id_and_title` passes | ✅ Pass |
| 7 | AC4: `get_document(id, return_fields=["created"])` — no validation error, `id` populated, `title=""` | No exception; `id=10`, `title=""` | As expected — unit test `test_get_document_return_fields_omitting_title` passes | ✅ Pass |
| 8 | AC5: All unit tests pass | 235 passed, 0 failed | 235 passed, 0 failed | ✅ Pass |
| 9 | AC5: Integration tests pass | 22 passed, 0 failed | 22 passed, 5 failed — failures in `test_document_notes.py` (pre-existing, tracked in issue 0016) | ✅ Pass (pre-existing failures unrelated to 0017) |
| 10 | AC6: Regression tests for `list_documents` with omitted `id`/`title` | Tests exist and pass | `test_list_documents_always_includes_id_even_when_omitted` and `test_list_documents_return_fields_omitting_id_and_title` both pass | ✅ Pass |
| 11 | AC6: Regression tests for `get_document` with omitted `id`/`title` | Tests exist and pass | `test_get_document_always_includes_id_even_when_omitted` and `test_get_document_return_fields_omitting_title` both pass | ✅ Pass |
| 12 | Edge: `return_fields=[]` (empty list) — id is added, all other fields zeroed | No exception; `id` populated | id silently added by guard; `_filter_fields` sets all fields to zero values | ✅ Pass |
| 13 | Edge: `_zero_value_for` with union type `int \| None` | Returns `0` (first non-None arg) | `get_args` extracts `[int, NoneType]`, `non_none=[int]`, returns `_ZERO_VALUES[int]=0` | ✅ Pass |
| 14 | Lint/type-check: ruff + mypy on `src/` | No errors | All checks passed; no mypy issues in 12 source files | ✅ Pass |

### Bugs Found

None.

### Automated Tests
- Suite: unit — 235 passed, 0 failed
- Suite: integration — 22 passed, 5 failed
  - Failed (pre-existing, unrelated to 0017): `test_document_notes.py` — 5 tests fail with `AttributeError: 'list' object has no attribute 'get'` in easypaperless library's `http.py`. This is an easypaperless 0.3.x API incompatibility tracked under issue 0016.

### Summary
- ACs tested: 6/6
- ACs passing: 6/6
- Bugs found: 0
- Recommendation: ✅ Ready to merge
