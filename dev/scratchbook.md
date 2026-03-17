# scratchbook
my dev scratchbook where I drop notes. sometimes todos, thoughts or observations that later lead to work items.

## ideas from last implementation
i already had one first version for a easypaperless mcp server. but decided to start over again. 
some insights from the last version:
* i'm building for ai with limited context, context is expensive, only return large textfields when asked for
* set meaningful max_results default value - 5 or 10?
* offer an artificial parameter that reduces the result to certain specified fields. the docstring must name these fields, so that the ai knows what is available
* after an update, only return some basic fields + the changed fields (to allow for verification)
* time outs were an issue 

finding: "Also note: the .env file uses PAPERLESS_API_KEY but client.py reads PAPERLESS_TOKEN — you may want to align these."

3 skipped integration tests? why?

when testing in the fastmcp dev inspector:
created: 1999-06-11T00:00:00
Validation Error: data.created should match format "date-time", data.created should be null, data.created should match some schema in anyOf
Claude's answer:
The schema expects a date-time string with timezone (e.g. 1999-06-11T00:00:00Z), but paperless-ngx returns naive datetimes without timezone info (1999-06-11T00:00:00), which fails strict date-time format validation.
This is a data issue from paperless-ngx itself — the dates stored there have no timezone. It's not a bug in our code. The inspector is just being strict about the JSON Schema date-time format. It's a cosmetic validation warning in the inspector — the data is still returned and usable. When a real AI client calls the tool, it won't validate like this and will work fine.    



include_metadata missing in some tool? was it update_document?


delete_document_note in document resource? check

claude uses the bulk_* tools even if it is only one document two work on. not completely wrong.

help needed for difficult parameters with a certain structure. e.g. custom field queries?!

l3 archive: no search_hit field? claude says this depends on the Whoosh config!?


## 17.03.
remarks: mcp: ordering param: add possible fields to the description.
bulk_set_permissions() merge param desc!?
custom_fields.create(): extra_data desc?!
storage_paths.create(): path desc?!

sorting: make a docstring remark not to use the - prefix, but to using descending=True param. 