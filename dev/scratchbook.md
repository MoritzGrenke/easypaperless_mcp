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
