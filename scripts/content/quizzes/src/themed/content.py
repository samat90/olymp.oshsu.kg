"""All themed quizzes (sources c01.py … c17.py and n01.py … n08.py), in catalogue order."""
import importlib
QUIZZES = []
for name in ['c01', 'c02', 'c03', 'c04', 'c05', 'c06', 'c07', 'c08', 'c09', 'c10', 'c11', 'c12', 'c13', 'c14', 'c15', 'c16', 'c17',
             'n01', 'n02', 'n03', 'n04', 'n05', 'n06', 'n07', 'n08', 'eda']:
    module = importlib.import_module(name)
    QUIZZES += [v for v in vars(module).values() if isinstance(v, dict) and 'questions' in v and 'key' in v]
