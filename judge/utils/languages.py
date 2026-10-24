from judge.models import Language

# Kept only for old submissions: new problems and the compiler use .NET C# and Java 21 instead.
LEGACY_LANGUAGES = ('MONOCS', 'JAVA8')
# Programs in these languages are files, not text: no code editor for them.
EDITOR_EXCLUDED = ('SB3',)


def problem_languages():
    """Languages every problem allows: all of them except the legacy runtimes."""
    return Language.objects.exclude(key__in=LEGACY_LANGUAGES)
