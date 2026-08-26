---
name: ctf-graphql-introspection
description: Solve CTF web challenges built around GraphQL endpoints, especially when introspection is enabled, hidden root queries or object fields exist, client JavaScript sends GraphQL JSON to paths like /graphql or /rocketql, or the task requires extracting a flag by enumerating schema fields, arguments, IDs, aliases, or concealed resolver data. Use for Root-Me and similar CTF GraphQL recon, hidden query discovery, schema dumping, and small-scale value enumeration.
---

# CTF GraphQL Introspection

## Overview

Use this skill to turn a suspected CTF GraphQL endpoint into a small map of its schema and hidden data. Prefer direct HTTP requests over browser-only interaction; most challenges expose enough through introspection, validation errors, or enumerable resolver arguments.

## Workflow

1. Capture the normal request.
   - Inspect HTML and JavaScript for `fetch`, `axios`, `/graphql`, `/api/graphql`, `/rocketql`, `query:`, `mutation:`, or `Content-Type: application/json`.
   - Reproduce one valid query with `curl`, PowerShell `Invoke-RestMethod`, or `scripts/graphql_probe.py`.

2. Test introspection.
   - Query `__schema.queryType.fields` first; this is compact and usually enough.
   - Then query suspicious object types with `__type(name:"TypeName")`.
   - If querying `__type` more than once, use aliases to avoid GraphQL field conflicts.

3. Identify hidden entry points.
   - Compare public UI fields with all root fields from introspection.
   - Prioritize strange names, challenge-y names, unused resolvers, and fields with required scalar args such as `id`, `very_long_id`, `token`, `name`, or `country`.
   - Inspect return object fields; request every scalar field, plus `__typename`.

4. Enumerate safely.
   - For integer args, try small ranges first: `0..30`, then common values like `42`, `100`, `1337`, years, and IDs found in normal objects.
   - For string args, try values already present in the UI, then use GraphQL string-breaking only when the server builds downstream queries unsafely.
   - Look for flag patterns such as `RM{`, `flag`, `password`, `secret`, `Congratulations`, and unusually long strings.

5. If introspection is disabled.
   - Use validation errors to infer field names: submit guessed fields and read `"Cannot query field"` suggestions.
   - Try common root fields from UI nouns and challenge text.
   - Read `references/graphql-ctf-patterns.md` for fallback probes.

## Compact Introspection Queries

Root query fields:

```graphql
{ __schema { queryType { fields { name args { name type { name kind ofType { name kind } } } type { name kind ofType { name kind } } } } } }
```

Object fields:

```graphql
{ t: __type(name:"TypeName") { name fields { name type { name kind ofType { name kind } } } } }
```

Hidden resolver example:

```graphql
{ HiddenQuery(id: 17) { __typename id value secret flag } }
```

## Script

Use `scripts/graphql_probe.py` when shell quoting is annoying or repeated POSTs are needed. It supports:

```bash
python scripts/graphql_probe.py ENDPOINT --query '{ __schema { queryType { fields { name } } } }'
python scripts/graphql_probe.py ENDPOINT --introspect
python scripts/graphql_probe.py ENDPOINT --enum-int IAmNotHere very_long_id --fields 'very_long_id very_long_value' --start 0 --end 30
```

## Notes

- Do not assume the flag is in `flag`; challenge authors often hide it in harmless names like `value`, `description`, or `very_long_value`.
- GraphQL returns validation and resolver errors as JSON; inspect error text before changing tools.
- Use aliases for duplicate meta-fields: `a: __type(name:"A")`, `b: __type(name:"B")`.
- Read `references/graphql-ctf-patterns.md` when introspection is blocked, args are non-obvious, or injection into a GraphQL argument may be required.
