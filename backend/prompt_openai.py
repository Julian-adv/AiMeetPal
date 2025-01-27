def make_openai_prompt(user, name, wiBefore, description, personality, scenario, wiAfter, persona, entries: list, start_index: int) -> list:
    messages = []
    
    for entry in entries[start_index:]:
        role = 'user' if entry.speaker == user else 'assistant'
        message = {
            'role': role,
            'content': entry.content
        }
        messages.append(message)
    
    return messages
