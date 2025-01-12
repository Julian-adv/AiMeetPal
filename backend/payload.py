INFERMATICAI_KEYS = [
    'model',
    'prompt',
    'max_tokens',
    'temperature',
    'top_p',
    'top_k',
    'repetition_penalty',
    'stream',
    'stop',
    'presence_penalty',
    'frequency_penalty',
    'min_p',
    'seed',
    'ignore_eos',
    'n',
    'best_of',
    'min_tokens',
    'spaces_between_special_tokens',
    'skip_special_tokens',
    'logprobs',
]

def make_payload(prompt: str, settings: dict, preset: dict, stream: bool = True) -> dict:
    payload = {
        **preset,
        "prompt": prompt,
        "model": settings["model"],
        "max_tokens": settings["max_tokens"],
        "stream": stream,
    }
    # Filter preset to only include keys in INFERMATICAI_KEYS
    filtered_preset = {k: v for k, v in payload.items() if k in INFERMATICAI_KEYS}
    
    return filtered_preset
