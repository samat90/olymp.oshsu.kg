"""Shows $...$ formulas of the statements as plain text (the site has no formula renderer).

The converter itself lives next to the training-set builder (problemsets/train2026/statement_math.py), which also
runs on the judge machine without the rest of the site; it is loaded from there.
"""
import importlib.util
import os

from django.conf import settings

_clean = None


def clean_math(text):
    global _clean
    if not text or '$' not in text:
        return text
    if _clean is None:
        path = os.path.join(settings.BASE_DIR, 'problemsets', 'train2026', 'statement_math.py')
        try:
            spec = importlib.util.spec_from_file_location('statement_math', path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            _clean = module.clean_math
        except Exception:
            _clean = lambda t: t  # noqa: E731
    return _clean(text)
