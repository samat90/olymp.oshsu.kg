import itertools
from datetime import timedelta
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from judge.models import Course, CourseAttempt, CourseBlock, CourseEnrollment, CourseLesson, CourseModule, \
    CourseOption, CourseProgress, CourseQuestion, CourseWork, MiscConfig, NavigationBar
from judge.models.course import youtube_id
from judge.models.tests.util import create_organization, create_problem, create_user
from judge.utils import course_logic as logic

KEYS = itertools.count(1)


def make_course(author, **kwargs):
    kwargs.setdefault('status', Course.PUBLISHED)
    kwargs.setdefault('title', 'Алгебра')
    return Course.objects.create(author=author.profile, key='c%07d' % next(KEYS), **kwargs)


def add_lesson(course, title='Урок', **kwargs):
    kwargs.setdefault('order', course.lessons.count())
    return CourseLesson.objects.create(course=course, title=title, **kwargs)


def add_block(lesson, type=CourseBlock.TEXT, **kwargs):
    return CourseBlock.objects.create(lesson=lesson, type=type, order=lesson.blocks.count(), **kwargs)


def add_test(lesson, **data):
    block = add_block(lesson, CourseBlock.TEST, data=data)
    single = CourseQuestion.objects.create(block=block, type=CourseQuestion.SINGLE, text='2+2?', points=2, order=0)
    for n, (text, ok) in enumerate([('3', False), ('4', True), ('5', False)]):
        CourseOption.objects.create(question=single, text=text, is_correct=ok, order=n)
    multi = CourseQuestion.objects.create(block=block, type=CourseQuestion.MULTI, text='Простые?', points=1, order=1)
    for n, (text, ok) in enumerate([('2', True), ('4', False), ('7', True)]):
        CourseOption.objects.create(question=multi, text=text, is_correct=ok, order=n)
    number = CourseQuestion.objects.create(block=block, type=CourseQuestion.NUMBER, text='Пи?', points=1, order=2)
    CourseOption.objects.create(question=number, text='3.14', is_correct=True)
    word = CourseQuestion.objects.create(block=block, type=CourseQuestion.TEXT, text='Столица?', points=1, order=3)
    CourseOption.objects.create(question=word, text='Бишкек', is_correct=True)
    return block


def right_answers(block):
    post = {}
    for q in block.questions.all():
        options = list(q.options.all())
        if q.type == CourseQuestion.SINGLE:
            post['q%d' % q.id] = [o.id for o in options if o.is_correct][0]
        elif q.type == CourseQuestion.MULTI:
            post['q%d' % q.id] = [o.id for o in options if o.is_correct]
        else:
            post['q%d' % q.id] = options[0].text
    return post


@override_settings(LANGUAGE_CODE='ru')
class CourseBase(TestCase):
    def setUp(self):
        cache.clear()
        self.teacher = create_user(username='teach')
        self.teacher.profile.is_teacher = True
        self.teacher.profile.save()
        self.other_teacher = create_user(username='teach2')
        self.other_teacher.profile.is_teacher = True
        self.other_teacher.profile.save()
        self.student = create_user(username='stud')
        self.student2 = create_user(username='stud2')
        self.admin = create_user(username='cadmin', is_superuser=True, is_staff=True)

    def login(self, user):
        client = Client()
        client.force_login(user)
        return client

    def enroll(self, course, user=None):
        user = user or self.student
        return CourseEnrollment.objects.create(course=course, profile=user.profile)

    def progress(self, enrollment):
        return logic.build_progress(enrollment)


class AccessTests(CourseBase):
    def test_navigation_link_exists(self):
        self.assertTrue(NavigationBar.objects.filter(key='courses', path='/courses/').exists())

    def test_catalog_shows_only_public_published(self):
        public = make_course(self.teacher, title='Открытый')
        make_course(self.teacher, title='Черновик', status=Course.DRAFT)
        make_course(self.teacher, title='Скрытый', is_hidden=True)
        make_course(self.teacher, title='Удалённый', is_deleted=True)
        make_course(self.teacher, title='По ссылке', access=Course.LINK)
        page = Client().get(reverse('course_catalog'))
        self.assertContains(page, 'Открытый')
        for hidden in ('Черновик', 'Скрытый', 'Удалённый', 'По ссылке'):
            self.assertNotContains(page, hidden)
        self.assertEqual(Client().get(reverse('course_catalog') + '?q=откр&order=popular').status_code, 200)
        self.assertEqual(Client().get(reverse('course_detail', args=[public.key])).status_code, 200)

    def test_visibility_rules(self):
        draft = make_course(self.teacher, status=Course.DRAFT)
        self.assertFalse(draft.can_view(self.student))
        self.assertTrue(draft.can_view(self.teacher))
        self.assertTrue(draft.can_view(self.admin))
        self.assertEqual(Client().get(reverse('course_detail', args=[draft.key])).status_code, 404)
        link = make_course(self.teacher, access=Course.LINK)
        self.assertEqual(Client().get(reverse('course_detail', args=[link.key])).status_code, 200)
        hidden = make_course(self.teacher, is_hidden=True)
        self.assertFalse(hidden.can_view(self.student))
        self.assertTrue(hidden.can_view(self.teacher))

    def test_organization_course(self):
        org = create_organization(name='Группа')
        course = make_course(self.teacher, access=Course.ORG, organization=org)
        self.assertFalse(course.can_view(self.student))
        self.assertFalse(course.can_view(self.student.__class__.objects.get(pk=self.student.pk)))
        self.student.profile.organizations.add(org)
        self.assertTrue(course.can_view(self.student))
        self.assertEqual(Client().get(reverse('course_detail', args=[course.key])).status_code, 404)

    def test_edit_rights(self):
        course = make_course(self.teacher)
        self.assertTrue(course.can_edit(self.teacher))
        self.assertTrue(course.can_edit(self.admin))
        self.assertFalse(course.can_edit(self.other_teacher))
        self.assertFalse(course.can_edit(self.student))
        self.assertEqual(self.login(self.other_teacher).get(reverse('course_edit', args=[course.key])).status_code, 404)
        self.assertEqual(self.login(self.student).get(reverse('course_edit', args=[course.key])).status_code, 404)
        self.assertEqual(Client().get(reverse('course_edit', args=[course.key])).status_code, 302)
        self.assertEqual(Client().get(reverse('course_students', args=[course.key])).status_code, 302)
        self.assertEqual(self.login(self.teacher).get(reverse('course_edit', args=[course.key])).status_code, 200)
        self.assertEqual(self.login(self.admin).get(reverse('course_edit', args=[course.key])).status_code, 200)
        course.coauthors.add(self.other_teacher.profile)
        self.assertTrue(course.can_edit(self.other_teacher))
        self.assertFalse(course.can_delete(self.other_teacher))
        self.assertTrue(course.can_delete(self.teacher))

    def test_edit_actions_need_edit_rights(self):
        course = make_course(self.teacher)
        url = reverse('course_edit_do', args=[course.key])
        response = self.login(self.other_teacher).post(url, {'action': 'module_add', 'title': 'Чужой'})
        self.assertEqual(response.status_code, 404)
        self.assertFalse(course.modules.exists())
        self.assertEqual(Client().post(url, {'action': 'module_add', 'title': 'x'}).status_code, 302)
        self.assertEqual(self.login(self.teacher).get(url).status_code, 405)

    def test_only_teachers_create_courses(self):
        self.assertEqual(self.login(self.student).get(reverse('course_new')).status_code, 403)
        self.assertEqual(self.login(self.student).post(reverse('course_new'), {'title': 'x'}).status_code, 403)
        self.assertEqual(Course.objects.count(), 0)
        response = self.login(self.teacher).post(reverse('course_new'), {'title': 'Мой курс', 'language': 'ky'})
        course = Course.objects.get()
        self.assertRedirects(response, reverse('course_edit', args=[course.key]))
        self.assertEqual((course.language, course.status, course.author_id),
                         ('ky', Course.DRAFT, self.teacher.profile.id))
        self.assertEqual(self.login(self.admin).get(reverse('course_new')).status_code, 200)

    def test_markdown_is_escaped(self):
        course = make_course(self.teacher, description='<script>alert(1)</script> **жирный**')
        page = Client().get(reverse('course_detail', args=[course.key]))
        self.assertNotContains(page, '<script>alert(1)</script>')
        self.assertContains(page, '<strong>жирный</strong>')

    def test_section_can_be_closed(self):
        course = make_course(self.teacher)
        add_lesson(course)
        MiscConfig.objects.create(key='courses_disabled', value='Идёт олимпиада')
        cache.clear()
        response = self.login(self.student).post(reverse('course_enroll', args=[course.key]))
        self.assertEqual(response.status_code, 403)
        self.assertContains(response, 'Идёт олимпиада', status_code=403)
        self.assertFalse(CourseEnrollment.objects.exists())
        self.assertContains(Client().get(reverse('course_catalog')), 'Идёт олимпиада')
        self.assertEqual(self.login(self.admin).post(reverse('course_enroll', args=[course.key])).status_code, 302)


class UtilityTests(TestCase):
    def test_youtube_id(self):
        vid = 'dQw4w9WgXcQ'
        for value in (vid, 'https://www.youtube.com/watch?v=' + vid, 'https://youtu.be/%s?t=5' % vid,
                      'https://www.youtube.com/embed/' + vid, 'https://youtube.com/shorts/' + vid,
                      'https://www.youtube.com/watch?feature=share&v=' + vid):
            self.assertEqual(youtube_id(value), vid, value)
        for bad in ('', 'https://example.com/watch?v=' + vid, 'javascript:alert(1)', 'abc'):
            self.assertEqual(youtube_id(bad), '', bad)


class ProgressTests(CourseBase):
    def test_text_course_needs_the_mark(self):
        course = make_course(self.teacher)
        first, second = add_lesson(course, 'Один'), add_lesson(course, 'Два')
        add_block(first, text='Привет')
        enrollment = self.enroll(course)
        client = self.login(self.student)
        self.assertEqual(client.get(reverse('course_lesson', args=[course.key, first.id])).status_code, 200)
        data = self.progress(enrollment)
        self.assertFalse(data.complete[first.id])
        self.assertEqual(data.percent, 0)
        client.post(reverse('course_mark', args=[course.key, first.id]))
        client.post(reverse('course_mark', args=[course.key, second.id]))
        enrollment.refresh_from_db()
        data = self.progress(enrollment)
        self.assertEqual(data.percent, 100)
        self.assertTrue(data.finished)
        self.assertIsNotNone(enrollment.completed_at)
        self.assertEqual(len(enrollment.certificate_code), 10)

    def test_optional_lessons_and_no_mark(self):
        course = make_course(self.teacher)
        required = add_lesson(course, 'Нужный', mark_required=False)
        optional = add_lesson(course, 'Лишний', is_required=False)
        enrollment = self.enroll(course)
        client = self.login(self.student)
        client.get(reverse('course_lesson', args=[course.key, required.id]))
        data = self.progress(enrollment)
        self.assertTrue(data.complete[required.id])
        self.assertFalse(data.complete.get(optional.id))
        self.assertTrue(data.finished)

    def test_draft_lessons_are_invisible_to_learners(self):
        course = make_course(self.teacher)
        add_lesson(course, 'Готов', mark_required=False)
        draft = add_lesson(course, 'Черновик', is_draft=True)
        self.enroll(course)
        self.assertEqual(self.login(self.student).get(reverse('course_lesson', args=[course.key, draft.id]))
                         .status_code, 404)
        self.assertEqual(self.login(self.teacher).get(reverse('course_lesson', args=[course.key, draft.id]))
                         .status_code, 200)

    def test_sequential_and_dates(self):
        course = make_course(self.teacher, sequential=True)
        first, second = add_lesson(course, 'А'), add_lesson(course, 'Б')
        later = add_lesson(course, 'В', open_at=timezone.now() + timedelta(days=2), is_required=False)
        enrollment = self.enroll(course)
        data = self.progress(enrollment)
        self.assertTrue(data.available[first.id])
        self.assertFalse(data.available[second.id])
        self.assertFalse(data.available[later.id])
        client = self.login(self.student)
        locked = client.get(reverse('course_lesson', args=[course.key, second.id]))
        self.assertContains(locked, 'Сначала пройдите')
        self.assertContains(client.get(reverse('course_lesson', args=[course.key, later.id])), 'Урок откроется')
        client.post(reverse('course_mark', args=[course.key, first.id]))
        self.assertTrue(self.progress(enrollment).available[second.id])

    def test_learn_redirects_to_next_lesson(self):
        course = make_course(self.teacher)
        first, second = add_lesson(course, 'А'), add_lesson(course, 'Б')
        enrollment = self.enroll(course)
        client = self.login(self.student)
        self.assertRedirects(client.get(reverse('course_learn', args=[course.key])),
                             reverse('course_lesson', args=[course.key, first.id]))
        CourseProgress.objects.update_or_create(enrollment=enrollment, lesson=first,
                                                defaults={'marked_at': timezone.now()})
        CourseEnrollment.objects.filter(id=enrollment.id).update(last_lesson=None)
        self.assertRedirects(client.get(reverse('course_learn', args=[course.key])),
                             reverse('course_lesson', args=[course.key, second.id]))

    def test_learner_needs_enrollment(self):
        course = make_course(self.teacher)
        lesson = add_lesson(course)
        client = self.login(self.student)
        self.assertRedirects(client.get(reverse('course_lesson', args=[course.key, lesson.id])),
                             reverse('course_detail', args=[course.key]))
        client.post(reverse('course_enroll', args=[course.key]))
        course.refresh_from_db()
        self.assertEqual(course.enrollments_count, 1)
        client.post(reverse('course_enroll', args=[course.key]))
        course.refresh_from_db()
        self.assertEqual(course.enrollments_count, 1)

    def test_pass_percent_blocks_certificate(self):
        course = make_course(self.teacher, pass_percent=80)
        lesson = add_lesson(course, mark_required=False)
        block = add_test(lesson, pass_percent=0)
        enrollment = self.enroll(course)
        client = self.login(self.student)
        url = reverse('course_submit_test', args=[course.key, lesson.id, block.id])
        client.post(url, {})
        enrollment.refresh_from_db()
        data = self.progress(enrollment)
        self.assertEqual(data.score_percent, 0)
        self.assertFalse(data.finished)
        self.assertIsNone(enrollment.completed_at)
        client.post(url, right_answers(block))
        enrollment.refresh_from_db()
        self.assertEqual(self.progress(enrollment).score_percent, 100)
        self.assertIsNotNone(enrollment.completed_at)

    def test_certificate_is_off_when_disabled(self):
        course = make_course(self.teacher, certificate=False)
        lesson = add_lesson(course, mark_required=False)
        enrollment = self.enroll(course)
        self.login(self.student).get(reverse('course_lesson', args=[course.key, lesson.id]))
        enrollment.refresh_from_db()
        self.assertIsNotNone(enrollment.completed_at)
        self.assertIsNone(enrollment.certificate_code)


class TestBlockTests(CourseBase):
    def setUp(self):
        super().setUp()
        self.course = make_course(self.teacher)
        self.lesson = add_lesson(self.course, mark_required=False)
        self.block = add_test(self.lesson, attempts=2, pass_percent=60, show_answers=True)
        self.enrollment = self.enroll(self.course)
        self.client = self.login(self.student)
        self.url = reverse('course_submit_test', args=[self.course.key, self.lesson.id, self.block.id])
        self.page = reverse('course_lesson', args=[self.course.key, self.lesson.id])

    def test_grading_all_types(self):
        score, total, results = logic.grade_test(self.block, {})
        self.assertEqual((score, total), (0, 5))
        answers = {str(k[1:]): v for k, v in right_answers(self.block).items()}
        answers = {k: v for k, v in answers.items()}
        score, total, results = logic.grade_test(self.block, answers)
        self.assertEqual((score, total), (5, 5))
        self.assertTrue(all(results.values()))

    def test_answer_checks(self):
        q = CourseQuestion.objects.get(block=self.block, type=CourseQuestion.NUMBER)
        options = list(q.options.all())
        for ok in ('3.14', '3,14', ' 3.140 '):
            self.assertTrue(logic.check_answer(q, ok, options), ok)
        for bad in ('', 'abc', '3.2'):
            self.assertFalse(logic.check_answer(q, bad, options), bad)
        word = CourseQuestion.objects.get(block=self.block, type=CourseQuestion.TEXT)
        self.assertTrue(logic.check_answer(word, '  бишкек ', list(word.options.all())))
        self.assertFalse(logic.check_answer(word, 'ош', list(word.options.all())))
        multi = CourseQuestion.objects.get(block=self.block, type=CourseQuestion.MULTI)
        ids = [o.id for o in multi.options.all() if o.is_correct]
        self.assertFalse(logic.check_answer(multi, ids[:1], list(multi.options.all())))
        self.assertFalse(logic.check_answer(multi, ids + [multi.options.filter(is_correct=False).first().id],
                                            list(multi.options.all())))

    def test_page_does_not_leak_answers_before_attempt(self):
        page = self.client.get(self.page)
        self.assertContains(page, '2+2?')
        self.assertNotContains(page, 'co-key')
        self.assertNotContains(page, 'Верный ответ:')

    def test_attempts_and_review(self):
        wrong = self.client.post(self.url, {})
        attempt = CourseAttempt.objects.get()
        self.assertRedirects(wrong, self.page + '?attempt=%d#block-%d' % (attempt.id, self.block.id),
                             fetch_redirect_response=False)
        review = self.client.get(self.page + '?attempt=%d' % attempt.id)
        self.assertContains(review, 'co-wrong')
        self.assertContains(review, 'Не зачтено')
        self.client.post(self.url, right_answers(self.block))
        self.assertEqual(CourseAttempt.objects.count(), 2)
        self.assertContains(self.client.get(self.page), 'Зачтено')
        blocked = self.client.post(self.url, right_answers(self.block))
        self.assertContains(blocked, 'Попытки закончились')
        self.assertEqual(CourseAttempt.objects.count(), 2)

    def test_hidden_answers_setting(self):
        self.block.data = {'attempts': 0, 'pass_percent': 0, 'show_answers': False}
        self.block.save()
        self.client.post(self.url, {})
        self.assertNotContains(self.client.get(self.page), 'co-key')
        self.assertNotContains(self.client.get(self.page), 'co-wrong')

    def test_closed_lesson_refuses_attempts(self):
        self.lesson.deadline = timezone.now() - timedelta(hours=1)
        self.lesson.save()
        self.assertContains(self.client.post(self.url, right_answers(self.block)), 'Срок сдачи прошёл')
        self.assertFalse(CourseAttempt.objects.exists())

    def test_strangers_cannot_submit(self):
        outsider = self.login(self.student2)
        self.assertEqual(outsider.post(self.url, right_answers(self.block)).status_code, 302)
        self.assertFalse(CourseAttempt.objects.exists())

    def test_best_attempt_counts(self):
        self.client.post(self.url, right_answers(self.block))
        self.client.post(self.url, {})
        state = self.progress(self.enrollment).states[self.block.id]
        self.assertEqual((state.score, state.maximum, state.attempts, state.done), (5, 5, 2, True))


class AssignmentTests(CourseBase):
    def setUp(self):
        super().setUp()
        self.course = make_course(self.teacher)
        self.lesson = add_lesson(self.course, mark_required=False)
        self.block = add_block(self.lesson, CourseBlock.ASSIGNMENT, points=10,
                               data={'allow_text': True, 'allow_file': True, 'pass_percent': 50})
        self.enrollment = self.enroll(self.course)
        self.client = self.login(self.student)
        self.url = reverse('course_submit_work', args=[self.course.key, self.lesson.id, self.block.id])

    def grade(self, work, **post):
        return self.login(self.teacher).post(reverse('course_grade', args=[self.course.key, work.id]), post)

    def test_submit_grade_and_complete(self):
        self.client.post(self.url, {'text': 'Моё решение'})
        work = CourseWork.objects.get()
        self.assertEqual(work.status, CourseWork.PENDING)
        self.assertFalse(self.progress(self.enrollment).complete[self.lesson.id])
        page = self.login(self.teacher).get(reverse('course_grading', args=[self.course.key]))
        self.assertContains(page, 'Моё решение')
        self.grade(work, result='grade', grade='8,5', comment='Хорошо')
        work.refresh_from_db()
        self.assertEqual((work.status, work.grade, work.comment), (CourseWork.GRADED, 8.5, 'Хорошо'))
        self.assertEqual(work.graded_by_id, self.teacher.profile.id)
        data = self.progress(self.enrollment)
        self.assertTrue(data.complete[self.lesson.id])
        self.assertEqual(data.score_percent, 85)
        self.assertContains(self.client.get(reverse('course_lesson', args=[self.course.key, self.lesson.id])), 'Хорошо')

    def test_grade_is_clamped_and_below_pass_stays_open(self):
        self.client.post(self.url, {'text': 'Плохо'})
        work = CourseWork.objects.get()
        self.grade(work, result='grade', grade='2')
        self.assertFalse(self.progress(self.enrollment).complete[self.lesson.id])
        self.grade(work, result='grade', grade='500')
        work.refresh_from_db()
        self.assertEqual(work.grade, 10)

    def test_return_and_resubmit(self):
        self.client.post(self.url, {'text': 'Первая версия'})
        first = CourseWork.objects.get()
        self.grade(first, result='return', comment='Дополните')
        first.refresh_from_db()
        self.assertEqual(first.status, CourseWork.RETURNED)
        self.client.post(self.url, {'text': 'Вторая версия'})
        self.assertEqual(CourseWork.objects.count(), 2)
        queue = self.login(self.teacher).get(reverse('course_grading', args=[self.course.key]))
        self.assertContains(queue, 'Вторая версия')
        self.assertNotContains(queue, 'Первая версия')
        stale = self.grade(first, result='grade', grade='9')
        self.assertContains(stale, 'новую версию')

    def test_graded_work_is_locked(self):
        self.client.post(self.url, {'text': 'Готово'})
        self.grade(CourseWork.objects.get(), result='grade', grade='10')
        self.assertContains(self.client.post(self.url, {'text': 'Ещё раз'}), 'уже оценена')
        self.assertEqual(CourseWork.objects.count(), 1)

    def test_empty_and_bad_files_are_refused(self):
        self.assertContains(self.client.post(self.url, {'text': '  '}), 'Напишите ответ')
        bad = SimpleUploadedFile('virus.exe', b'MZ')
        self.assertContains(self.client.post(self.url, {'file': bad}), 'не принимается')
        big = SimpleUploadedFile('big.zip', b'0' * (10 * 1024 * 1024 + 1))
        self.assertContains(self.client.post(self.url, {'file': big}), 'больше 10')
        self.assertFalse(CourseWork.objects.exists())

    def test_files_are_private(self):
        upload = SimpleUploadedFile('answer.txt', b'secret answer')
        self.client.post(self.url, {'file': upload})
        work = CourseWork.objects.get()
        url = reverse('course_work_file', args=[self.course.key, work.id])
        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertEqual(self.login(self.teacher).get(url).status_code, 200)
        self.assertEqual(self.login(self.student2).get(url).status_code, 404)
        self.assertEqual(self.login(self.other_teacher).get(url).status_code, 404)
        self.assertEqual(Client().get(url).status_code, 302)
        work.file.delete(save=False)

    def test_only_the_team_grades(self):
        self.client.post(self.url, {'text': 'x'})
        work = CourseWork.objects.get()
        url = reverse('course_grade', args=[self.course.key, work.id])
        self.assertEqual(self.client.post(url, {'result': 'grade', 'grade': '10'}).status_code, 404)
        self.assertEqual(self.login(self.other_teacher).post(url, {'result': 'grade', 'grade': '10'}).status_code, 404)
        work.refresh_from_db()
        self.assertEqual(work.status, CourseWork.PENDING)

    def test_text_only_assignment(self):
        self.block.data = {'allow_text': True, 'allow_file': False}
        self.block.save()
        upload = SimpleUploadedFile('a.txt', b'x')
        self.assertContains(self.client.post(self.url, {'file': upload}), 'Напишите ответ')


class ProblemBlockTests(CourseBase):
    def test_problem_block_follows_submissions(self):
        course = make_course(self.teacher)
        lesson = add_lesson(course, mark_required=False)
        block = add_block(lesson, CourseBlock.PROBLEM, points=20, data={'pass_percent': 100})
        enrollment = self.enroll(course)
        self.assertEqual(logic.build_progress(enrollment).states[block.id].done, False)
        block.problem = create_problem(code='cprob')
        block.save()
        for ratio, score, done in ((0.5, 10, False), (1.0, 20, True)):
            with patch.object(logic, 'problem_ratio', return_value=ratio):
                state = logic.build_progress(enrollment).states[block.id]
            self.assertEqual((state.score, state.done), (score, done))
        # No problem chosen: never done, no crash.
        self.assertEqual(logic.problem_ratio(self.student.profile, None), 0.0)


class EditorTests(CourseBase):
    def setUp(self):
        super().setUp()
        self.course = make_course(self.teacher, status=Course.DRAFT)
        self.client = self.login(self.teacher)
        self.url = reverse('course_edit_do', args=[self.course.key])

    def do(self, action, **post):
        return self.client.post(self.url, dict(post, action=action))

    def test_settings_save(self):
        response = self.do('course_save', title='Геометрия', subject='Математика', description='Текст',
                           language='en', access='link', status='published', pass_percent='70', sequential='1',
                           certificate='1', reviews_on='1')
        self.assertRedirects(response, reverse('course_edit', args=[self.course.key]))
        self.course.refresh_from_db()
        self.assertEqual((self.course.title, self.course.language, self.course.access, self.course.status,
                          self.course.pass_percent, self.course.sequential),
                         ('Геометрия', 'en', 'link', Course.PUBLISHED, 70, True))
        self.assertFalse(self.course.is_hidden)

    def test_settings_validation(self):
        self.assertContains(self.do('course_save', title=' '), 'Назовите курс')
        self.assertContains(self.do('course_save', title='x', access='org'), 'Выберите организацию')
        self.assertContains(self.do('course_save', title='x', coauthors='nobody'), 'Нет пользователя')

    def test_coauthors_and_org(self):
        org = create_organization(name='Кафедра')
        self.teacher.profile.organizations.add(org)
        self.do('course_save', title='x', access='org', organization=org.id, coauthors='teach2')
        self.course.refresh_from_db()
        self.assertEqual(self.course.organization_id, org.id)
        self.assertEqual(list(self.course.coauthors.all()), [self.other_teacher.profile])
        co = self.login(self.other_teacher).post(self.url, {'action': 'course_save', 'title': 'Новое имя',
                                                            'coauthors': ''})
        self.assertEqual(co.status_code, 302)
        self.course.refresh_from_db()
        self.assertEqual(self.course.title, 'Новое имя')
        self.assertEqual(self.course.coauthors.count(), 1)

    def test_outsider_org_is_refused(self):
        org = create_organization(name='Чужая')
        self.assertContains(self.do('course_save', title='x', access='org', organization=org.id),
                            'Выберите организацию')

    def test_modules_lessons_order(self):
        self.do('module_add', title='Первый')
        module = CourseModule.objects.get()
        response = self.do('lesson_add', title='Вводный', module=module.id)
        lesson = CourseLesson.objects.get()
        self.assertRedirects(response, reverse('course_edit_lesson', args=[self.course.key, lesson.id]))
        self.assertTrue(lesson.is_draft)
        self.do('lesson_add', title='Второй')
        second = CourseLesson.objects.exclude(id=lesson.id).get()
        self.assertIsNone(second.module_id)
        self.do('lesson_add', title='Третий', module=module.id)
        third = CourseLesson.objects.get(title='Третий')
        self.do('lesson_move', lesson=third.id, dir='up')
        lesson.refresh_from_db(), third.refresh_from_db()
        self.assertLess(third.order, lesson.order)
        self.do('lesson_publish', lesson=lesson.id)
        lesson.refresh_from_db()
        self.assertFalse(lesson.is_draft)
        self.do('module_delete', module=module.id)
        lesson.refresh_from_db()
        self.assertIsNone(lesson.module_id)
        self.do('lesson_delete', lesson=second.id)
        self.assertFalse(CourseLesson.objects.filter(id=second.id).exists())
        # Lessons of another course cannot be touched.
        other = make_course(self.other_teacher)
        stranger = add_lesson(other)
        self.assertEqual(self.do('lesson_delete', lesson=stranger.id).status_code, 404)
        self.assertTrue(CourseLesson.objects.filter(id=stranger.id).exists())

    def test_lesson_save_and_dates(self):
        lesson = add_lesson(self.course, 'Старое')
        response = self.do('lesson_save', lesson=lesson.id, title='Новое', is_required='1', mark_required='',
                           open_at='2030-01-05T09:30', deadline='2030-02-01T12:00')
        self.assertEqual(response.status_code, 302)
        lesson.refresh_from_db()
        self.assertEqual(lesson.title, 'Новое')
        self.assertTrue(lesson.is_draft is False and lesson.is_required and not lesson.mark_required)
        self.assertEqual((lesson.open_at.year, lesson.deadline.month), (2030, 2))
        self.assertContains(self.do('lesson_save', lesson=lesson.id, title='x', open_at='вчера'), 'Неверная дата')
        self.assertContains(self.do('lesson_save', lesson=lesson.id, title=''), 'Назовите урок')
        page = self.client.get(reverse('course_edit_lesson', args=[self.course.key, lesson.id]))
        self.assertContains(page, '2030-01-05T09:30')

    def test_blocks_of_every_type(self):
        lesson = add_lesson(self.course)
        for kind in CourseBlock.TYPES:
            self.assertEqual(self.do('block_add', lesson=lesson.id, type=kind[0]).status_code, 302)
        self.assertEqual(lesson.blocks.count(), 7)
        self.assertEqual(self.do('block_add', lesson=lesson.id, type='virus').status_code, 404)
        page = self.client.get(reverse('course_edit_lesson', args=[self.course.key, lesson.id]))
        self.assertEqual(page.status_code, 200)
        video = lesson.blocks.get(type=CourseBlock.VIDEO)
        self.do('block_save', block=video.id, title='Видео', video='https://youtu.be/dQw4w9WgXcQ', text='Подпись')
        video.refresh_from_db()
        self.assertEqual(video.youtube_id, 'dQw4w9WgXcQ')
        self.assertContains(self.do('block_save', block=video.id, video='https://evil.example/x'),
                            'Это не ссылка на YouTube')
        text = lesson.blocks.get(type=CourseBlock.TEXT)
        self.do('block_save', block=text.id, text='**важно** $x^2$')
        self.do('block_move', block=text.id, dir='down')
        assignment = lesson.blocks.get(type=CourseBlock.ASSIGNMENT)
        self.do('block_save', block=assignment.id, points='25', pass_percent='60', allow_text='1')
        assignment.refresh_from_db()
        self.assertEqual((assignment.points, assignment.data['pass_percent'], assignment.data['allow_file']),
                         (25, 60, False))
        self.assertContains(self.do('block_save', block=assignment.id), 'хотя бы один способ ответа')
        problem = lesson.blocks.get(type=CourseBlock.PROBLEM)
        self.assertContains(self.do('block_save', block=problem.id, problem_code='nosuchproblem'), 'Задача не найдена')
        self.do('block_delete', block=text.id)
        self.assertEqual(lesson.blocks.count(), 6)

    def test_image_and_file_uploads(self):
        lesson = add_lesson(self.course)
        image_block = add_block(lesson, CourseBlock.IMAGE)
        fake = SimpleUploadedFile('x.png', b'not a picture')
        self.assertContains(self.do('block_save', block=image_block.id, image=fake), 'Это не картинка')
        file_block = add_block(lesson, CourseBlock.FILE)
        exe = SimpleUploadedFile('x.exe', b'MZ')
        self.assertContains(self.do('block_save', block=file_block.id, file=exe), 'не принимается')
        good = SimpleUploadedFile('notes.txt', b'hello')
        self.do('block_save', block=file_block.id, title='Конспект', file=good)
        file_block.refresh_from_db()
        self.assertTrue(file_block.file.name.startswith('courses/files/'))
        self.assertTrue(file_block.file.name.endswith('.txt'))
        self.enroll(self.course)
        self.course.status = Course.PUBLISHED
        self.course.save()
        url = reverse('course_block_file', args=[self.course.key, file_block.id])
        self.assertEqual(self.login(self.student).get(url).status_code, 200)
        self.assertEqual(self.login(self.student2).get(url).status_code, 404)
        file_block.file.delete(save=False)

    def test_question_editing(self):
        lesson = add_lesson(self.course)
        self.do('block_add', lesson=lesson.id, type=CourseBlock.TEST)
        block = lesson.blocks.get()
        question = block.questions.get()
        self.assertEqual(question.options.count(), 2)
        self.do('question_add', block=block.id)
        self.assertEqual(block.questions.count(), 2)
        base = {'question': question.id, 'text': 'Сколько?', 'qtype': 'single', 'points': '3',
                'opt_0_text': 'Раз', 'opt_1_text': 'Два', 'opt_1_ok': '1', 'opt_2_text': 'Три'}
        self.assertEqual(self.do('question_save', **base).status_code, 302)
        question.refresh_from_db()
        self.assertEqual((question.points, question.options.count()), (3, 3))
        self.assertEqual(question.options.get(is_correct=True).text, 'Два')
        both = dict(base, opt_0_ok='1')
        self.assertContains(self.do('question_save', **both), 'Отметьте один верный')
        self.assertContains(self.do('question_save', **dict(base, opt_1_ok='', opt_1_text='', opt_2_text='')),
                            'минимум два')
        self.assertContains(self.do('question_save', **dict(base, qtype='multi', opt_1_ok='')), 'хотя бы один')
        self.assertContains(self.do('question_save', **dict(base, qtype='number', opt_0_text='abc')),
                            'должен быть числом')
        self.assertContains(self.do('question_save', **dict(base, qtype='text', opt_0_text='', opt_1_text='',
                                                            opt_2_text='')), 'верный ответ')
        question.refresh_from_db()
        self.assertEqual(question.options.count(), 3)
        self.do('question_move', question=question.id, dir='down')
        self.do('question_delete', question=question.id)
        self.assertEqual(block.questions.count(), 1)

    def test_copy_course_is_deep_and_independent(self):
        lesson = add_lesson(self.course, 'Урок', module=CourseModule.objects.create(course=self.course, title='М'))
        test = add_test(lesson, attempts=3)
        add_block(lesson, CourseBlock.TEXT, text='Привет')
        response = self.client.post(reverse('course_copy', args=[self.course.key]))
        copy = Course.objects.exclude(id=self.course.id).get()
        self.assertRedirects(response, reverse('course_edit', args=[copy.key]))
        self.assertEqual((copy.status, copy.enrollments_count), (Course.DRAFT, 0))
        new_lesson = copy.lessons.get()
        self.assertEqual(new_lesson.module.course_id, copy.id)
        self.assertEqual(new_lesson.blocks.count(), 2)
        new_test = new_lesson.blocks.get(type=CourseBlock.TEST)
        self.assertEqual(new_test.questions.count(), 4)
        self.assertEqual(new_test.data, test.data)
        self.assertEqual(CourseOption.objects.filter(question__block=new_test).count(),
                         CourseOption.objects.filter(question__block=test).count())
        self.assertEqual(test.questions.count(), 4)
        self.assertEqual(self.login(self.other_teacher).post(reverse('course_copy', args=[self.course.key]))
                         .status_code, 404)

    def test_delete_is_soft_and_owner_only(self):
        self.course.coauthors.add(self.other_teacher.profile)
        self.assertEqual(self.login(self.other_teacher).post(reverse('course_delete', args=[self.course.key]))
                         .status_code, 404)
        self.client.post(reverse('course_delete', args=[self.course.key]))
        self.course.refresh_from_db()
        self.assertTrue(self.course.is_deleted)
        self.assertEqual(Client().get(reverse('course_detail', args=[self.course.key])).status_code, 404)


class GradebookTests(CourseBase):
    def test_students_page_and_export(self):
        course = make_course(self.teacher)
        lesson = add_lesson(course, 'Урок', mark_required=False)
        add_block(lesson, CourseBlock.ASSIGNMENT, points=10)
        enrollment = self.enroll(course)
        CourseWork.objects.create(enrollment=enrollment, block=lesson.blocks.get(), text='ответ',
                                  status=CourseWork.GRADED, grade=7)
        client = self.login(self.teacher)
        page = client.get(reverse('course_students', args=[course.key]))
        self.assertContains(page, 'stud')
        self.assertContains(client.get(reverse('course_students', args=[course.key]) + '?q=zzz'), 'Слушателей пока нет')
        sheet = client.get(reverse('course_students_xlsx', args=[course.key]))
        self.assertEqual(sheet.status_code, 200)
        self.assertEqual(sheet.content[:2], b'PK')
        self.assertEqual(self.login(self.student).get(reverse('course_students', args=[course.key])).status_code, 404)
        self.assertEqual(self.login(self.student).get(reverse('course_students_xlsx', args=[course.key]))
                         .status_code, 404)
        self.assertEqual(self.login(self.student).get(reverse('course_grading', args=[course.key])).status_code, 404)

    def test_my_courses(self):
        course = make_course(self.teacher)
        add_lesson(course)
        self.enroll(course)
        page = self.login(self.student).get(reverse('course_my'))
        self.assertContains(page, 'Алгебра')
        self.assertContains(self.login(self.teacher).get(reverse('course_my')), 'Я преподаю')
        self.assertEqual(Client().get(reverse('course_my')).status_code, 302)


class CertificateTests(CourseBase):
    def finished(self):
        course = make_course(self.teacher, title='Сертифицируемый курс')
        add_lesson(course, mark_required=False)
        enrollment = self.enroll(course)
        self.login(self.student).get(reverse('course_lesson', args=[course.key, course.lessons.get().id]))
        enrollment.refresh_from_db()
        return enrollment

    def test_pdf_page_and_qr(self):
        enrollment = self.finished()
        code = enrollment.certificate_code
        client = Client()
        page = client.get(reverse('course_certificate', args=[code]))
        self.assertContains(page, 'Сертифицируемый курс')
        self.assertEqual(client.get(reverse('course_certificate', args=[code.lower()])).status_code, 200)
        pdf = client.get(reverse('course_certificate_pdf', args=[code]))
        self.assertEqual(pdf['Content-Type'], 'application/pdf')
        self.assertTrue(pdf.content.startswith(b'%PDF'))
        self.assertGreater(len(pdf.content), 5000)
        self.assertEqual(client.get(reverse('course_certificate_qr', args=[code]))['Content-Type'], 'image/svg+xml')
        self.assertEqual(client.get(reverse('course_certificate', args=['NOSUCHCODE1'])).status_code, 404)

    def test_pdf_for_each_language(self):
        enrollment = self.finished()
        from judge.utils.course_certificate import render_certificate
        for lang in ('ru', 'ky', 'en'):
            enrollment.course.language = lang
            self.assertTrue(render_certificate(enrollment, 'https://example.org/c/1').startswith(b'%PDF'), lang)

    def test_unfinished_has_no_certificate(self):
        course = make_course(self.teacher)
        add_lesson(course)
        enrollment = self.enroll(course)
        self.assertIsNone(enrollment.certificate_code)
        self.assertEqual(Client().get(reverse('course_certificate', args=['ABCDEFGHJK'])).status_code, 404)


class CommentTests(CourseBase):
    def test_comments_and_reviews(self):
        course = make_course(self.teacher)
        lesson = add_lesson(course)
        self.enroll(course)
        url = reverse('course_comment', args=[course.key, lesson.id])
        client = self.login(self.student)
        client.post(url, {'text': 'Вопрос <b>по</b> уроку'})
        comment = lesson.comments.get()
        page = client.get(reverse('course_lesson', args=[course.key, lesson.id]))
        self.assertContains(page, 'Вопрос &lt;b&gt;по&lt;/b&gt; уроку')
        self.login(self.teacher).post(url, {'text': 'Ответ', 'parent': comment.id})
        self.assertEqual(lesson.comments.filter(parent=comment).count(), 1)
        self.assertEqual(self.login(self.student2).post(url, {'text': 'Чужой'}).status_code, 404)
        delete = reverse('course_comment_delete', args=[course.key, comment.id])
        self.assertEqual(self.login(self.student2).post(delete).status_code, 404)
        client.post(delete)
        self.assertFalse(lesson.comments.exists())
        client.post(reverse('course_rate', args=[course.key]), {'rating': '9', 'text': 'Отлично'})
        review = course.reviews.get()
        self.assertEqual(review.rating, 5)
        client.post(reverse('course_rate', args=[course.key]), {'rating': '4'})
        self.assertEqual(course.reviews.get().rating, 4)
        self.assertEqual(self.login(self.student2).post(reverse('course_rate', args=[course.key]), {'rating': '1'})
                         .status_code, 404)
        self.assertContains(Client().get(reverse('course_detail', args=[course.key])), '4.0')


class PagesRenderTests(CourseBase):
    def test_lesson_with_every_block_renders(self):
        course = make_course(self.teacher, sequential=False)
        lesson = add_lesson(course, 'Всё сразу')
        add_block(lesson, CourseBlock.TEXT, title='Теория', text='# Заголовок\n\n```python\nprint(1)\n```\n$a^2$')
        add_block(lesson, CourseBlock.VIDEO, title='Видео', youtube_id='dQw4w9WgXcQ', text='Смотрите')
        add_block(lesson, CourseBlock.FILE, title='Файл')
        add_test(lesson)
        add_block(lesson, CourseBlock.ASSIGNMENT, text='Сделайте', points=5)
        add_block(lesson, CourseBlock.PROBLEM, text='Решите')
        self.enroll(course)
        page = self.login(self.student).get(reverse('course_lesson', args=[course.key, lesson.id]))
        self.assertContains(page, 'youtube-nocookie.com/embed/dQw4w9WgXcQ')
        self.assertContains(page, 'Изучено')
        self.assertContains(page, 'Сделайте')
        preview = self.login(self.teacher).get(reverse('course_lesson', args=[course.key, lesson.id]))
        self.assertContains(preview, 'Предпросмотр')
        self.assertEqual(self.login(self.teacher).get(reverse('course_detail', args=[course.key])).status_code, 200)
        self.assertEqual(self.login(self.teacher).get(reverse('course_edit_lesson', args=[course.key, lesson.id]))
                         .status_code, 200)

    def test_preview_does_not_save_progress(self):
        course = make_course(self.teacher)
        lesson = add_lesson(course)
        self.login(self.teacher).get(reverse('course_lesson', args=[course.key, lesson.id]))
        self.assertFalse(CourseEnrollment.objects.exists())
        self.assertFalse(CourseProgress.objects.exists())

    def test_teacher_badge_in_user_links(self):
        course = make_course(self.teacher)
        page = Client().get(reverse('course_detail', args=[course.key]))
        self.assertContains(page, 'fa-graduation-cap')

    def test_admin_pages(self):
        course = make_course(self.teacher)
        lesson = add_lesson(course)
        add_block(lesson)
        client = self.login(self.admin)
        for name, args in (('admin:judge_course_changelist', ()), ('admin:judge_course_add', ()),
                           ('admin:judge_course_change', (course.pk,)),
                           ('admin:judge_courselesson_change', (lesson.pk,)),
                           ('admin:judge_courseenrollment_changelist', ()), ('admin:judge_coursework_changelist', ()),
                           ('admin:judge_profile_changelist', ())):
            self.assertEqual(client.get(reverse(name, args=args)).status_code, 200, name)
        client.post(reverse('admin:judge_profile_changelist'), {
            'action': 'make_teachers', '_selected_action': [self.student.profile.pk]})
        self.student.profile.refresh_from_db()
        self.assertTrue(self.student.profile.is_teacher)
        client.post(reverse('admin:judge_course_changelist'), {
            'action': 'hide', '_selected_action': [course.pk]})
        course.refresh_from_db()
        self.assertTrue(course.is_hidden)
        self.assertEqual(Client().get(reverse('course_detail', args=[course.key])).status_code, 404)

    def test_static_files_exist(self):
        import os
        from django.conf import settings
        base = os.path.join(settings.BASE_DIR, 'resources', 'courses')
        for name in ('courses.css', 'courses.js', 'fonts/DejaVuSans.ttf', 'fonts/DejaVuSans-Bold.ttf'):
            self.assertTrue(os.path.isfile(os.path.join(base, name)), name)


class HardeningTests(CourseBase):
    def test_locked_lesson_file_and_draft_comment(self):
        course = make_course(self.teacher, sequential=True)
        add_lesson(course, 'Первый')
        locked = add_lesson(course, 'Второй')
        block = add_block(locked, CourseBlock.FILE, title='Секрет')
        block.file.save('s.txt', SimpleUploadedFile('s.txt', b'secret'))
        self.enroll(course)
        client = self.login(self.student)
        self.assertEqual(client.get(reverse('course_block_file', args=[course.key, block.id])).status_code, 404)
        self.assertEqual(self.login(self.teacher).get(reverse('course_block_file', args=[course.key, block.id]))
                         .status_code, 200)
        draft = add_lesson(course, 'Черновик', is_draft=True)
        self.assertEqual(client.post(reverse('course_comment', args=[course.key, draft.id]), {'text': 'x'})
                         .status_code, 404)
        self.assertEqual(client.post(reverse('course_comment', args=[course.key, locked.id]), {'text': 'x'})
                         .status_code, 404)
        self.assertFalse(locked.comments.exists())
        block.file.delete(save=False)

    def test_cannot_leave_after_submitting_work(self):
        course = make_course(self.teacher)
        lesson = add_lesson(course)
        block = add_test(lesson)
        enrollment = self.enroll(course)
        client = self.login(self.student)
        client.post(reverse('course_submit_test', args=[course.key, lesson.id, block.id]), {})
        response = client.post(reverse('course_leave', args=[course.key]))
        self.assertContains(response, 'Нельзя отписаться')
        self.assertTrue(CourseEnrollment.objects.filter(id=enrollment.id).exists())
        CourseAttempt.objects.all().delete()
        client.post(reverse('course_leave', args=[course.key]))
        self.assertFalse(CourseEnrollment.objects.exists())
