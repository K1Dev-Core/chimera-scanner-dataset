#!/usr/bin/env python3
import argparse
import json
import sys
import urllib.error
import urllib.request


ROOT_INTROSPECTION = """
{
  __schema {
    queryType {
      fields {
        name
        args { name type { name kind ofType { name kind } } }
        type { name kind ofType { name kind } }
      }
    }
  }
}
""".strip()


TYPE_QUERY = """
query($name: String!) {
  __type(name: $name) {
    name
    fields {
      name
      type { name kind ofType { name kind } }
    }
  }
}
""".strip()


def post_graphql(endpoint, query, variables=None):
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    request = urllib.request.Request(
        endpoint,
        data=body,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as exc:
        text = exc.read().decode("utf-8", "replace")
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"http_error": exc.code, "body": text}


def print_json(value):
    print(json.dumps(value, indent=2, ensure_ascii=False))


def build_enum_query(field, arg, fields, value):
    return f"{{ {field}({arg}: {value}) {{ __typename {fields} }} }}"


def enum_payload_is_empty(result, field):
    data = result.get("data") if isinstance(result, dict) else None
    if not isinstance(data, dict) or field not in data:
        return False
    return data[field] in (None, [])


def main():
    parser = argparse.ArgumentParser(description="Small GraphQL helper for CTF introspection and integer enumeration.")
    parser.add_argument("endpoint")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--query", help="GraphQL query to send")
    group.add_argument("--introspect", action="store_true", help="List root query fields")
    group.add_argument("--type", help="Inspect an object type by name")
    group.add_argument("--enum-int", nargs=2, metavar=("FIELD", "ARG"), help="Enumerate an integer argument")
    parser.add_argument("--fields", default="id value flag secret password very_long_id very_long_value", help="Fields to request for --enum-int")
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--end", type=int, default=30)
    parser.add_argument("--show-empty", action="store_true")
    args = parser.parse_args()

    if args.query:
        print_json(post_graphql(args.endpoint, args.query))
        return

    if args.introspect:
        print_json(post_graphql(args.endpoint, ROOT_INTROSPECTION))
        return

    if args.type:
        print_json(post_graphql(args.endpoint, TYPE_QUERY, {"name": args.type}))
        return

    field, arg = args.enum_int
    for value in range(args.start, args.end + 1):
        result = post_graphql(args.endpoint, build_enum_query(field, arg, args.fields, value))
        is_empty = enum_payload_is_empty(result, field)
        if args.show_empty or not is_empty:
            print(f"## {arg}={value}")
            print_json(result)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
