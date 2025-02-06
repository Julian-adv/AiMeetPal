def get_global_var(id: str) -> int:
    # TODO: Implement actual global variable retrieval
    return 0


def skip_whitespace(text: str, pos: int) -> int:
    while pos < len(text) and text[pos].isspace():
        pos += 1
    return pos


def parse_number(text: str, pos: int) -> tuple[int, int]:
    num = ""
    while pos < len(text) and text[pos].isdigit():
        num += text[pos]
        pos += 1
    return int(num) if num else 0, pos


def parse_var_expr(text: str, pos: int) -> tuple[int, int]:
    if text[pos:].startswith("{{getglobalvar::"):
        end = text.find("}}", pos)
        if end == -1:
            return 0, pos
        var_id = text[pos + 16 : end]
        value = get_global_var(var_id)
        return value, end + 2
    return parse_number(text, pos)


def parse_keyword(text: str, pos: int, values: dict) -> tuple[str, int]:
    if text[pos:].startswith("{{user}}"):
        return values["user"], pos + 8
    if text[pos:].startswith("{{char}}"):
        return values["char"], pos + 8
    if text[pos:].startswith("{{"):
        pos = text.find("}}", pos) + 2
        return "", pos
    return "", pos


def parse_term(text: str, pos: int) -> tuple[int, int]:
    if pos < len(text) and text[pos] == "(":
        pos = skip_whitespace(text, pos + 1)
        value, pos = parse_expression(text, pos)
        pos = skip_whitespace(text, pos)
        if pos < len(text) and text[pos] == ")":
            return value, pos + 1
    return parse_var_expr(text, pos)


def parse_expression(text: str, pos: int) -> tuple[int, int]:
    value, pos = parse_term(text, pos)
    pos = skip_whitespace(text, pos)

    while pos < len(text) and text[pos] in "+>=":
        op = text[pos]
        pos = skip_whitespace(text, pos + 1)
        right_value, pos = parse_term(text, pos)

        if op == "+":
            value += right_value
        elif op == ">":
            value = int(value > right_value)
        elif op == "=":
            value = int(value == right_value)

        pos = skip_whitespace(text, pos)

    return value, pos


def parse_condition(text: str, pos: int) -> tuple[bool, int]:
    if text[pos:].startswith("{{?"):
        pos += 3  # Skip {{?
        pos = skip_whitespace(text, pos)

        value, pos = parse_expression(text, pos)
        pos = skip_whitespace(text, pos)

        if text[pos:].startswith("}}"):
            return bool(value), pos + 2
        else:
            return text[pos], pos
    else:
        return parse_var_expr(text, pos)


def parse_if_expr(text: str, pos: int, values: dict) -> tuple[str, int]:
    if not text[pos:].startswith("{{#if"):
        return text[pos], pos

    pos += 5  # Skip {{#if
    pos = skip_whitespace(text, pos)
    condition_value, pos = parse_condition(text, pos)
    pos = skip_whitespace(text, pos)
    if text[pos:].startswith("}}"):
        pos += 2  # Skip }}
    else:
        return text[pos], pos

    result = []
    if condition_value:
        template_text, pos = parse_template(text, pos, values)
        result.append(template_text)
    else:
        _, pos = parse_template(text, pos, values)

    if text[pos:].startswith("{{/if}}"):
        return "".join(result), pos + 7

    return "".join(result), pos


def parse_template(text: str, pos: int, values: dict) -> tuple[str, int]:
    result = []
    while pos < len(text):
        if text[pos:].startswith("{{#if"):
            template_text, pos = parse_if_expr(text, pos, values)
            result.append(template_text)
        elif text[pos:].startswith("{{/if}}"):
            break
        # elif text[pos:].startswith("{{getglobalvar::"):
        #     value, new_pos = parse_var_expr(text, pos)
        #     result.append(str(value))
        #     pos = new_pos
        elif text[pos:].startswith("{{"):
            template_text, pos = parse_keyword(text, pos, values)
            result.append(template_text)
        else:
            result.append(text[pos])
            pos += 1

    return "".join(result), pos


# template   -> (
#             | if_expr
#             | text
#             | keyword )*
# if_expr    -> {{#if condition }} template {{/if}}
# condition  -> {{? expression }}
#             | var_expr
# expression -> term op term
# op         -> + | > | =
# term       -> '(' expression ')'
#             | var_expr
# var_expr   -> {{getglobalvar::var_id}}
#             | {{user}}
#             | {{char}}
#             | number
# keyword    -> {{char}}
#             | {{user}}


def compile_prompt(text: str, values: dict) -> str:
    result, _ = parse_template(text, 0, values)
    return result


def make_googleaistudio_prompt(
    user,
    name,
    wiBefore,
    description,
    personality,
    scenario,
    examples,
    wiAfter,
    persona,
    entries,
    start_index,
    preset,
):
    values = {
        "user": user,
        "char": name,
    }
    prompts = preset["promptTemplate"]
    text = ""
    for prompt in prompts:
        if "text" in prompt:
            text += compile_prompt(prompt["text"], values)
    print(text)
