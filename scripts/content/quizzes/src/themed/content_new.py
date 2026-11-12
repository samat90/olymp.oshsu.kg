"""New themed quizzes (sources n01.py … n08.py), added 2026-11."""
import importlib
QUIZZES = []
for name in ['n01', 'n02', 'n03', 'n04', 'n05', 'n06', 'n07', 'n08']:
    module = importlib.import_module(name)
    QUIZZES += [v for v in vars(module).values() if isinstance(v, dict) and 'questions' in v and 'key' in v]
