from judge.models import Language

# Kept only for old submissions; new problems and the compiler use modern C# (.NET) instead.
LEGACY_LANGUAGES = ('MONOCS',)


def problem_languages():
    """Languages every problem allows: all of them except the legacy runtimes."""
    return Language.objects.exclude(key__in=LEGACY_LANGUAGES)
