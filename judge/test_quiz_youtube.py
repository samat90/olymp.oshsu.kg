"""A YouTube video in a quiz question: reading links, the editor, the game."""
import json

from django.test import SimpleTestCase
from django.urls import reverse

from judge.models import QuizQuestion
from judge.test_quiz import Q, QuizGameTestCase, add_question, make_quiz, option_id
from judge.utils import youtube
from judge.utils.quiz_import import clean_question, problems, QuestionError

ID = 'dQw4w9WgXcQ'


class YouTubeLinkTest(SimpleTestCase):
    def test_accepted_links(self):
        cases = {
            'https://www.youtube.com/watch?v=%s' % ID: 0,
            'http://youtube.com/watch?list=PL1&v=%s&index=2' % ID: 0,
            'https://m.youtube.com/watch?v=%s&t=90' % ID: 90,
            'https://music.youtube.com/watch?v=%s&si=abc' % ID: 0,
            'https://youtu.be/%s' % ID: 0,
            'https://youtu.be/%s?si=xyz&t=1m30s' % ID: 90,
            'youtu.be/%s?t=45s' % ID: 45,
            'www.youtube.com/watch?v=%s&t=1h2m3s' % ID: 3723,
            'https://www.youtube.com/shorts/%s' % ID: 0,
            'https://www.youtube.com/shorts/%s?feature=share' % ID: 0,
            'https://www.youtube.com/embed/%s?start=15' % ID: 15,
            'https://www.youtube-nocookie.com/embed/%s' % ID: 0,
            'https://www.youtube.com/live/%s?t=7' % ID: 7,
            'https://www.youtube.com/v/%s' % ID: 0,
            'https://youtube.com/watch?v=%s#t=2m' % ID: 120,
            '  HTTPS://WWW.YOUTUBE.COM/watch?v=%s  ' % ID: 0,
        }
        for link, start in cases.items():
            self.assertEqual(youtube.parse(link), (ID, start), link)

    def test_rejected_links(self):
        for link in ('', 'просто текст', ID, 'https://vimeo.com/123456789', 'https://youtube.com/',
                     'https://youtube.com/watch?v=short', 'https://youtube.com/watch?v=%sx' % ID,
                     'https://youtube.com.evil.kg/watch?v=%s' % ID, 'https://evil.kg/youtu.be/%s' % ID,
                     'https://user@evil.kg/watch?v=%s' % ID, 'javascript:alert(1)//youtu.be/%s' % ID,
                     'ftp://youtu.be/%s' % ID, 'https://youtube.com/channel/%s' % ID,
                     'https://youtu.be/"><script>', 'https://[bad', 'x' * 600):
            self.assertIsNone(youtube.parse(link), link)

    def test_bad_start_time_is_ignored(self):
        for tail in ('t=abc', 't=-5', 't=', 't=99999999'):
            self.assertEqual(youtube.parse('https://youtu.be/%s?%s' % (ID, tail)), (ID, 0), tail)

    def test_canonical_link_reads_back(self):
        for start in (0, 90):
            self.assertEqual(youtube.parse(youtube.link(ID, start)), (ID, start))
        self.assertEqual(youtube.link('', 0), '')


class YouTubeQuestionCleanTest(SimpleTestCase):
    def payload(self, **kwargs):
        return dict({'type': 'single', 'text': 'Что играет?',
                     'options': [{'text': 'а', 'is_correct': True}, {'text': 'б'}]}, **kwargs)

    def test_only_the_id_and_start_are_kept(self):
        fields, _options = clean_question(self.payload(video='https://youtu.be/%s?t=12&si=track' % ID))
        self.assertEqual((fields['youtube_id'], fields['youtube_start']), (ID, 12))

    def test_no_video(self):
        for value in (None, '', '   '):
            fields, _options = clean_question(self.payload(video=value))
            self.assertEqual((fields['youtube_id'], fields['youtube_start']), ('', 0))

    def test_wrong_link_is_an_error_of_the_video_field(self):
        with self.assertRaises(QuestionError) as ctx:
            clean_question(self.payload(video='https://vimeo.com/1'))
        self.assertEqual(ctx.exception.field, 'video')

    def test_a_video_is_enough_as_the_question(self):
        fields, options = clean_question(self.payload(text='', video='youtu.be/%s' % ID))
        self.assertEqual(problems(fields, options, False), [])


class YouTubeEditorTest(QuizGameTestCase):
    def save(self, **extra):
        body = dict({'type': 'single', 'text': 'Что играет?',
                     'options': [{'text': 'а', 'is_correct': True}, {'text': 'б'}]}, **extra)
        return self.host.post(reverse('quiz_api_question_save', args=[self.quiz.key, self.q1.id]),
                              json.dumps(body), content_type='application/json')

    def test_save_preview_and_remove(self):
        response = self.save(video='https://www.youtube.com/shorts/%s' % ID)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['question']['video'], 'https://youtu.be/%s' % ID)
        preview = self.host.get(reverse('quiz_api_question_preview', args=[self.quiz.key, self.q1.id])).json()
        self.assertEqual(preview['question']['video'], {'id': ID, 'start': 0})
        self.assertEqual(self.save(video='').json()['question']['video'], '')
        self.q1.refresh_from_db()
        self.assertEqual(self.q1.youtube_id, '')

    def test_wrong_link_changes_nothing(self):
        self.save(video='youtu.be/%s?t=5' % ID)
        response = self.save(video='https://example.com/video', text='другой')
        self.assertEqual((response.status_code, response.json()['field']), (400, 'video'))
        self.q1.refresh_from_db()
        self.assertEqual((self.q1.youtube_id, self.q1.youtube_start, self.q1.text), (ID, 5, 'Что играет?'))

    def test_copy_and_duplicate_keep_the_video(self):
        QuizQuestion.objects.filter(id=self.q1.id).update(youtube_id=ID, youtube_start=30)
        self.host.post(reverse('quiz_api_question_duplicate', args=[self.quiz.key, self.q1.id]))
        self.assertEqual(self.quiz.questions.filter(youtube_id=ID, youtube_start=30).count(), 2)
        self.login(self.other).post(reverse('quiz_copy', args=[self.quiz.key]))
        self.assertEqual(QuizQuestion.objects.filter(quiz__author=self.other.profile, youtube_id=ID).count(), 2)

    def test_quiz_page_marks_the_question_without_showing_the_video(self):
        QuizQuestion.objects.filter(id=self.q1.id).update(youtube_id=ID)
        page = self.host.get(reverse('quiz_detail', args=[self.quiz.key])).content.decode()
        self.assertIn('fa-youtube-play', page)
        self.assertNotIn(ID, page)


class YouTubeGameTest(QuizGameTestCase):
    def setUp(self):
        super().setUp()
        self.video_quiz = make_quiz(self.author, title='Клипы')
        self.q = add_question(self.video_quiz, Q.SINGLE, [('Да', True), ('Нет', False)], youtube_id=ID,
                              youtube_start=9)
        self.plain = add_question(self.video_quiz, Q.SINGLE, [('Да', True), ('Нет', False)])

    def test_players_and_host_get_only_id_and_start(self):
        pin, clients = self.game_with_players('Айбек', quiz=self.video_quiz)
        self.action(pin, 'start')
        for data in (self.question(clients[0], pin), self.state(clients[0], pin)['question'],
                     self.host.get(reverse('quiz_host_state', args=[pin])).json()['question']):
            self.assertEqual(data['video'], {'id': ID, 'start': 9})
        self.answer(clients[0], pin, 0, option_id(self.q, 'Да'))
        self.action(pin, 'next')
        self.action(pin, 'next')
        self.assertNotIn('video', self.question(clients[0], pin))

    def test_game_pages_do_not_load_youtube_by_themselves(self):
        pin, clients = self.game_with_players('Айбек', quiz=self.video_quiz)
        for page in (clients[0].get(reverse('quiz_play', args=[pin])), self.host.get(reverse('quiz_host', args=[pin]))):
            self.assertNotIn('youtube', page.content.decode())
