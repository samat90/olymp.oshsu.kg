"""Add missing translations to the .po files and rebuild the .mo files.

    python scripts/dev/add_translations.py scripts/dev/translations.json

The JSON maps an English msgid to {"ru": "...", "ky": "..."}. New entries are
appended to the end of each .po file; existing entries are left alone.
"""
import json
import os
import sys

from babel.messages.mofile import write_mo
from babel.messages.pofile import read_po

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def po_escape(text):
    return text.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')


def main(path):
    with open(path, encoding='utf-8') as f:
        table = json.load(f)
    for lang in ('ru', 'ky'):
        po_path = os.path.join(ROOT, 'locale', lang, 'LC_MESSAGES', 'django.po')
        with open(po_path, 'rb') as f:
            catalog = read_po(f)
        entries = []
        for msgid, values in table.items():
            text = values.get(lang) or values.get('ru')
            if not text or msgid in catalog:
                continue
            entries.append('\nmsgid "%s"\nmsgstr "%s"\n' % (po_escape(msgid), po_escape(text)))
        if entries:
            with open(po_path, 'a', encoding='utf-8', newline='\n') as f:
                f.write(''.join(entries))
        with open(po_path, 'rb') as f:
            catalog = read_po(f)
        with open(po_path[:-3] + '.mo', 'wb') as f:
            write_mo(f, catalog)
        print(lang, 'added', len(entries))


if __name__ == '__main__':
    main(sys.argv[1])
