from typing import List
from pydantic import BaseModel

class ChatEntry(BaseModel):
    id: int
    speaker: str
    content: str
    token_count: int | None = None

class CharInfo(BaseModel):
    name: str
    description: str
    personality: str
    scenario: str
    mes_example: str

class ChatMessage(BaseModel):
    system_token_count: int
    info: CharInfo
    entries: List[ChatEntry]


def find_start_index(system_token_count: int, entries: List[ChatEntry], max_token_count: int, user: str) -> int:
    try:
        total_tokens = system_token_count
        for i in range(len(entries) - 1, -1, -1):
            entry = entries[i]
            if entry.token_count is not None:
                if total_tokens + entry.token_count > max_token_count:
                    # Find first non-user entry from i + 1
                    for j in range(i + 1, len(entries)):
                        if entries[j].speaker != user:
                            return j
                    return len(entries) - 1  # If no non-user entry found, return end of list
                total_tokens += entry.token_count
            
        return 0
    except Exception as e:
        print(f"Error finding start index: {e}")
        return 0