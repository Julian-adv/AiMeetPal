from chat_common import ChatEntry
from prompt_openai import find_prompt
from prompt_googleai_risu import compile_prompt


def calc_index(index: int | str, start_index: int, length: int) -> int:
    if index == "end":
        return length
    if index == 0:
        return start_index
    if index < 0:
        return length + index
    return index


def append_upto(contents: list[dict], text_acc: list[str]) -> list[str]:
    text = "".join(text_acc)
    contents.append({"role": "user", "parts": [{"text": text}]})
    return []


def merge_contents(contents: list[dict]) -> list[dict]:
    if not contents:
        return contents

    merged = []
    current_role = contents[0]["role"]
    current_text = contents[0]["parts"][0]["text"]

    for content in contents[1:]:
        if content["role"] == current_role:
            current_text += content["parts"][0]["text"]
        else:
            merged.append({"role": current_role, "parts": [{"text": current_text}]})
            current_role = content["role"]
            current_text = content["parts"][0]["text"]

    merged.append({"role": current_role, "parts": [{"text": current_text}]})
    return merged


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
    entries: list[ChatEntry],
    start_index,
    preset,
) -> dict:
    system_prompt = []
    contents = []
    if "prompts" in preset:
        role, content = find_prompt(preset["prompts"], "main", user, name)
        system_prompt.append(content)
        system_prompt.append(persona)
        system_prompt.append(personality)
        system_prompt.append(description)
        role, content = find_prompt(preset["prompts"], "nsfw", user, name)
        system_prompt.append("[Start a new Chat]")
        text = "\n\n".join(system_prompt)

        return {
            "contents": [
                {"role": "user" if entry.speaker == user else "model", "parts": [{"text": entry.content}]}
                for entry in entries[start_index:]
            ],
            "systemInstruction": {"parts": [{"text": text}]},
        }
    elif "promptTemplate" in preset:
        values = {
            "user": user,
            "char": name,
            "slot": "",
        }
        first = True
        for prompt in preset["promptTemplate"]:
            if prompt["type"] == "plain":
                text = compile_prompt(prompt["text"], values)
                role = "model" if prompt["role"] == "bot" else "user"
                contents.append({"role": role, "parts": [{"text": text}]})
            elif prompt["type"] == "persona":
                values["slot"] = persona
                text = compile_prompt(prompt["innerFormat"], values)
                contents.append({"role": "user", "parts": [{"text": text}]})
            elif prompt["type"] == "description":
                values["slot"] = description
                text = compile_prompt(prompt["innerFormat"], values)
                contents.append({"role": "user", "parts": [{"text": text}]})
            elif prompt["type"] == "lorebook":
                pass
            elif prompt["type"] == "memory":
                pass
            elif prompt["type"] == "chat":
                start = calc_index(prompt["rangeStart"], start_index, len(entries))
                end = calc_index(prompt["rangeEnd"], start_index, len(entries))
                if first:
                    contents.append({"role": "user", "parts": [{"text": "[Start a new Chat]"}]})
                    first = False

                if start < end:
                    chats = [
                        {"role": "user" if entry.speaker == user else "model", "parts": [{"text": entry.content}]}
                        for entry in entries[start:end]
                    ]
                    contents.extend(chats)
                else:  # empty chat
                    contents.append({"role": "user", "parts": [{"text": "\n"}]})

        contents = merge_contents(contents)
        return {
            "contents": contents,
            "systemInstruction": {"parts": [{"text": ""}]},
        }
