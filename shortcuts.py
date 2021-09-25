import re

import bs4.element
import requests
import random
import string
import unicodedata

from bs4 import BeautifulSoup
from typing import List

from models import System, KeyboardShortcut

MAC_ALIAS = ['mac', 'm', 'macos', 'apple']
MAC_SHORTCUTS_LINK = 'https://support.apple.com/en-us/HT201236'
MAC_SHORTCUT_CATEGORIES = {'copy': 'Cut, copy, paste, and other common shortcuts',
                           'sleep': 'Sleep, log out, and shut down shortcuts',
                           'finder': 'Finder and system shortcuts',
                           'text': "Document shortcuts. The behavior of these shortcuts may vary with the app you're using."}

WIN_ALIAS = ['win', 'w', 'windows', 'microsoft']
WIN_SHORTCUTS_LINK = 'https://support.microsoft.com/en-us/windows/keyboard-shortcuts-in-windows-dcc61a57-8ff0-cffe-9796-cb9706c75eec'
WIN_SHORTCUT_CATEGORIES = {'copy': 'Copy, paste, and other general keyboard shortcuts',
                           'windows': 'Windows logo key keyboard shortcuts',
                           'command': 'Command Prompt keyboard shortcuts',
                           'dialog': 'Dialog box keyboard shortcuts',
                           'file': 'File Explorer keyboard shortcuts',
                           'virtual': 'Virtual desktops keyboard shortcuts',
                           'taskbar': 'Taskbar keyboard shortcuts',
                           'settings': 'Settings keyboard shortcuts'}


def remove_extra_whitespace(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()


def parse_unicode(text: str) -> str:
    return unicodedata.normalize('NFKD', text).strip()


def get_tag_text_only(element: bs4.element) -> str:
    text = []
    for item in element.children:
        if isinstance(item, bs4.element.NavigableString):
            text.append(item)
    return ' '.join(text)


def get_all_shortcuts_by_system(system: System) -> List[KeyboardShortcut]:
    all_shortcuts = []
    if system == System.MAC:
        r = requests.get(MAC_SHORTCUTS_LINK)
        command_headers = BeautifulSoup(r.content, features='html.parser').find('div',
                                                                                {'id': 'sections'}).find_all('h2')
        command_sections = [header.parent for header in command_headers]

        for section in command_sections:
            section_name = section.find('h2').get('id')
            if section_name in MAC_SHORTCUT_CATEGORIES:
                command_list = section.find_all('li')
                for command in command_list:
                    if command.strong is not None:
                        full_text = command.text.split(':')
                        shortcut_command = parse_unicode(full_text[0])
                        command_description = remove_extra_whitespace(parse_unicode(full_text[1]))
                        all_shortcuts.append(KeyboardShortcut(category=section_name,
                                                              command=shortcut_command,
                                                              description=command_description))
    elif system == System.WINDOWS:
        r = requests.get(WIN_SHORTCUTS_LINK)
        commands_sections = BeautifulSoup(r.content, features='html.parser').find('div', {
            'id': 'ID0EBD-supTabControlContent-1'}).find_all('section', {'class': 'ocpSection'})
        for section in commands_sections:
            section_name = section['aria-label'].split(' ')[0].lower().strip(string.punctuation + ' ')
            if section_name in WIN_SHORTCUT_CATEGORIES:
                table_rows = section.find('tbody').find_all('tr')
                for row in table_rows:
                    cols = row.find_all('td')
                    shortcut_command = cols[0].text
                    command_description = cols[1].text
                    all_shortcuts.append(KeyboardShortcut(category=section_name,
                                                          command=remove_extra_whitespace(shortcut_command),
                                                          description=remove_extra_whitespace(command_description)))
    return all_shortcuts


def select_shortcut_from_list(all_shortcuts, system):
    shortcut = random.choice(all_shortcuts)
    if system == System.MAC:
        shortcut.category_description = MAC_SHORTCUT_CATEGORIES[shortcut.category]
    elif system == System.WINDOWS:
        shortcut.category_description = WIN_SHORTCUT_CATEGORIES[shortcut.category]
    elif system == System.BOT:
        pass
    return shortcut


def get_random_shortcut(system: System) -> KeyboardShortcut:
    all_shortcuts = get_all_shortcuts_by_system(system)
    return select_shortcut_from_list(all_shortcuts, system)


def get_random_shortcut_by_category(system: System, category: str) -> KeyboardShortcut:
    all_shortcuts = get_all_shortcuts_by_system(system)
    category_dict = {}

    if system == System.MAC:
        category_dict = MAC_SHORTCUT_CATEGORIES
    elif system == System.WINDOWS:
        category_dict = WIN_SHORTCUT_CATEGORIES

    if category in category_dict:
        shortcuts_in_category = [s for s in all_shortcuts if s.category == category]
        shortcut = select_shortcut_from_list(shortcuts_in_category, system)
    else:
        shortcut = select_shortcut_from_list(all_shortcuts, system)

    return shortcut
