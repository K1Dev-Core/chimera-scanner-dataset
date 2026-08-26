# GraphQL CTF Patterns

## Endpoint Discovery

Check HTML and JavaScript for GraphQL JSON bodies:

```javascript
fetch('/rocketql', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({query: '{ rockets(country: "France") { name } }'})
})
```

Common paths: `/graphql`, `/api/graphql`, `/gql`, `/query`, `/rocketql`, `/graphiql`, `/playground`.

## Introspection Disabled

Use error suggestions:

```graphql
{ usre { id } }
{ user { definitelyNotAField } }
```

GraphQL implementations often respond with close field-name suggestions. Try nouns from page text, object names in JavaScript, and resolver names implied by network calls.

## Hidden Query Enumeration

After root fields are known, inspect each object type and request all scalar fields. Required integer arguments are often enumerable:

```graphql
{ Hidden(id: 1) { __typename id value } }
{ Hidden(id: 2) { __typename id value } }
```

Try small ranges before broad scans. If values spell decoys such as `nothinghere`, keep going a little past the message.

## Argument Injection

If client code concatenates a selected value into a GraphQL query, test whether user-controlled strings can escape the argument:

```graphql
{ rockets(country: "France") { name } hidden: IAmNotHere(very_long_id: 17) { very_long_value } #") { name } }
```

If the server sends the GraphQL query directly, this can add aliases or extra root selections. If the GraphQL resolver builds SQL/NoSQL queries internally, switch to SQLi/NoSQLi reasoning after confirming resolver behavior.

## Useful Flag Searches

Search returned JSON for:

```text
RM{
flag
secret
password
pass
token
Congratulations
validate
```
