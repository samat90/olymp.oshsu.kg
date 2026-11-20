"""Courses, learner side: catalog, course page, lesson player, tests, assignments, comments, certificates."""
import os
from io import BytesIO

from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Avg, Count, F, Q
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from judge.models import Course, CourseAttempt, CourseBlock, CourseComment, CourseEnrollment, CourseLesson, \
    CourseReview, CourseWork, MiscConfig
from judge.utils import course_logic as logic

CATALOG_PAGE = 24
WORK_MAX = 10 * 1024 * 1024
WORK_EXT = {'.txt', '.md', '.pdf', '.doc', '.docx', '.odt', '.xls', '.xlsx', '.ods', '.ppt', '.pptx', '.zip', '.7z',
            '.rar', '.png', '.jpg', '.jpeg', '.gif', '.webp', '.py', '.cpp', '.c', '.h', '.java', '.cs', '.js', '.go',
            '.kt', '.pas', '.csv', '.json', '.ipynb', '.html', '.css', '.sql'}


def section_closed():
    """Admins can close the section for a while: misc config `courses_disabled` holds the message."""
    value = cache.get('co:disabled')
    if value is None:
        value = MiscConfig.objects.filter(key='courses_disabled').values_list('value', flat=True).first() or ''
        cache.set('co:disabled', value, 30)
    return value.strip()


def message(request, text, back=None, status=200):
    return render(request, 'courses/message.html', {'title': _('Курсы'), 'message': text, 'back': back}, status=status)


def guard_write(request):
    """A reply for blocked changes while the section is closed (None when changes are allowed)."""
    note = section_closed()
    if note and not Course.is_admin(request.user):
        return message(request, note, status=403)
    return None


def get_course(request, key, edit=False):
    course = get_object_or_404(Course.objects.select_related('author__user', 'organization'), key=key)
    allowed = course.can_edit(request.user) if edit else course.can_view(request.user)
    if not allowed:
        raise Http404()
    return course


def can_teach(user):
    return user.is_authenticated and (user.profile.is_teacher or Course.is_admin(user))


def course_stats(courses):
    return courses.annotate(
        lesson_total=Count('lessons', filter=Q(lessons__is_draft=False), distinct=True),
        rating=Avg('reviews__rating'), review_total=Count('reviews', distinct=True),
    ).select_related('author__user')


def visible_courses():
    return Course.objects.filter(access=Course.PUBLIC, status=Course.PUBLISHED, is_hidden=False, is_deleted=False)


# ---------------------------------------------------------------- catalog

def catalog(request):
    courses = course_stats(visible_courses())
    query = request.GET.get('q', '').strip()[:100]
    subject = request.GET.get('subject', '').strip()[:60]
    language = request.GET.get('lang', '').strip()[:2]
    if query:
        courses = courses.filter(Q(title__icontains=query) | Q(description__icontains=query) |
                                 Q(subject__icontains=query))
    if subject:
        courses = courses.filter(subject__iexact=subject)
    if language in dict(Course.LANGUAGES):
        courses = courses.filter(language=language)
    order = request.GET.get('order')
    courses = courses.order_by('-enrollments_count', '-updated', '-id') if order == 'popular' else \
        courses.order_by('-updated', '-id')
    page = Paginator(courses, CATALOG_PAGE).get_page(request.GET.get('page'))
    subjects = cache.get('co:subjects')
    if subjects is None:
        subjects = list(visible_courses().exclude(subject='').values('subject').annotate(c=Count('id'))
                        .order_by('-c').values_list('subject', flat=True)[:20])
        cache.set('co:subjects', subjects, 300)
    return render(request, 'courses/catalog.html', {
        'title': _('Курсы'), 'page': page, 'query': query, 'subject': subject, 'subjects': subjects,
        'order': order or 'new', 'lang': language, 'closed': section_closed(),
        'can_teach': can_teach(request.user),
    })


@login_required
def my_courses(request):
    profile = request.profile
    learning = []
    for enrollment in CourseEnrollment.objects.filter(profile=profile, course__is_deleted=False) \
            .select_related('course__author__user', 'last_lesson').order_by('-joined'):
        course = enrollment.course
        progress = logic.build_progress(enrollment)
        learning.append({'enrollment': enrollment, 'course': course, 'progress': progress,
                         'visible': course.can_view(request.user)})
    teaching = course_stats(Course.objects.filter(Q(author=profile) | Q(coauthors=profile), is_deleted=False)
                            .distinct()).order_by('-updated')
    waiting = CourseWork.objects.filter(
        status=CourseWork.PENDING, block__lesson__course__in=[c.id for c in teaching]).values(
        'block__lesson__course').annotate(c=Count('id'))
    waiting = {row['block__lesson__course']: row['c'] for row in waiting}
    for course in teaching:
        course.waiting = waiting.get(course.id, 0)
    return render(request, 'courses/my.html', {
        'title': _('Мои курсы'), 'learning': learning, 'teaching': teaching, 'can_teach': can_teach(request.user),
    })


# ---------------------------------------------------------------- course page

def get_enrollment(request, course):
    if not request.user.is_authenticated:
        return None
    return CourseEnrollment.objects.filter(course=course, profile=request.profile).first()


def structure(course, lessons):
    """Lessons grouped by module for the program: [(module or None, [lessons])]."""
    groups, index = [], {}
    for lesson in lessons:
        key = lesson.module_id
        if key not in index:
            index[key] = (lesson.module, [])
            groups.append(index[key])
        index[key][1].append(lesson)
    return groups


def course_detail(request, key):
    course = get_course(request, key)
    can_edit = course.can_edit(request.user)
    lessons = logic.ordered_lessons(course, drafts=can_edit)
    enrollment = get_enrollment(request, course)
    progress = logic.build_progress(enrollment, [x for x in lessons if not x.is_draft]) if enrollment else None
    reviews = course.reviews.select_related('profile__user')
    summary = reviews.aggregate(avg=Avg('rating'), n=Count('id'))
    mine = reviews.filter(profile=request.profile).first() if request.user.is_authenticated else None
    first = next((x for x in lessons if not x.is_draft), None)
    return render(request, 'courses/detail.html', {
        'title': course.title, 'course': course, 'groups': structure(course, lessons), 'enrollment': enrollment,
        'progress': progress, 'can_edit': can_edit, 'lesson_total': sum(1 for x in lessons if not x.is_draft),
        'reviews': reviews[:20], 'summary': summary, 'my_review': mine, 'first': first,
        'closed': section_closed(), 'can_review': enrollment is not None and course.reviews_on, 'now': timezone.now(),
        'authors': [course.author] + list(course.coauthors.select_related('user')),
        'can_copy': can_edit, 'can_delete': course.can_delete(request.user),
    })


@login_required
@require_POST
def enroll(request, key):
    course = get_course(request, key)
    blocked = guard_write(request)
    if blocked:
        return blocked
    if course.status != Course.PUBLISHED:
        return message(request, _('Курс ещё не опубликован.'), reverse('course_detail', args=[key]))
    with transaction.atomic():
        _enrollment, created = CourseEnrollment.objects.get_or_create(course=course, profile=request.profile)
        if created:
            Course.objects.filter(id=course.id).update(enrollments_count=F('enrollments_count') + 1)
    return redirect('course_learn', key=key)


@login_required
@require_POST
def unenroll(request, key):
    course = get_course(request, key)
    blocked = guard_write(request)
    if blocked:
        return blocked
    enrollment = get_enrollment(request, course)
    if enrollment is not None and (enrollment.attempts.exists() or enrollment.submissions.exists()):
        # Leaving would wipe test attempts and works (and reset attempt limits).
        return message(request, _('Нельзя отписаться: у вас есть сданные тесты или задания.'),
                       reverse('course_detail', args=[key]))
    deleted = CourseEnrollment.objects.filter(course=course, profile=request.profile, completed_at=None).delete()[0]
    if deleted:
        Course.objects.filter(id=course.id, enrollments_count__gt=0) \
            .update(enrollments_count=F('enrollments_count') - 1)
    return redirect('course_detail', key=key)


@login_required
@require_POST
def rate(request, key):
    course = get_course(request, key)
    blocked = guard_write(request)
    if blocked:
        return blocked
    if not course.reviews_on or get_enrollment(request, course) is None:
        raise Http404()
    try:
        rating = min(5, max(1, int(request.POST.get('rating', '5'))))
    except ValueError:
        rating = 5
    CourseReview.objects.update_or_create(course=course, profile=request.profile, defaults={
        'rating': rating, 'text': request.POST.get('text', '').strip()[:2000]})
    return redirect(reverse('course_detail', args=[key]) + '#reviews')


# ---------------------------------------------------------------- lessons

def learn(request, key):
    """The next lesson to continue with."""
    course = get_course(request, key)
    enrollment = get_enrollment(request, course)
    lessons = [x for x in logic.ordered_lessons(course)]
    if not lessons:
        return message(request, _('В курсе пока нет уроков.'), reverse('course_detail', args=[key]))
    if enrollment is None:
        if not course.can_edit(request.user):
            return redirect('course_detail', key=key)
        return redirect('course_lesson', key=key, lesson_id=lessons[0].id)
    progress = logic.build_progress(enrollment, lessons)
    target = None
    if enrollment.last_lesson_id and enrollment.last_lesson_id in progress.available and \
            progress.available[enrollment.last_lesson_id] and not progress.complete[enrollment.last_lesson_id]:
        target = enrollment.last_lesson_id
    if target is None:
        target = next((x.id for x in lessons if progress.available[x.id] and not progress.complete[x.id]), None)
    if target is None:
        target = next((x.id for x in lessons if progress.available[x.id]), lessons[0].id)
    return redirect('course_lesson', key=key, lesson_id=target)


def test_context(request, block, state, enrollment, last_attempt_id):
    """Questions without answers for the form, plus the review of the last attempt."""
    shuffle = bool(logic.block_setting(block, 'shuffle', False))
    questions = logic.test_questions(block, shuffle)
    limit = int(logic.block_setting(block, 'attempts', 0))
    info = {'questions': questions, 'limit': limit, 'used': state.attempts if state else 0, 'last': None,
            'show': bool(logic.block_setting(block, 'show_answers', True)),
            'pass_percent': int(logic.block_setting(block, 'pass_percent', 0))}
    info['can_try'] = enrollment is not None and (limit == 0 or info['used'] < limit)
    if enrollment is not None:
        attempts = CourseAttempt.objects.filter(enrollment=enrollment, block=block)
        attempt = attempts.filter(id=last_attempt_id).first() if last_attempt_id else attempts.first()
        if attempt:
            results = {}
            for q in questions:
                results[q.id] = logic.check_answer(q, attempt.answers.get(str(q.id)), list(q.options.all()))
            info['last'] = {'attempt': attempt, 'results': results, 'answers': attempt.answers}
    return info


def lesson_blocks(request, lessons_blocks, progress, enrollment, last_attempt_id):
    items = []
    for block in lessons_blocks:
        item = {'block': block, 'state': progress.states.get(block.id) if progress else None}
        if block.type == CourseBlock.TEST:
            item['test'] = test_context(request, block, item['state'], enrollment, last_attempt_id)
        elif block.type == CourseBlock.ASSIGNMENT:
            item['allow_text'] = bool(logic.block_setting(block, 'allow_text', True))
            item['allow_file'] = bool(logic.block_setting(block, 'allow_file', True))
            item['work'] = item['state'].work if item['state'] else None
        elif block.type == CourseBlock.PROBLEM and block.problem_id:
            item['problem'] = block.problem
            item['pass_percent'] = int(logic.block_setting(block, 'pass_percent', 100))
        items.append(item)
    return items


def lesson(request, key, lesson_id):
    course = get_course(request, key)
    team = course.can_edit(request.user)
    enrollment = get_enrollment(request, course)
    current = get_object_or_404(CourseLesson, id=lesson_id, course=course)
    if current.is_draft and not team:
        raise Http404()
    if enrollment is None and not team:
        return redirect('course_detail', key=key)
    lessons = logic.ordered_lessons(course, drafts=team and enrollment is None)
    visible = [x for x in lessons if not x.is_draft]
    block_map = logic.blocks_by_lesson(course)
    progress = logic.build_progress(enrollment, visible, block_map) if enrollment else None
    if progress is None:
        # Preview for the team: everything open, nothing is saved.
        class Preview:
            states, complete, available, percent, score_percent = {}, {}, {}, 0, None
        progress_view = Preview()
        for x in lessons:
            progress_view.available[x.id] = True
            progress_view.complete[x.id] = False
    else:
        progress_view = progress
    if not progress_view.available.get(current.id, False) and not team:
        text = _('Урок откроется %s.') % timezone.localtime(current.open_at).strftime('%d.%m.%Y %H:%M') \
            if current.open_at and current.open_at > timezone.now() else _('Сначала пройдите предыдущие уроки.')
        return message(request, text, reverse('course_detail', args=[key]))
    if enrollment is not None:
        logic.touch_lesson(enrollment, current)
        if enrollment.last_lesson_id != current.id:
            CourseEnrollment.objects.filter(id=enrollment.id).update(last_lesson=current)
        progress = logic.build_progress(enrollment, visible, block_map)
        logic.refresh(enrollment, progress)
        progress_view = progress
    index = next((i for i, x in enumerate(lessons) if x.id == current.id), 0)
    previous = lessons[index - 1] if index > 0 else None
    following = lessons[index + 1] if index + 1 < len(lessons) else None
    last_attempt = request.GET.get('attempt')
    items = lesson_blocks(request, block_map.get(current.id, []), progress, enrollment,
                          int(last_attempt) if last_attempt and last_attempt.isdigit() else None)
    comments = list(CourseComment.objects.filter(lesson=current).select_related('author__user'))
    roots = [c for c in comments if c.parent_id is None]
    replies = {}
    for c in comments:
        if c.parent_id:
            replies.setdefault(c.parent_id, []).append(c)
    is_closed = logic.lesson_is_closed(current)
    return render(request, 'courses/learn.html', {
        'title': current.title, 'course': course, 'lesson': current, 'groups': structure(course, lessons),
        'items': items, 'enrollment': enrollment, 'progress': progress_view, 'team': team,
        'preview': enrollment is None, 'previous': previous, 'following': following, 'roots': roots,
        'replies': replies, 'closed': is_closed, 'comment_error': None,
        'marked': bool(progress and current.id in progress.progress and progress.progress[current.id].marked_at),
        'complete': progress_view.complete.get(current.id, False), 'draft': current.is_draft,
        'finished': enrollment is not None and enrollment.completed_at is not None,
        'certificate': enrollment.certificate_code if enrollment else None,
        'disabled': section_closed(),
    })


def learner_context(request, key, lesson_id):
    """(course, enrollment, lesson) for learner actions; None when the learner may not act."""
    course = get_course(request, key)
    enrollment = get_enrollment(request, course)
    current = get_object_or_404(CourseLesson, id=lesson_id, course=course, is_draft=False)
    return course, enrollment, current


def back_to(key, lesson_id, anchor='', **params):
    url = reverse('course_lesson', args=[key, lesson_id])
    if params:
        url += '?' + '&'.join('%s=%s' % kv for kv in params.items())
    return url + anchor


@login_required
@require_POST
def mark(request, key, lesson_id):
    course, enrollment, current = learner_context(request, key, lesson_id)
    blocked = guard_write(request)
    if blocked:
        return blocked
    if enrollment is None:
        return redirect('course_detail', key=key)
    progress = logic.build_progress(enrollment)
    if not progress.available.get(current.id):
        raise Http404()
    logic.touch_lesson(enrollment, current, mark=True)
    logic.refresh(enrollment)
    return redirect('course_lesson', key=key, lesson_id=lesson_id)


@login_required
@require_POST
def submit_test(request, key, lesson_id, block_id):
    course, enrollment, current = learner_context(request, key, lesson_id)
    block = get_object_or_404(CourseBlock, id=block_id, lesson=current, type=CourseBlock.TEST)
    blocked = guard_write(request)
    if blocked:
        return blocked
    if enrollment is None:
        return redirect('course_detail', key=key)
    progress = logic.build_progress(enrollment)
    if not progress.available.get(current.id):
        raise Http404()
    if logic.lesson_is_closed(current):
        return message(request, _('Срок сдачи прошёл.'), back_to(key, lesson_id))
    limit = int(logic.block_setting(block, 'attempts', 0))
    with transaction.atomic():
        used = CourseAttempt.objects.select_for_update().filter(enrollment=enrollment, block=block).count()
        if limit and used >= limit:
            return message(request, _('Попытки закончились.'), back_to(key, lesson_id, '#block-%d' % block.id))
        questions = list(block.questions.all())
        answers = logic.read_answers(questions, request.POST)
        score, total, _results = logic.grade_test(block, answers)
        attempt = CourseAttempt.objects.create(enrollment=enrollment, block=block, answers=answers,
                                               score=score, total=total)
    logic.touch_lesson(enrollment, current)
    logic.refresh(enrollment)
    return redirect(back_to(key, lesson_id, '#block-%d' % block.id, attempt=attempt.id))


def clean_work_file(upload):
    """(ok, error). Files of learners: limited in size and kind, never served as pages."""
    ext = os.path.splitext(upload.name)[1].lower()
    if ext not in WORK_EXT:
        return _('Этот тип файла не принимается.')
    if upload.size > WORK_MAX:
        return _('Файл больше 10 МБ.')
    return None


@login_required
@require_POST
def submit_work(request, key, lesson_id, block_id):
    course, enrollment, current = learner_context(request, key, lesson_id)
    block = get_object_or_404(CourseBlock, id=block_id, lesson=current, type=CourseBlock.ASSIGNMENT)
    blocked = guard_write(request)
    if blocked:
        return blocked
    if enrollment is None:
        return redirect('course_detail', key=key)
    progress = logic.build_progress(enrollment)
    if not progress.available.get(current.id):
        raise Http404()
    back = back_to(key, lesson_id, '#block-%d' % block.id)
    if logic.lesson_is_closed(current):
        return message(request, _('Срок сдачи прошёл.'), back)
    last = CourseWork.objects.filter(enrollment=enrollment, block=block).first()
    if last is not None and last.status == CourseWork.GRADED:
        return message(request, _('Работа уже оценена.'), back)
    text = request.POST.get('text', '').strip()[:20000]
    upload = request.FILES.get('file')
    if not logic.block_setting(block, 'allow_text', True):
        text = ''
    if not logic.block_setting(block, 'allow_file', True):
        upload = None
    if not text and upload is None:
        return message(request, _('Напишите ответ или приложите файл.'), back)
    if upload is not None:
        error = clean_work_file(upload)
        if error:
            return message(request, error, back)
    work = CourseWork(enrollment=enrollment, block=block, text=text)
    if upload is not None:
        work.file_name = os.path.basename(upload.name)[:120]
        work.file = upload
    work.save()
    logic.touch_lesson(enrollment, current)
    return redirect(back)


@login_required
@require_POST
def add_comment(request, key, lesson_id):
    course = get_course(request, key)
    current = get_object_or_404(CourseLesson, id=lesson_id, course=course)
    blocked = guard_write(request)
    if blocked:
        return blocked
    team = course.can_edit(request.user)
    if get_enrollment(request, course) is None and not team:
        raise Http404()
    if current.is_draft and not team:
        raise Http404()
    if not team and not logic.build_progress(get_enrollment(request, course)).available.get(current.id):
        raise Http404()
    text = request.POST.get('text', '').strip()[:3000]
    parent = None
    if request.POST.get('parent', '').isdigit():
        parent = CourseComment.objects.filter(id=int(request.POST['parent']), lesson=current, parent=None).first()
    if text and not request.profile.mute:
        CourseComment.objects.create(lesson=current, author=request.profile, text=text, parent=parent)
    return redirect(back_to(key, lesson_id, '#comments'))


@login_required
@require_POST
def delete_comment(request, key, comment_id):
    course = get_course(request, key)
    comment = get_object_or_404(CourseComment, id=comment_id, lesson__course=course)
    if comment.author_id == request.profile.id or course.can_edit(request.user):
        lesson_id = comment.lesson_id
        comment.delete()
        return redirect(back_to(key, lesson_id, '#comments'))
    raise Http404()


# ---------------------------------------------------------------- files (served only to those who may see them)

def send_file(field, name=None):
    if not field:
        raise Http404()
    try:
        handle = field.open('rb')
    except (FileNotFoundError, ValueError):
        raise Http404()
    response = FileResponse(handle, as_attachment=True, filename=name or os.path.basename(field.name))
    response['X-Content-Type-Options'] = 'nosniff'
    response['Content-Security-Policy'] = "default-src 'none'; sandbox"
    return response


@login_required
def block_file(request, key, block_id):
    course = get_course(request, key)
    block = get_object_or_404(CourseBlock, id=block_id, lesson__course=course, type=CourseBlock.FILE)
    if block.lesson.is_draft and not course.can_edit(request.user):
        raise Http404()
    if not course.can_edit(request.user):
        enrollment = get_enrollment(request, course)
        if enrollment is None or not logic.build_progress(enrollment).available.get(block.lesson_id):
            raise Http404()
    return send_file(block.file, block.title and (block.title + os.path.splitext(block.file.name)[1]))


@login_required
def work_file(request, key, work_id):
    course = get_course(request, key)
    work = get_object_or_404(CourseWork.objects.select_related('enrollment'), id=work_id,
                             block__lesson__course=course)
    if work.enrollment.profile_id != request.profile.id and not course.can_edit(request.user):
        raise Http404()
    return send_file(work.file, work.file_name)


# ---------------------------------------------------------------- certificate

def certificate_enrollment(code):
    return get_object_or_404(CourseEnrollment.objects.select_related('course__author__user', 'profile__user'),
                             certificate_code=code.upper(), course__is_deleted=False, completed_at__isnull=False)


def certificate_page(request, code):
    enrollment = certificate_enrollment(code)
    return render(request, 'courses/certificate.html', {
        'title': _('Сертификат'), 'enrollment': enrollment, 'course': enrollment.course,
        'code': enrollment.certificate_code,
        'is_owner': request.user.is_authenticated and request.profile.id == enrollment.profile_id,
    })


def certificate_qr(request, code):
    import qrcode
    import qrcode.image.svg
    enrollment = certificate_enrollment(code)
    url = request.build_absolute_uri(reverse('course_certificate', args=[enrollment.certificate_code]))
    image = qrcode.make(url, image_factory=qrcode.image.svg.SvgPathImage, box_size=10, border=1)
    buf = BytesIO()
    image.save(buf)
    response = HttpResponse(buf.getvalue(), content_type='image/svg+xml')
    response['Cache-Control'] = 'public, max-age=3600'
    return response


def certificate_pdf(request, code):
    from judge.utils.course_certificate import render_certificate
    enrollment = certificate_enrollment(code)
    url = request.build_absolute_uri(reverse('course_certificate', args=[enrollment.certificate_code]))
    data = render_certificate(enrollment, url)
    response = HttpResponse(data, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="certificate-%s.pdf"' % enrollment.certificate_code
    return response
