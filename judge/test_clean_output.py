from django.test import SimpleTestCase

from judge.utils.clean_output import clean


class CleanOutputTest(SimpleTestCase):
    def test_python_traceback_keeps_the_error_but_not_the_sandbox(self):
        text = ('Traceback (most recent call last):\n'
                '  File "/tmp/tmp8ai6qfxa/-loader.py", line 5, in <module>\n'
                "    runpy.run_path(sys.argv[0], run_name='__main__')\n"
                '  File "<frozen runpy>", line 286, in run_path\n'
                '  File "/tmp/tmp8ai6qfxa/main.py", line 2, in <module>\n'
                '    x=1/0\n'
                'ZeroDivisionError: division by zero\n')
        self.assertEqual(clean(text), 'Traceback (most recent call last):\n'
                                      '  File "main.py", line 2, in <module>\n'
                                      '    x=1/0\n'
                                      'ZeroDivisionError: division by zero\n')

    def test_compiler_error_and_internal_names(self):
        self.assertEqual(clean('/tmp/tmpab12/maincpp.cpp:1:13: error: x was not declared'),
                         'main.cpp:1:13: error: x was not declared')
        self.assertEqual(clean('\t/tmp/tmppifzppso/main.go:2 +0x14'), '\tmain.go:2 +0x14')

    def test_plain_text_is_left_alone(self):
        self.assertEqual(clean('ratio 3/4, a/b'), 'ratio 3/4, a/b')

    def test_colored_gcc_output(self):
        self.assertEqual(clean('\x1b[01m\x1b[Kmaincpp.cpp:1:13:\x1b[m\x1b[K error'),
                         '\x1b[01m\x1b[Kmain.cpp:1:13:\x1b[m\x1b[K error')

    def test_kotlin_jansi_lock_notice_is_dropped(self):
        self.assertEqual(clean('jansi-2.4.0-9340af9629fa45e0-libjansi.so.lck (Permission denied)\r\n'), '')
        self.assertEqual(clean('warning: x\n/tmp/jansi-2.4.0-9340af9629fa45e0-libjansi.so.lck (Permission denied)\n'
                               'main.kt:1:1: error'), 'warning: x\nmain.kt:1:1: error')
