import settings
from pybars import Compiler
import html

def make_prompt(user: str, char: str, wiBefore: str, description: str, personality: str, scenario: str, wiAfter: str, persona: str, entries: list, start_index: int) -> str:
    preset = settings.load_preset()
    context = settings.load_context()
    instruct = settings.load_instruct()

    # Initialize Handlebars compiler
    compiler = Compiler()
    
    # Compile the story template
    template = compiler.compile(context["story_string"] + context["chat_start"] + '\n' + instruct["first_output_sequence"])
    
    # Prepare context data with rendered system_prompt
    template_data = {
        "system": instruct["system_prompt"],
        "wiBefore": wiBefore,
        "description": description,
        "personality": personality,
        "scenario": scenario,
        "wiAfter": wiAfter,
        "persona": persona,
        "user": user,
        "char": char
    }
    
    # Render the story
    story_string = template(template_data)

    template = compiler.compile(story_string)
    story_string = template(template_data)

    story_string = html.unescape(story_string)

    story_string += entries[start_index].content + instruct["output_suffix"]
    for entry in entries[start_index + 1:]:
        if entry.speaker == user:
            story_string += instruct["input_sequence"] + entry.content + instruct["input_suffix"]
        else:
            story_string += instruct["output_sequence"] + entry.content + instruct["output_suffix"]
    story_string += instruct["last_output_sequence"]
    return story_string

def make_prompt_single(user: str, entry: list) -> str:
    instruct = settings.load_instruct()
    if entry.speaker == user:
        return instruct["input_sequence"] + entry.content + instruct["input_suffix"]
    else:
        return instruct["output_sequence"] + entry.content + instruct["output_suffix"]