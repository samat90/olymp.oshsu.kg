from judge.models import Language

# Kept only for old submissions: new problems and the compiler use .NET C# and Java 21 instead.
LEGACY_LANGUAGES = ('MONOCS', 'JAVA8')
# Programs in these languages are project files, not text: the editors upload them
# and keep them base64-encoded (Scratch 3: .sb3).
FILE_LANGUAGES = ('SB3',)
# Code is at most 64 KB; a project may be bigger (256 KB of base64 is about 190 KB of .sb3).
MAX_SOURCE = 65536
MAX_PROJECT = 262144


def problem_languages():
    """Languages every problem allows: all of them except the legacy runtimes."""
    return Language.objects.exclude(key__in=LEGACY_LANGUAGES)
