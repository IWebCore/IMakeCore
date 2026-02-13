# HtmlTemplate
> ginger like html template in Qt，

> If you like to know about ginger, please visit [ginger](https://github.com/subosito/gingerice).


## Supported grammer

### Value statement

```plain
${{value}}
```


### if judgement
```text
$if val {{
    // content
}}

---
$if val {{
    // content
}} $elif {{
    // branch
}} $else{{
    // branch
}}
```


### for loop

```text
$for val in path {{
    // content
}}
```

## Error handle

if error occur in template, it will throw a `NodyError` exception. this exception will be intercepted in `parse` function and return a status code to you, and fatal the program.

below is an example:
```
ERROR: error, can not eat variable: {{ NEAR: hello {{ <h1>hello world></h1> }}
ERROR: parse $if error NEAR: $if error hello {{ <h1>hello world></h1>...
```

## plan

### support more grammar

- embended languange support

    - $js support

```js
$js {{
    return "hello world";
}}
```

- python support    `$py`
- lua support   `$lua`

- template extends support
```html
$extend {{path}}

$block a {{}}
$block b {{}}
```

- include support
```html
$include {{path}}
```

## About
This project is the support of `IWebCore` project, which is a web framework based on Qt. the unrealized function is to be provieded in `IWebCore`. and this project stop update here because it is not a priority.
