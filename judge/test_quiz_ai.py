import json
from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from judge.models import Quiz, QuizQuestion as Q
from judge.models.tests.util import create_user
from judge.utils import quiz_ai
from judge.views import quiz_editor

ANSWER = {
    'title': 'Горы Кыргызстана', 'description': 'Про вершины и перевалы.', 'subject': 'География',
    'questions': [
        {'type': 'single', 'text': 'Самая высокая вершина Кыргызстана?', 'weight': 2, 'explanation': 'Пик Жеңиш.',
         'options': [{'text': 'Пик Жеңиш', 'correct': True}, {'text': 'Пик Ленина', 'correct': False},
                     {'text': 'Хан-Тенгри', 'correct': False}, {'text': 'Сулайман-Тоо', 'correct': False}]},
        {'type': 'truefalse', 'text': 'Иссык-Куль замерзает зимой.', 'answer': False, 'weight': 0},
        {'type': 'multi', 'text': 'Какие города стоят в Ферганской долине?',
         'options': [{'text': 'Ош', 'correct': True}, {'text': 'Жалал-Абад', 'correct': True},
                     {'text': 'Нарын', 'correct': False}, {'text': 'Каракол', 'correct': False}]},
        {'type': 'order', 'text': 'Расставьте по высоте, от низкой', 'options': [
            {'text': 'Сулайман-Тоо'}, {'text': 'Ала-Арча'}, {'text': 'Пик Ленина'}]},
        {'type': 'text', 'text': 'Столица Кыргызстана?', 'answers': ['Бишкек']},
        {'type': 'slider', 'text': 'Высота пика Ленина, м', 'min': 6000, 'max': 8000, 'step': 1, 'answer': 7134,
         'tolerance': 50, 'unit': 'м'},
        {'type': 'word', 'text': 'Озеро в Нарынской области', 'word': 'Сон-Куль'},
        {'type': 'code', 'text': 'Что выведет?', 'code': 'print(2 ** 3)', 'language': 'Python',
         'options': [{'text': '8', 'correct': True}, {'text': '6', 'correct': False}]},
        # broken: dropped
        {'type': 'single', 'text': 'Нет верного', 'options': [{'text': 'а'}, {'text': 'б'}]},
        {'type': 'multi', 'text': 'Все верные',
         'options': [{'text': 'а', 'correct': True}, {'text': 'б', 'correct': True}]},
        {'type': 'pin', 'text': 'Где Ош?'},
        {'type': 'single', 'text': 'Самая высокая вершина Кыргызстана?', 'options': [
            {'text': 'а', 'correct': True}, {'text': 'б'}]},
        'junk',
    ],
}


class QuizAIParseTest(TestCase):
    def test_json_inside_markdown(self):
        data = quiz_ai.parse_json('Вот:\n```json\n{"questions": []}\n```')
        self.assertEqual(data, {'questions': []})
        with self.assertRaises(quiz_ai.AIError):
            quiz_ai.parse_json('нет json')

    @override_settings(QUIZ_AI_GEMINI_KEY='g')
    def test_good_questions_kept_broken_dropped(self):
        with patch.object(quiz_ai, 'ask_gemini', return_value=json.dumps(ANSWER)):
            result = quiz_ai.generate('Горы', '', 10, 'ru', 'hard')
        types = [fields['type'] for fields, _options in result['questions']]
        self.assertEqual(types, ['single', 'truefalse', 'multi', 'order', 'text', 'slider', 'word', 'code'])
        self.assertEqual(result['title'], 'Горы Кыргызстана')
        by_type = {fields['type']: (fields, options) for fields, options in result['questions']}
        self.assertEqual(by_type['word'][0]['data']['word'], 'СОН-КУЛЬ')
        self.assertEqual(by_type['code'][0]['code_language'], 'python')
        self.assertEqual([o['text'] for o in by_type['order'][1]], ['Сулайман-Тоо', 'Ала-Арча', 'Пик Ленина'])
        self.assertEqual([o['is_correct'] for o in by_type['truefalse'][1]], [False, True])
        self.assertEqual(by_type['single'][0]['weight'], 2)
        self.assertEqual(by_type['truefalse'][0]['weight'], 0)

    @override_settings(QUIZ_AI_GEMINI_KEY='g', QUIZ_AI_GROQ_KEY='q')
    def test_groq_takes_over_when_gemini_fails(self):
        with patch.object(quiz_ai, 'ask_gemini', side_effect=quiz_ai.AIError('HTTP 500')), \
                patch.object(quiz_ai, 'ask_groq', return_value=json.dumps(ANSWER)) as groq:
            result = quiz_ai.generate('Горы', '', 5, 'ky', 'easy')
        self.assertTrue(groq.called)
        self.assertEqual(len(result['questions']), 5)

    @override_settings(QUIZ_AI_GEMINI_KEY='', QUIZ_AI_GROQ_KEY='')
    def test_not_configured(self):
        self.assertFalse(quiz_ai.is_configured())
        with self.assertRaises(quiz_ai.AIError):
            quiz_ai.generate('Горы', '', 5, 'ru', 'easy')


class SyncThread:
    def __init__(self, target, args, daemon):
        self.target, self.args = target, args

    def start(self):
        # In the test the job runs in the test's own thread and transaction: keep its connection open.
        with patch.object(quiz_editor, 'close_old_connections'):
            self.target(*self.args)


@override_settings(QUIZ_AI_GEMINI_KEY='g')
class QuizAIViewTest(TestCase):
    def setUp(self):
        cache.clear()
        self.user = create_user(username='ai_author')
        self.client.force_login(self.user)

    def start(self, **body):
        body.setdefault('topic', 'Горы Кыргызстана')
        return self.client.post(reverse('quiz_ai_start'), json.dumps(body), content_type='application/json')

    def test_generated_quiz_opens_in_the_editor_as_link_only(self):
        with patch.object(quiz_ai, 'ask_gemini', return_value=json.dumps(ANSWER)), \
                patch.object(quiz_editor.threading, 'Thread', SyncThread):
            response = self.start(count=10)
        self.assertEqual(response.status_code, 200, response.content)
        status = self.client.get(response.json()['status']).json()
        self.assertEqual(status['status'], 'done')
        quiz = Quiz.objects.get(author=self.user.profile)
        self.assertEqual(status['url'], reverse('quiz_edit', args=[quiz.key]))
        self.assertEqual(quiz.access, Quiz.LINK)
        self.assertEqual(quiz.title, 'Горы Кыргызстана')
        self.assertEqual(quiz.questions.count(), 8)
        self.assertEqual(self.client.get(status['url']).status_code, 200)
        single = quiz.questions.get(type=Q.SINGLE)
        self.assertEqual(single.options.filter(is_correct=True).get().text, 'Пик Жеңиш')

    def test_failure_is_reported(self):
        with patch.object(quiz_ai, 'ask_gemini', side_effect=quiz_ai.AIError('down')), \
                patch.object(quiz_editor.threading, 'Thread', SyncThread):
            response = self.start()
        status = self.client.get(response.json()['status']).json()
        self.assertEqual(status['status'], 'error')
        self.assertFalse(Quiz.objects.exists())

    def generate_times(self, times):
        with patch.object(quiz_ai, 'ask_gemini', return_value=json.dumps(ANSWER)), \
                patch.object(quiz_editor.threading, 'Thread', SyncThread):
            return [self.start().status_code for _i in range(times)]

    def test_topic_required_and_daily_limit(self):
        self.assertEqual(self.start(topic=' ').status_code, 400)
        # Three quizzes a day by default.
        self.assertEqual(self.generate_times(4), [200, 200, 200, 429])

    def test_unlimited_users(self):
        self.user.username = 'samat1'
        self.user.save()
        self.assertEqual(self.generate_times(4), [200] * 4)
        with self.settings(QUIZ_AI_UNLIMITED_USERS='teacher1, teacher2'):
            # samat1 is not on this list: its generations above were not counted, now the usual limit applies.
            self.assertEqual(self.generate_times(4), [200, 200, 200, 429])
            self.user.username = 'Teacher2'
            self.user.save()
            self.assertEqual(self.generate_times(1), [200])

    def test_author_questions_go_into_the_prompt(self):
        details = '1. Кто записал эпос?\n2. Сколько строк?\n3. Где Манас-Ордо?'
        sent = []
        with patch.object(quiz_ai, 'ask_gemini', side_effect=lambda key, model, system, prompt:
                          sent.append(prompt) or json.dumps(ANSWER)), \
                patch.object(quiz_editor.threading, 'Thread', SyncThread):
            self.assertEqual(self.start(details=details + 'x' * 6000, count=5).status_code, 200)
        self.assertIn('Описание и пожелания автора (может содержать готовые вопросы):\n' + details, sent[0])
        self.assertIn(quiz_ai.AUTHOR_RULE, sent[0])
        self.assertNotIn('x' * (quiz_ai.MAX_DETAILS + 1), sent[0])

    def test_someone_elses_job_is_not_shown(self):
        cache.set('qz:ai:job:abc', {'profile': 999999, 'status': 'done', 'key': 'x'}, 60)
        self.assertEqual(self.client.get(reverse('quiz_ai_status', args=['abc'])).json()['status'], 'error')

    def test_buttons_on_the_pages(self):
        for name in ('quiz_my', 'quiz_catalog'):
            html = self.client.get(reverse(name)).content.decode()
            self.assertIn('data-qz-ai', html)
            self.assertIn(reverse('quiz_new'), html)

    @override_settings(QUIZ_AI_GEMINI_KEY='')
    def test_not_configured_message(self):
        self.assertEqual(self.start().status_code, 503)
