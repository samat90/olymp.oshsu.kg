import glob
import os
import re

from django.conf import settings
from django.test import SimpleTestCase, override_settings
from django.utils import translation

from judge.utils.quiz_i18n import JS_STRINGS, js_catalog

CALL = re.compile(r"\bL\('((?:[^'\\]|\\.)*)'\)")


# On the site Russian is the main language, so a Russian page falls back to the msgids.
@override_settings(LANGUAGE_CODE='ru')
class QuizScriptStringsTest(SimpleTestCase):
    def test_every_script_string_is_listed(self):
        found = set()
        for path in glob.glob(os.path.join(settings.BASE_DIR, 'resources', 'quiz', '*.js')):
            with open(path, encoding='utf-8') as f:
                found.update(re.sub(r"\\(.)", r"\1", s) for s in CALL.findall(f.read()))
        self.assertTrue(found)
        self.assertEqual(sorted(found - set(JS_STRINGS)), [])
        self.assertEqual(sorted(set(JS_STRINGS) - found), [])

    def test_catalog_follows_the_language(self):
        with translation.override('ru'):
            self.assertEqual(js_catalog(), {})
        with translation.override('ky'):
            self.assertEqual(js_catalog().get('Ответить'), 'Жооп берүү')
        with translation.override('en'):
            self.assertEqual(js_catalog().get('Ответить'), 'Answer')
