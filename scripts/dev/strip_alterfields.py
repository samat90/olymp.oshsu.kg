"""Remove AlterField operations from a generated migration.

makemigrations keeps proposing no-op AlterFields (choices and help texts that
differ between machines). Run this on a fresh migration to keep only real changes.
"""
import sys

path = sys.argv[1]
lines = open(path, encoding='utf-8').read().split('\n')
out = []
skip = False
for line in lines:
    if line == '        migrations.AlterField(':
        skip = True
        continue
    if skip:
        if line == '        ),':
            skip = False
        continue
    out.append(line)
text = '\n'.join(out)
if 'judge.models.problem' not in text.split('class Migration')[1]:
    text = text.replace('import judge.models.problem\n', '')
open(path, 'w', encoding='utf-8', newline='\n').write(text)
