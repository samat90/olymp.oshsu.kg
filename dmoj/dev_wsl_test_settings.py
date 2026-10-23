"""Settings for running the test suite in WSL.

The upstream DMOJ tests expect English messages and free-form problem codes.
"""
from dmoj.dev_wsl_settings import *  # noqa: F401, F403

LANGUAGE_CODE = 'en'
DMOJ_NUMERIC_PROBLEM_CODES = False
