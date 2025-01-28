from pybars import Compiler

def compile_prompt(text: str, user: str, char: str) -> str:
    compiler = Compiler()
    template = compiler.compile(text)
    template_data = {
        "user": user,
        "char": char
    }
    result = template(template_data)
    return result


def find_prompt(prompts: list, id: str, user, char) -> str:
    for prompt in prompts:
        if prompt["identifier"] == id:
            return prompt["role"], compile_prompt(prompt["content"], user, char)
    return "system",""


def append(messages: list, role: str, content: str, user, char):
    messages.append({
        'role': role,
        "content": compile_prompt(content, user, char)
    })

def make_openai_prompt(user, char, wiBefore, description, personality, scenario,
                       mes_example, wiAfter, persona, entries: list, start_index: int,
                       preset: dict) -> list:


    messages = []
    prompts = preset["prompts"]
    prompt_order = preset["prompt_order"][1]["order"]

    for order in prompt_order:
        if order["enabled"]:
            if (order["identifier"] == "main" or order["identifier"] == "nsfw" or
                order["identifier"] == "jailbreak"):
                role, content = find_prompt(prompts, order["identifier"], user, char)
                append(messages, role, content, user, char)
            elif order["identifier"] == "worldInfoBefore":
                append(messages, "system", wiBefore, user, char)
            elif order["identifier"] == "personaDescription":
                append(messages, "system", persona, user, char)
            elif order["identifier"] == "charDescription":
                append(messages, "system", description, user, char)
            elif order["identifier"] == "charPersonality":
                append(messages, "system", personality, user, char)
            elif order["identifier"] == "scenario":
                append(messages, "system", scenario, user, char)
            elif order["identifier"] == "worldInfoAfter":
                append(messages, "system", wiAfter, user, char)
            elif order["identifier"] == "dialogueExamples":
                append(messages, "system", mes_example, user, char)

    for entry in entries[start_index:]:
        role = 'user' if entry.speaker == user else 'assistant'
        message = {
            'role': role,
            'content': entry.content
        }
        messages.append(message)
    
    return messages
