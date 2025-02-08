from chat_common import ChatEntry
from prompt_openai import find_prompt


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
