import random

global_vars = {
    "third_person": 1,
    "protagonist": 1,
    "enhance_depiction": 1,
}


def get_global_var(id: str) -> int:
    return global_vars.get(id, 0)


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


def parse_random(text: str, pos: int) -> tuple[str, int]:
    if text[pos:].startswith("{{random::"):
        end = text.find("}}", pos)
        if end == -1:
            raise Exception("Invalid random: expect }} got " + text[pos:])
        value_str = text[pos + 10 : end]
        value_list = value_str.split("::")
        value = random.choice(value_list)
        return value, end + 2
    return "", pos


def parse_var_expr(text: str, pos: int) -> tuple[int, int]:
    if text[pos:].startswith("{{getglobalvar::"):
        end = text.find("}}", pos)
        if end == -1:
            raise Exception("Invalid getglobalvar: expect }} got " + text[pos:])
        var_id = text[pos + 16 : end]
        value = get_global_var(var_id)
        return value, end + 2
    elif text[pos:].startswith("{{lastmessageid}}"):
        return 0, pos + 17
    elif text[pos:].startswith("{{random::"):
        value_str, pos = parse_random(text, pos)
        return int(value_str), pos
    return parse_number(text, pos)


def parse_keyword(text: str, pos: int, values: dict) -> tuple[str, int]:
    if text[pos:].startswith("{{user}}"):
        return values["user"], pos + 8
    if text[pos:].startswith("{{char}}"):
        return values["char"], pos + 8
    if text[pos:].startswith("{{slot}}"):
        parsed_value, _ = parse_template(values["slot"], 0, values)
        return parsed_value, pos + 8
    if text[pos:].startswith("{{/}}"):
        pos += 5
        if pos < len(text) and text[pos] == "\n":
            return "", pos + 1
        return "", pos
    if text[pos:].startswith("{{random::"):
        value_str, pos = parse_random(text, pos)
        return value_str, pos
    raise Exception("Unknown keyword: " + text[pos:])


def parse_term(text: str, pos: int) -> tuple[int, int]:
    if pos < len(text) and text[pos] == "(":
        pos = skip_whitespace(text, pos + 1)
        value, pos = parse_expression(text, pos)
        pos = skip_whitespace(text, pos)
        if pos < len(text) and text[pos] == ")":
            return value, pos + 1
        else:
            raise Exception("Invalid term: expect ) got " + text[pos])
    return parse_var_expr(text, pos)


def parse_mult_expr(text: str, pos: int) -> tuple[int, int]:
    value, pos = parse_term(text, pos)
    pos = skip_whitespace(text, pos)

    while pos < len(text) and text[pos] in "*":
        op = text[pos]
        pos = skip_whitespace(text, pos + 1)
        right_value, pos = parse_term(text, pos)

        if op == "*":
            value *= right_value

        pos = skip_whitespace(text, pos)

    return value, pos


def parse_add_expr(text: str, pos: int) -> tuple[int, int]:
    value, pos = parse_mult_expr(text, pos)
    pos = skip_whitespace(text, pos)

    while pos < len(text) and text[pos] in "+":
        op = text[pos]
        pos = skip_whitespace(text, pos + 1)
        right_value, pos = parse_mult_expr(text, pos)

        if op == "+":
            value += right_value

        pos = skip_whitespace(text, pos)

    return value, pos


def parse_expression(text: str, pos: int) -> tuple[int, int]:
    value, pos = parse_add_expr(text, pos)
    pos = skip_whitespace(text, pos)

    while pos < len(text) and text[pos] in "=>":
        op = text[pos]
        pos = skip_whitespace(text, pos + 1)
        right_value, pos = parse_term(text, pos)

        if op == ">":
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

        if text[pos:].startswith("}}"):
            return bool(value), pos + 2
        else:
            raise Exception("Invalid condition: expect }} got " + text[pos:])
    else:
        return parse_var_expr(text, pos)


def parse_if_expr(text: str, pos: int, values: dict) -> tuple[str, int]:
    if not text[pos:].startswith("{{#if"):
        raise Exception("Invalid if expression: expect {{#if got " + text[pos])

    pos += 5  # Skip {{#if
    pos = skip_whitespace(text, pos)
    condition_value, pos = parse_condition(text, pos)
    pos = skip_whitespace(text, pos)
    if text[pos:].startswith("}}"):
        pos += 2  # Skip }}
    else:
        raise Exception("Invalid if expression: expect }} got " + text[pos:])

    result = []
    if condition_value:
        template_text, pos = parse_template(text, pos, values)
        result.append(template_text)
    else:
        _, pos = parse_template(text, pos, values)

    if text[pos:].startswith("{{/if}}"):
        pos += 7  # Skip {{/if}}
        return "".join(result), pos

    raise Exception(
        "Invalid if expression: expect {{/if}} got: " + (text[pos:] if pos < len(text) else text[pos - 20 :])
    )


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


# template   ->
#             ( if_expr
#             | text
#             | keyword
#             )*
# if_expr    -> {{#if condition }} template {{/if}}
# condition  -> {{? expression }}
#             | var_expr
# expression -> add_expr comp_op term
# comp_op    -> > | =
# add_expr   -> mult_expr (add_op mult_expr)*
# add_op     -> +
# mult_expr  -> term (mult_op term)*
# mult_op    -> *
# term       -> '(' expression ')'
#             | var_expr
# var_expr   -> {{getglobalvar::var_id}}
#             | number
# keyword    -> {{char}}
#             | {{user}}
#             | {{slot}}


def compile_prompt(text: str, values: dict) -> str:
    try:
        result, _ = parse_template(text, 0, values)
        return result
    except Exception as e:
        print("Error parsing prompt:", e)
        return ""


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
        if "type" in prompt:
            if prompt["type"] == "description":
                values["slot"] = description
                text += compile_prompt(prompt["innerFormat"], values)
                text += "\n"
            elif prompt["type"] == "persona":
                values["slot"] = persona
                text += compile_prompt(prompt["innerFormat"], values)
                text += "\n"
            elif prompt["type"] == "plain":
                text += compile_prompt(prompt["text"], values)
                text += "\n"
            else:
                print("Unknown type: " + prompt["type"])
    print(text)
