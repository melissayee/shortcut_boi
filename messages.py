from typing import List

from models import KeyboardShortcut, Parameter


def parse_parameters(parameters: str) -> List[Parameter]:
    pass


def build_single_shortcut_response(shortcut: KeyboardShortcut) -> List[dict]:
    formatted_text = f'*Type: * {shortcut.category_description}\n' \
                     f'*Command:* {shortcut.command}\n' \
                     f'*Result:* {shortcut.description}'

    blocks = [{
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": formatted_text,
        },
    }]
    return blocks
