"""Courses, teacher side: creating, the program and lesson editor, gradebook, grading, export, copy and delete."""
import os
from io import BytesIO

from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, Exists, OuterRef
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from judge.models import Course, CourseBlock, CourseEnrollment, CourseLesson, CourseModule, CourseOption, \
    CourseQuestion, CourseWork, Organization, Problem, Profile
from judge.models.course import new_key, youtube_id
from judge.utils import course_logic as logic
from judge.utils import quiz_images as images
from judge.views.course import can_teach, get_course, guard_write, message, section_closed

FILE_MAX = 25 * 1024 * 1024
FILE_EXT = {'.pdf', '.doc', '.docx', '.odt', '.xls', '.xlsx', '.ods', '.ppt', '.pptx', '.zip', '.7z', '.rar', '.txt',
            '.md', '.csv', '.json', '.png', '.jpg', '.jpeg', '.gif', '.webp', '.py', '.cpp', '.c', '.h', '.java',
            '.cs', '.js', '.go', '.kt', '.pas', '.ipynb', '.sql', '.mp3', '.mp4', '.webm'}
GRADE_PAGE = 40
STUDENT_PAGE = 40


class EditError(Exception):
    pass


def number(value, low, high, default):
    try:
        return min(high, max(low, int(float(str(value).replace(',', '.')))))
    except (TypeError, ValueError):
        return default


def checked(request, name):
    return request.POST.get(name) in ('1', 'on', 'true', 'yes')


def read_datetime(request, name):
    raw = request.POST.get(name, '').strip()
    if not raw:
        return None
    try:
        naive = timezone.datetime.strptime(raw, '%Y-%m-%dT%H:%M')
    except ValueError:
        raise EditError(_('Неверная дата.'))
    return timezone.make_aware(naive)


def store_image(instance, field, upload):
    """Re-encodes a picture with Pillow (no scripts, limited size) and stores it in the model's folder."""
    try:
        data, ext = images.process(upload)
    except images.ImageError as error:
        raise EditError(str(error))
    old = getattr(instance, field)
    getattr(instance, field).save('image.' + ext, ContentFile(data), save=False)
    if old and old.name != getattr(instance, field).name:
        images.delete_file(old)


def store_file(instance, field, upload):
    ext = os.path.splitext(upload.name)[1].lower()
    if ext not in FILE_EXT:
        raise EditError(_('Этот тип файла не принимается.'))
    if upload.size > FILE_MAX:
        raise EditError(_('Файл больше 25 МБ.'))
    old = getattr(instance, field)
    getattr(instance, field).save(upload.name, upload, save=False)
    if old and old.name != getattr(instance, field).name:
        images.delete_file(old)


def clone_file(field):
    """A copy of a stored file, so that a copied course never shares files with the original."""
    if not field:
        return None
    try:
        with field.open('rb') as handle:
            return ContentFile(handle.read(), name=os.path.basename(field.name))
    except (FileNotFoundError, ValueError):
        return None


def renumber(items, target_id, direction):
    """Move the item with `target_id` one step up or down within an ordered list and renumber."""
    items = list(items)
    ids = [x.id for x in items]
    if target_id not in ids:
        return
    i = ids.index(target_id)
    j = i - 1 if direction == 'up' else i + 1
    if 0 <= j < len(items):
        items[i], items[j] = items[j], items[i]
    for n, item in enumerate(items):
        if item.order != n:
            type(item).objects.filter(id=item.id).update(order=n)


def new_order(queryset):
    last = queryset.order_by('-order').values_list('order', flat=True).first()
    return 0 if last is None else last + 1


# ---------------------------------------------------------------- create and edit

@login_required
def new_course(request):
    if not can_teach(request.user):
        return message(request, _('Создавать курсы могут преподаватели. Статус даёт администратор сайта.'),
                       reverse('course_catalog'), 403)
    if request.method == 'POST':
        blocked = guard_write(request)
        if blocked:
            return blocked
        title = request.POST.get('title', '').strip()[:120]
        if not title:
            return message(request, _('Назовите курс.'), reverse('course_new'))
        language = request.POST.get('language')
        course = Course.objects.create(
            author=request.profile, title=title, subject=request.POST.get('subject', '').strip()[:60],
            language=language if language in dict(Course.LANGUAGES) else 'ru', key=new_key())
        return redirect('course_edit', key=course.key)
    return render(request, 'courses/new.html', {'title': _('Новый курс'), 'languages': Course.LANGUAGES})


@login_required
def edit(request, key):
    course = get_course(request, key, edit=True)
    lessons = logic.ordered_lessons(course, drafts=True)
    counts = dict(CourseLesson.objects.filter(course=course).annotate(n=Count('blocks')).values_list('id', 'n'))
    groups, index = [], {}
    for module in course.modules.all():
        index[module.id] = (module, [])
    flat = []
    for item in lessons:
        item.block_count = counts.get(item.id, 0)
        (index[item.module_id][1] if item.module_id in index else flat).append(item)
    orgs = Organization.objects.all() if Course.is_admin(request.user) else request.profile.organizations.all()
    coauthors = ', '.join(c.user.username for c in course.coauthors.select_related('user'))
    return render(request, 'courses/edit.html', {
        'title': course.title, 'course': course, 'flat': flat, 'modules': list(index.values()), 'groups': groups,
        'organizations': orgs, 'coauthors': coauthors, 'languages': Course.LANGUAGES,
        'is_owner': course.is_owner(request.user) or Course.is_admin(request.user),
        'pending': CourseWork.objects.filter(block__lesson__course=course, status=CourseWork.PENDING).count(),
        'disabled': section_closed(), 'lesson_count': len(lessons),
        'learners': course.enrollments_count,
    })


@login_required
def edit_lesson(request, key, lesson_id):
    course = get_course(request, key, edit=True)
    lesson = get_object_or_404(CourseLesson, id=lesson_id, course=course)
    blocks = list(lesson.blocks.prefetch_related('questions__options'))

    def local(dt):
        return timezone.localtime(dt).strftime('%Y-%m-%dT%H:%M') if dt else ''

    return render(request, 'courses/lesson_edit.html', {
        'title': lesson.title, 'course': course, 'lesson': lesson, 'blocks': blocks, 'types': CourseBlock.TYPES,
        'modules': course.modules.all(), 'open_at': local(lesson.open_at), 'deadline': local(lesson.deadline),
        'qtypes': CourseQuestion.TYPES, 'disabled': section_closed(),
        'cfgs': {b.id: {'attempts': logic.block_setting(b, 'attempts', 0),
                        'pass_percent': logic.block_setting(b, 'pass_percent',
                                                            100 if b.type == CourseBlock.PROBLEM else 0),
                        'shuffle': logic.block_setting(b, 'shuffle', False),
                        'show_answers': logic.block_setting(b, 'show_answers', True),
                        'allow_text': logic.block_setting(b, 'allow_text', True),
                        'allow_file': logic.block_setting(b, 'allow_file', True)} for b in blocks},
        'error': request.GET.get('error', '')[:200],
    })


# ---------------------------------------------------------------- actions (one POST endpoint, one handler each)

def act_course_save(request, course):
    post = request.POST
    title = post.get('title', '').strip()[:120]
    if not title:
        raise EditError(_('Назовите курс.'))
    course.title = title
    course.subject = post.get('subject', '').strip()[:60]
    course.description = post.get('description', '').strip()[:10000]
    if post.get('language') in dict(Course.LANGUAGES):
        course.language = post['language']
    access = post.get('access')
    if access in (Course.PUBLIC, Course.LINK, Course.ORG):
        course.access = access
    org = None
    if course.access == Course.ORG:
        pool = Organization.objects.all() if Course.is_admin(request.user) else request.profile.organizations.all()
        org = pool.filter(id=number(post.get('organization'), 0, 10 ** 9, 0)).first()
        if org is None and 'organization' not in post and course.organization_id:
            org = course.organization  # a coauthor from elsewhere saves the course without moving it
        if org is None:
            raise EditError(_('Выберите организацию.'))
    course.organization = org
    course.sequential = checked(request, 'sequential')
    course.certificate = checked(request, 'certificate')
    course.reviews_on = checked(request, 'reviews_on')
    course.pass_percent = number(post.get('pass_percent'), 0, 100, 0)
    status = post.get('status')
    if status in (Course.DRAFT, Course.PUBLISHED):
        course.status = status
    if post.get('remove_cover') and course.cover:
        images.delete_file(course.cover)
        course.cover = ''
    if request.FILES.get('cover'):
        store_image(course, 'cover', request.FILES['cover'])
    if (course.is_owner(request.user) or Course.is_admin(request.user)) and 'coauthors' in post:
        names = [n.strip() for n in post['coauthors'].replace(';', ',').split(',') if n.strip()][:10]
        profiles = list(Profile.objects.filter(user__username__in=names).exclude(id=course.author_id))
        missing = set(n.lower() for n in names) - set(p.user.username.lower() for p in profiles)
        if missing:
            raise EditError(_('Нет пользователя: %s') % ', '.join(sorted(missing)))
        course.coauthors.set(profiles)
    course.save()


def act_module_add(request, course):
    title = request.POST.get('title', '').strip()[:120]
    if not title:
        raise EditError(_('Назовите модуль.'))
    CourseModule.objects.create(course=course, title=title, order=new_order(course.modules))


def get_module(course, request):
    return get_object_or_404(CourseModule, id=number(request.POST.get('module'), 0, 10 ** 9, 0), course=course)


def act_module_save(request, course):
    module = get_module(course, request)
    title = request.POST.get('title', '').strip()[:120]
    if title:
        module.title = title
        module.save(update_fields=['title'])


def act_module_delete(request, course):
    # Lessons of a deleted module stay in the course, outside modules.
    get_module(course, request).delete()


def act_module_move(request, course):
    module = get_module(course, request)
    renumber(course.modules.all(), module.id, request.POST.get('dir'))


def get_lesson(course, request, name='lesson'):
    return get_object_or_404(CourseLesson, id=number(request.POST.get(name), 0, 10 ** 9, 0), course=course)


def act_lesson_add(request, course):
    title = request.POST.get('title', '').strip()[:160] or _('Новый урок')
    module = None
    if request.POST.get('module'):
        module = get_module(course, request)
    siblings = CourseLesson.objects.filter(course=course, module=module)
    lesson = CourseLesson.objects.create(course=course, module=module, title=title, order=new_order(siblings),
                                         is_draft=True)
    return reverse('course_edit_lesson', args=[course.key, lesson.id])


def act_lesson_save(request, course):
    lesson = get_lesson(course, request)
    post = request.POST
    title = post.get('title', '').strip()[:160]
    if not title:
        raise EditError(_('Назовите урок.'))
    lesson.title = title
    module = None
    if post.get('module'):
        module = get_module(course, request)
    if module != lesson.module:
        lesson.module = module
        lesson.order = new_order(CourseLesson.objects.filter(course=course, module=module))
    lesson.is_draft = checked(request, 'is_draft')
    lesson.is_required = checked(request, 'is_required')
    lesson.mark_required = checked(request, 'mark_required')
    lesson.open_at = read_datetime(request, 'open_at')
    lesson.deadline = read_datetime(request, 'deadline')
    lesson.save()
    return reverse('course_edit_lesson', args=[course.key, lesson.id])


def act_lesson_publish(request, course):
    """Open or hide a lesson from the program list."""
    lesson = get_lesson(course, request)
    lesson.is_draft = not lesson.is_draft
    lesson.save(update_fields=['is_draft'])


def act_lesson_delete(request, course):
    get_lesson(course, request).delete()


def act_lesson_move(request, course):
    lesson = get_lesson(course, request)
    siblings = CourseLesson.objects.filter(course=course, module=lesson.module).order_by('order', 'id')
    renumber(siblings, lesson.id, request.POST.get('dir'))


def get_block(course, request):
    return get_object_or_404(CourseBlock, id=number(request.POST.get('block'), 0, 10 ** 9, 0), lesson__course=course)


def back_lesson(course, lesson_id, anchor=''):
    return reverse('course_edit_lesson', args=[course.key, lesson_id]) + anchor


def act_block_add(request, course):
    lesson = get_lesson(course, request)
    kind = request.POST.get('type')
    if kind not in dict(CourseBlock.TYPES):
        raise Http404()
    block = CourseBlock.objects.create(lesson=lesson, type=kind, order=new_order(lesson.blocks),
                                       points=10, data={})
    if kind == CourseBlock.TEST:
        question = CourseQuestion.objects.create(block=block, text=_('Вопрос'), type=CourseQuestion.SINGLE)
        CourseOption.objects.bulk_create([CourseOption(question=question, order=0, text=_('Верный ответ'),
                                                       is_correct=True),
                                          CourseOption(question=question, order=1, text=_('Неверный ответ'))])
    return back_lesson(course, lesson.id, '#block-%d' % block.id)


def act_block_save(request, course):
    block = get_block(course, request)
    post = request.POST
    block.title = post.get('title', '').strip()[:200]
    block.text = post.get('text', '').strip()[:30000]
    block.is_required = checked(request, 'is_required')
    data = dict(block.data or {})
    if block.type == CourseBlock.VIDEO:
        raw = post.get('video', '').strip()
        block.youtube_id = youtube_id(raw)
        if raw and not block.youtube_id:
            raise EditError(_('Это не ссылка на YouTube.'))
    elif block.type == CourseBlock.IMAGE:
        if post.get('remove_image') and block.image:
            images.delete_file(block.image)
            block.image = ''
        if request.FILES.get('image'):
            store_image(block, 'image', request.FILES['image'])
    elif block.type == CourseBlock.FILE:
        if request.FILES.get('file'):
            store_file(block, 'file', request.FILES['file'])
    elif block.type == CourseBlock.TEST:
        data.update(attempts=number(post.get('attempts'), 0, 100, 0),
                    pass_percent=number(post.get('pass_percent'), 0, 100, 0),
                    shuffle=checked(request, 'shuffle'), show_answers=checked(request, 'show_answers'))
    elif block.type == CourseBlock.ASSIGNMENT:
        block.points = number(post.get('points'), 1, 1000, 10)
        data.update(pass_percent=number(post.get('pass_percent'), 0, 100, 0), allow_text=checked(request, 'allow_text'),
                    allow_file=checked(request, 'allow_file'))
        if not data['allow_text'] and not data['allow_file']:
            raise EditError(_('Нужен хотя бы один способ ответа: текст или файл.'))
    elif block.type == CourseBlock.PROBLEM:
        code = post.get('problem_code', '').strip()
        block.problem = None
        if code:
            problem = Problem.objects.filter(code=code).first()
            if problem is None or not problem.is_accessible_by(request.user):
                raise EditError(_('Задача не найдена: %s') % code)
            block.problem = problem
        block.points = number(post.get('points'), 1, 1000, 10)
        data.update(pass_percent=number(post.get('pass_percent'), 1, 100, 100))
    block.data = data
    block.save()
    return back_lesson(course, block.lesson_id, '#block-%d' % block.id)


def act_block_delete(request, course):
    block = get_block(course, request)
    lesson_id = block.lesson_id
    for field in (block.image, block.file):
        images.delete_file(field)
    block.delete()
    return back_lesson(course, lesson_id)


def act_block_move(request, course):
    block = get_block(course, request)
    renumber(block.lesson.blocks.all(), block.id, request.POST.get('dir'))
    return back_lesson(course, block.lesson_id, '#block-%d' % block.id)


def get_question(course, request):
    return get_object_or_404(CourseQuestion, id=number(request.POST.get('question'), 0, 10 ** 9, 0),
                             block__lesson__course=course, block__type=CourseBlock.TEST)


def act_question_add(request, course):
    block = get_block(course, request)
    if block.type != CourseBlock.TEST:
        raise Http404()
    if block.questions.count() >= 100:
        raise EditError(_('Слишком много вопросов.'))
    question = CourseQuestion.objects.create(block=block, text=_('Вопрос'), order=new_order(block.questions))
    CourseOption.objects.bulk_create([CourseOption(question=question, order=0, text=_('Верный ответ'), is_correct=True),
                                      CourseOption(question=question, order=1, text=_('Неверный ответ'))])
    return back_lesson(course, block.lesson_id, '#question-%d' % question.id)


def act_question_save(request, course):
    question = get_question(course, request)
    post = request.POST
    text = post.get('text', '').strip()[:3000]
    if not text:
        raise EditError(_('Напишите вопрос.'))
    kind = post.get('qtype')
    if kind not in dict(CourseQuestion.TYPES):
        kind = question.type
    rows = []
    for i in range(12):
        option_text = post.get('opt_%d_text' % i, '').strip()[:300]
        if option_text:
            rows.append((option_text, checked(request, 'opt_%d_ok' % i)))
    if kind in (CourseQuestion.NUMBER, CourseQuestion.TEXT):
        rows = [(t, True) for t, _ok in rows]
        if not rows:
            raise EditError(_('Укажите верный ответ.'))
        if kind == CourseQuestion.NUMBER and any(logic.to_number(t) is None for t, _ok in rows):
            raise EditError(_('Ответ должен быть числом.'))
    else:
        right = sum(1 for _t, ok in rows if ok)
        if len(rows) < 2:
            raise EditError(_('Нужно минимум два варианта.'))
        if kind == CourseQuestion.SINGLE and right != 1:
            raise EditError(_('Отметьте один верный вариант.'))
        if kind == CourseQuestion.MULTI and right < 1:
            raise EditError(_('Отметьте хотя бы один верный вариант.'))
    with transaction.atomic():
        question.text, question.type = text, kind
        question.explanation = post.get('explanation', '').strip()[:2000]
        question.points = number(post.get('points'), 1, 100, 1)
        question.save()
        question.options.all().delete()
        CourseOption.objects.bulk_create([CourseOption(question=question, order=n, text=t, is_correct=ok)
                                          for n, (t, ok) in enumerate(rows)])
    return back_lesson(course, question.block.lesson_id, '#question-%d' % question.id)


def act_question_delete(request, course):
    question = get_question(course, request)
    lesson_id = question.block.lesson_id
    question.delete()
    return back_lesson(course, lesson_id)


def act_question_move(request, course):
    question = get_question(course, request)
    renumber(question.block.questions.all(), question.id, request.POST.get('dir'))
    return back_lesson(course, question.block.lesson_id, '#question-%d' % question.id)


ACTIONS = {
    'course_save': act_course_save, 'module_add': act_module_add, 'module_save': act_module_save,
    'module_delete': act_module_delete, 'module_move': act_module_move, 'lesson_add': act_lesson_add,
    'lesson_save': act_lesson_save, 'lesson_publish': act_lesson_publish, 'lesson_delete': act_lesson_delete,
    'lesson_move': act_lesson_move, 'block_add': act_block_add, 'block_save': act_block_save,
    'block_delete': act_block_delete, 'block_move': act_block_move, 'question_add': act_question_add,
    'question_save': act_question_save, 'question_delete': act_question_delete, 'question_move': act_question_move,
}


@login_required
@require_POST
def edit_do(request, key):
    course = get_course(request, key, edit=True)
    blocked = guard_write(request)
    if blocked:
        return blocked
    handler = ACTIONS.get(request.POST.get('action', ''))
    if handler is None:
        raise Http404()
    try:
        with transaction.atomic():
            target = handler(request, course)
    except EditError as error:
        return message(request, str(error), request.POST.get('back') if is_local(request.POST.get('back')) else
                       reverse('course_edit', args=[key]))
    Course.objects.filter(id=course.id).update(updated=timezone.now())
    back = request.POST.get('back')
    return redirect(target or (back if is_local(back) else reverse('course_edit', args=[key])))


def is_local(url):
    return bool(url) and url.startswith('/') and not url.startswith('//')


# ---------------------------------------------------------------- learners and grading

def student_rows(course, enrollments, lessons=None, blocks=None):
    lessons = lessons if lessons is not None else logic.ordered_lessons(course)
    blocks = blocks if blocks is not None else logic.blocks_by_lesson(course)
    rows = []
    for enrollment in enrollments:
        progress = logic.build_progress(enrollment, lessons, blocks)
        rows.append({'enrollment': enrollment, 'progress': progress})
    return rows


@login_required
def students(request, key):
    course = get_course(request, key, edit=True)
    query = request.GET.get('q', '').strip()[:60]
    enrollments = CourseEnrollment.objects.filter(course=course).select_related('profile__user')
    if query:
        enrollments = enrollments.filter(profile__user__username__icontains=query)
    sort = request.GET.get('sort')
    enrollments = enrollments.order_by('profile__user__username' if sort == 'name' else '-joined', '-id')
    page = Paginator(enrollments, STUDENT_PAGE).get_page(request.GET.get('page'))
    lessons = logic.ordered_lessons(course)
    rows = student_rows(course, page.object_list, lessons)
    return render(request, 'courses/students.html', {
        'title': _('Слушатели: %s') % course.title, 'course': course, 'page': page, 'rows': rows, 'query': query,
        'lessons': lessons, 'sort': sort or 'new', 'total': course.enrollments_count,
        'finished': CourseEnrollment.objects.filter(course=course, completed_at__isnull=False).count(),
        'pending': CourseWork.objects.filter(block__lesson__course=course, status=CourseWork.PENDING).count(),
    })


@login_required
def students_xlsx(request, key):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill
    course = get_course(request, key, edit=True)
    lessons = logic.ordered_lessons(course)
    blocks = logic.blocks_by_lesson(course)
    book = Workbook()
    sheet = book.active
    sheet.title = _('Слушатели')[:30]
    sheet.append([_('Пользователь'), _('Записан'), _('Прогресс, %'), _('Балл, %'), _('Завершён'), _('Сертификат')] +
                 [x.title[:30] for x in lessons])
    green = PatternFill('solid', fgColor='C8EED9')
    enrollments = CourseEnrollment.objects.filter(course=course).select_related('profile__user') \
        .order_by('profile__user__username')
    for r, row in enumerate(student_rows(course, enrollments, lessons, blocks), 2):
        enrollment, progress = row['enrollment'], row['progress']
        sheet.append([enrollment.profile.user.username, timezone.localtime(enrollment.joined).strftime('%d.%m.%Y'),
                      progress.percent, progress.score_percent if progress.score_percent is not None else '',
                      timezone.localtime(enrollment.completed_at).strftime('%d.%m.%Y')
                      if enrollment.completed_at else '',
                      enrollment.certificate_code or ''] +
                     ['✓' if progress.complete.get(x.id) else '' for x in lessons])
        for c, lesson in enumerate(lessons, 7):
            if progress.complete.get(lesson.id):
                sheet.cell(row=r, column=c).fill = green
    for cell in sheet[1]:
        cell.font = Font(bold=True)
    works = book.create_sheet(_('Задания')[:30])
    works.append([_('Пользователь'), _('Урок'), _('Задание'), _('Сдано'), _('Статус'), _('Оценка'), _('Комментарий')])
    for work in CourseWork.objects.filter(block__lesson__course=course).select_related(
            'enrollment__profile__user', 'block__lesson').order_by('enrollment__profile__user__username', 'submitted'):
        works.append([work.enrollment.profile.user.username, work.block.lesson.title, work.block.title or '',
                      timezone.localtime(work.submitted).strftime('%d.%m.%Y %H:%M'), work.get_status_display(),
                      work.grade if work.grade is not None else '', work.comment[:500]])
    for cell in works[1]:
        cell.font = Font(bold=True)
    buf = BytesIO()
    book.save(buf)
    response = HttpResponse(buf.getvalue(),
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="course-%s.xlsx"' % course.key
    return response


@login_required
def grading(request, key):
    course = get_course(request, key, edit=True)
    later = CourseWork.objects.filter(enrollment=OuterRef('enrollment'), block=OuterRef('block'),
                                      id__gt=OuterRef('id'))
    works = CourseWork.objects.filter(block__lesson__course=course).annotate(newer=Exists(later)) \
        .filter(newer=False).select_related('enrollment__profile__user', 'block__lesson')
    show = request.GET.get('show')
    works = works.filter(status=CourseWork.PENDING) if show != 'all' else works
    works = works.order_by('submitted' if show != 'all' else '-submitted', 'id')
    page = Paginator(works, GRADE_PAGE).get_page(request.GET.get('page'))
    return render(request, 'courses/grading.html', {
        'title': _('Проверка работ: %s') % course.title, 'course': course, 'page': page, 'show': show or 'new',
        'disabled': section_closed(),
    })


@login_required
@require_POST
def grade(request, key, work_id):
    course = get_course(request, key, edit=True)
    blocked = guard_write(request)
    if blocked:
        return blocked
    work = get_object_or_404(CourseWork.objects.select_related('enrollment__course', 'block'), id=work_id,
                             block__lesson__course=course)
    later = CourseWork.objects.filter(enrollment=work.enrollment, block=work.block, id__gt=work.id).exists()
    if later:
        return message(request, _('Слушатель уже прислал новую версию.'), reverse('course_grading', args=[key]))
    maximum = logic.block_max(work.block)
    work.comment = request.POST.get('comment', '').strip()[:5000]
    if request.POST.get('result') == 'return':
        work.status, work.grade = CourseWork.RETURNED, None
    else:
        try:
            value = float(request.POST.get('grade', '').replace(',', '.'))
        except ValueError:
            return message(request, _('Укажите оценку числом.'), reverse('course_grading', args=[key]))
        work.status, work.grade = CourseWork.GRADED, max(0.0, min(value, maximum))
    work.graded_by, work.graded_at = request.profile, timezone.now()
    work.save()
    logic.refresh(work.enrollment)
    back = request.POST.get('back')
    return redirect(back if is_local(back) else reverse('course_grading', args=[key]))


# ---------------------------------------------------------------- copy and delete

@login_required
@require_POST
def copy_course(request, key):
    course = get_course(request, key, edit=True)
    blocked = guard_write(request)
    if blocked:
        return blocked
    with transaction.atomic():
        copy = Course.objects.get(id=course.id)
        copy.pk, copy.id = None, None
        copy.key, copy.author, copy.status = new_key(), request.profile, Course.DRAFT
        copy.title = (_('Копия: %s') % course.title)[:120]
        copy.enrollments_count, copy.is_hidden, copy.is_deleted = 0, False, False
        cover = clone_file(course.cover)
        copy.cover = ''
        if cover:
            copy.cover.save(cover.name, cover, save=False)
        copy.save()
        modules = {}
        for module in course.modules.all():
            old = module.id
            module.pk, module.id, module.course = None, None, copy
            module.save()
            modules[old] = module
        for lesson in CourseLesson.objects.filter(course=course):
            blocks = list(lesson.blocks.prefetch_related('questions__options'))
            lesson.pk, lesson.id, lesson.course = None, None, copy
            lesson.module = modules.get(lesson.module_id)
            lesson.save()
            for block in blocks:
                questions = list(block.questions.all())
                image, attached = clone_file(block.image), clone_file(block.file)
                block.pk, block.id, block.lesson = None, None, lesson
                block.image = block.file = ''
                if image:
                    block.image.save(image.name, image, save=False)
                if attached:
                    block.file.save(attached.name, attached, save=False)
                block.save()
                for question in questions:
                    options = list(question.options.all())
                    question.pk, question.id, question.block = None, None, block
                    question.save()
                    for option in options:
                        option.pk, option.id, option.question = None, None, question
                    CourseOption.objects.bulk_create(options)
    return redirect('course_edit', key=copy.key)


@login_required
@require_POST
def delete_course(request, key):
    course = get_course(request, key)
    if not course.can_delete(request.user):
        raise Http404()
    blocked = guard_write(request)
    if blocked:
        return blocked
    Course.objects.filter(id=course.id).update(is_deleted=True)
    return redirect('course_my')
