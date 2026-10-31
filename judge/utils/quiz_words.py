"""A short filter for rude nicknames in quiz games (Russian, Kyrgyz, English roots)."""
import re

ROOTS = (
    'хуй', 'хуе', 'хуё', 'хуи', 'пизд', 'ебан', 'ебат', 'ёбан', 'ебл', 'бляд', 'блят', 'бля', 'сука', 'суки',
    'мудак', 'мудил', 'пидор', 'пидар', 'гандон', 'залуп', 'шлюх', 'дроч',
    'сигил', 'сикей', 'сиктир', 'котон', 'шерменде',
    'fuck', 'shit', 'bitch', 'cunt', 'dick', 'pussy', 'whore', 'nigg', 'fag', 'porn', 'sex',
)
LOOKALIKE = str.maketrans({'a': 'а', 'e': 'е', 'o': 'о', 'p': 'р', 'c': 'с', 'y': 'у', 'x': 'х', 'k': 'к',
                           'm': 'м', 'b': 'б', '3': 'з', '0': 'о', '@': 'а', '6': 'б', 'ё': 'е'})


def is_rude(nick):
    plain = re.sub(r'[\s._\-*]+', '', nick.casefold())
    if any(root in plain for root in ROOTS):
        return True
    cyrillic = plain.translate(LOOKALIKE)
    return any(root in cyrillic for root in ROOTS)
