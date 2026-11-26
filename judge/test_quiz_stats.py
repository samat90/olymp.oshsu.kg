"""Quiz statistics: which games count, the stored counters, the backfill and the pages that show them."""
from importlib import import_module

from django.apps import apps
from django.core.cache import cache
from django.test import Client
from django.urls import reverse

from judge.models import GameSession, Quiz, QuizPlayer
from judge.test_quiz import Q, QuizGameTestCase, add_question, make_quiz, option_id
from judge.utils import quiz_stats
from judge.views.quiz import GUEST_COOKIE

COUNTERS = ('plays', 'hosted_plays', 'solo_plays', 'participations', 'hosted_participations', 'unique_players',
            'answers_counted', 'answers_correct')


class StatsTestCase(QuizGameTestCase):
    def play(self, answers, mode='screen', quiz=None):
        """A finished hosted game. answers: {nickname: [text chosen for question 1, 2, ... or None]}."""
        quiz = quiz or self.quiz
        pin, clients = self.game_with_players(*answers, mode=mode, quiz=quiz)
        self.action(pin, 'start')
        questions = list(quiz.questions.order_by('order', 'id'))
        for index, question in enumerate(questions):
            for client, nickname in zip(clients, answers):
                given = answers[nickname]
                if index < len(given) and given[index] is not None:
                    self.t += 1
                    self.answer(client, pin, index, option_id(question, given[index]))
            if self.phase(pin) == 'question':
                self.action(pin, 'skip')
            if index + 1 < len(questions):
                self.action(pin, 'next')   # leaderboard
                self.action(pin, 'next')   # next question
        self.action(pin, 'end')
        return pin

    def play_solo(self, client=None, answer=True, nickname='Алмаз'):
        client = client or Client()
        data = {} if '_auth_user_id' in client.session else {'nickname': nickname}
        response = client.post(reverse('quiz_solo', args=[self.quiz.key]), data)
        self.assertEqual(response.status_code, 302)
        pin = response['Location'].rstrip('/').split('/')[-1]
        client.post(reverse('quiz_solo_next', args=[pin]))
        for index, question in enumerate([self.q1, self.q2]):
            if answer:
                self.t += 1
                self.assertEqual(self.answer(client, pin, index, option_id(
                    question, question.options.get(is_correct=True).text)).status_code, 200)
            else:
                self.t += 100
                self.state(client, pin)
            client.post(reverse('quiz_solo_next', args=[pin]))
        self.assertEqual(self.game(pin).status, GameSession.FINISHED)
        return client

    def counters(self, quiz=None):
        quiz = Quiz.objects.get(id=(quiz or self.quiz).id)
        return {name: getattr(quiz, name) for name in COUNTERS}


class QuizStatsCountTest(StatsTestCase):
    def test_finished_hosted_game_is_counted(self):
        self.play({'Айбек': ['Два', 'Нет'], 'Бегимай': ['Три', 'Да']})
        self.assertEqual(self.counters(), {
            'plays': 1, 'hosted_plays': 1, 'solo_plays': 0, 'participations': 2, 'hosted_participations': 2,
            'unique_players': 2, 'answers_counted': 4, 'answers_correct': 2})
        self.assertIsNotNone(Quiz.objects.get(id=self.quiz.id).last_played)

    def test_hosted_and_solo_are_counted_apart(self):
        self.play({'Айбек': ['Два', 'Да'], 'Бегимай': ['Два', 'Да']}, mode='auto')
        self.play_solo()
        got = self.counters()
        self.assertEqual((got['hosted_plays'], got['solo_plays'], got['plays']), (1, 1, 2))
        self.assertEqual((got['participations'], got['hosted_participations']), (3, 2))

    def test_game_without_answers_is_not_counted(self):
        pin, _clients = self.game_with_players('Айбек')
        self.action(pin, 'start')
        self.action(pin, 'end')
        self.assertEqual(self.counters()['plays'], 0)
        self.assertIsNone(Quiz.objects.get(id=self.quiz.id).last_played)

    def test_cancelled_lobby_and_unfinished_games_are_not_counted(self):
        pin = self.launch()
        self.action(pin, 'end')
        pin, clients = self.game_with_players('Айбек')
        self.action(pin, 'start')
        self.answer(clients[0], pin, 0, option_id(self.q1, 'Два'))
        quiz_stats.recount(self.quiz.id)
        self.assertEqual(self.counters()['plays'], 0)

    def test_players_who_never_answered_or_were_removed_do_not_count(self):
        pin, clients = self.game_with_players('Айбек', 'Молчун', 'Лишний')
        self.action(pin, 'start')
        self.answer(clients[0], pin, 0, option_id(self.q1, 'Два'))
        self.answer(clients[2], pin, 0, option_id(self.q1, 'Два'))
        self.action(pin, 'kick', player=self.player(pin, 'Лишний').id)
        self.action(pin, 'end')
        got = self.counters()
        self.assertEqual((got['participations'], got['unique_players'], got['answers_counted']), (1, 1, 1))

    def test_the_same_user_and_the_same_guest_are_one_player(self):
        user = self.login(self.student)
        self.play_solo(user)
        self.play_solo(user)
        guest = Client()
        self.play_solo(guest)
        self.play_solo(guest)
        got = self.counters()
        self.assertEqual((got['solo_plays'], got['participations'], got['unique_players']), (4, 4, 2))
        self.assertIn(GUEST_COOKIE, guest.cookies)

    def test_unscored_questions_do_not_lower_the_share_of_correct_answers(self):
        poll = add_question(self.quiz, Q.POLL, [('Кошки', False), ('Собаки', False)])
        self.play({'Айбек': ['Два', 'Да', 'Кошки']})
        got = self.counters()
        self.assertEqual((got['answers_counted'], got['answers_correct']), (2, 2))
        # The same after the poll is deleted: its type comes from the snapshot of the game.
        poll.delete()
        quiz_stats.recount(self.quiz.id)
        self.assertEqual(self.counters()['answers_counted'], 2)

    def test_deleting_a_game_recounts(self):
        pin = self.play({'Айбек': ['Два', 'Да']})
        with self.captureOnCommitCallbacks(execute=True):
            self.game(pin).delete()
        self.assertEqual(self.counters()['plays'], 0)

    def test_recount_keeps_the_updated_time(self):
        before = Quiz.objects.get(id=self.quiz.id).updated
        self.play({'Айбек': ['Два', 'Да']})
        self.assertEqual(Quiz.objects.get(id=self.quiz.id).updated, before)

    def test_saving_settings_does_not_overwrite_counters(self):
        self.play({'Айбек': ['Два', 'Да']})
        response = self.host.post(reverse('quiz_api_save', args=[self.quiz.key]), '{"title": "Новое"}',
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.counters()['plays'], 1)

    def test_a_failing_recount_does_not_break_the_finish(self):
        from unittest.mock import patch
        with patch.object(quiz_stats, 'recount', side_effect=RuntimeError('boom')), \
                self.assertLogs('judge.quiz', 'ERROR'):
            pin = self.play({'Айбек': ['Два', 'Да']})
        self.assertEqual(self.game(pin).status, GameSession.FINISHED)

    def test_backfill_migration_counts_games_already_played(self):
        self.play({'Айбек': ['Два', 'Нет'], 'Бегимай': ['Два', 'Да']})
        expected = self.counters()
        Quiz.objects.filter(id=self.quiz.id).update(last_played=None, **{name: 0 for name in COUNTERS})
        # A counter left over from the old rule ("every finished game") is corrected too.
        empty = make_quiz(self.author, title='Пустая')
        Quiz.objects.filter(id=empty.id).update(plays=5)
        players = QuizPlayer.objects.count()
        import_module('judge.migrations.0192_quiz_stats_video').backfill(apps, None)
        self.assertEqual(self.counters(), expected)
        self.assertEqual(self.counters(empty)['plays'], 0)
        self.assertEqual(QuizPlayer.objects.count(), players)


class QuizStatsDetailTest(StatsTestCase):
    def test_summary(self):
        self.play({'Айбек': ['Два', 'Нет'], 'Бегимай': ['Два', 'Да'], 'Данияр': ['Три', None]})
        self.play({'Эрмек': ['Два', 'Да']})
        quiz = Quiz.objects.get(id=self.quiz.id)
        self.assertEqual(quiz.average_group, 2)
        self.assertEqual(quiz.correct_percent, 71)   # 5 of 7 answers
        detail = quiz_stats.detail(quiz)
        self.assertEqual(detail['questions'][self.q1.id], {'answered': 4, 'correct': 3, 'percent': 75})
        self.assertEqual(detail['questions'][self.q2.id], {'answered': 3, 'correct': 2, 'percent': 67})
        self.assertIn(detail['best']['nickname'], ('Бегимай', 'Эрмек'))
        self.assertGreater(detail['best']['score'], 0)

    def test_nothing_played(self):
        quiz = Quiz.objects.get(id=self.quiz.id)
        self.assertIsNone(quiz.average_group)
        self.assertIsNone(quiz.correct_percent)
        self.assertEqual(quiz_stats.detail(quiz), {'best': None, 'questions': {}})

    def test_play_labels_agree_with_the_number(self):
        for n, label in ((1, 'Сыграна 1 раз'), (2, 'Сыграна 2 раза'), (5, 'Сыграна 5 раз'),
                         (12, 'Сыграна 12 раз'), (22, 'Сыграна 22 раза'), (101, 'Сыграна 101 раз')):
            self.assertEqual(Quiz(plays=n).plays_label, label)

    def test_catalog_badge_and_order(self):
        quiet = make_quiz(self.author, title='Новая тихая')
        add_question(quiet, Q.SINGLE, [('Да', True), ('Нет', False)])
        self.play({'Айбек': ['Два', 'Да']})
        cache.clear()
        page = Client().get(reverse('quiz_catalog') + '?order=popular').content.decode()
        self.assertIn('Сыграна 1 раз', page)
        self.assertLess(page.index('Столицы'), page.index('Новая тихая'))
        newest = Client().get(reverse('quiz_catalog')).content.decode()
        self.assertLess(newest.index('Новая тихая'), newest.index('Столицы'))

    def test_quiz_page_shows_the_statistics(self):
        page = Client().get(reverse('quiz_detail', args=[self.quiz.key])).content.decode()
        self.assertNotIn('qz-statbox', page)
        self.play({'Айбек': ['Два', 'Нет'], 'Бегимай': ['Два', 'Да']})
        page = Client().get(reverse('quiz_detail', args=[self.quiz.key])).content.decode()
        for text in ('qz-statbox', 'С ведущим', 'Средняя группа', 'Верных ответов', '75%', 'Лучший результат',
                     'верно 100%', 'верно 50%'):
            self.assertIn(text, page)

    def test_my_quizzes_show_the_statistics(self):
        self.play({'Айбек': ['Два', 'Да'], 'Бегимай': ['Два', 'Да']})
        page = self.host.get(reverse('quiz_my')).content.decode()
        for text in ('Сыграна 1 раз', 'игроков: 2', 'верно 100%'):
            self.assertIn(text, page)
