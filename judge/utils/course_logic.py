"""Course rules in one place: what is open, what counts as done, test grading, the course score, certificates."""
import re
import secrets
from collections import defaultdict
from dataclasses import dataclass, field

from django.db.models import F, Max
from django.utils import timezone

from judge.models import CourseAttempt, CourseBlock, CourseEnrollment, CourseLesson, CourseProgress, CourseQuestion, \
    CourseWork, Submission

CERT_ALPHABET = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'


def ordered_lessons(course, drafts=False):
    """Lessons in reading order: those outside modules first, then module by module."""
    lessons = list(CourseLesson.objects.filter(course=course).select_related('module'))
    if not drafts:
        lessons = [lesson for lesson in lessons if not lesson.is_draft]
    lessons.sort(key=lambda x: (x.module.order if x.module_id else -1, x.module_id or 0, x.order, x.id))
    return lessons


def blocks_by_lesson(course):
    result = defaultdict(list)
    for block in CourseBlock.objects.filter(lesson__course=course).prefetch_related('questions'):
        result[block.lesson_id].append(block)
    for blocks in result.values():
        blocks.sort(key=lambda b: (b.order, b.id))
    return result


def block_max(block):
    if block.type == CourseBlock.TEST:
        return float(sum(q.points for q in block.questions.all()))
    return float(block.points) if block.graded else 0.0


def block_setting(block, key, default):
    value = block.data.get(key, default) if isinstance(block.data, dict) else default
    return default if value in (None, '') else value


def problem_ratio(profile, problem_id):
    """The best share (0..1) of test points among the user's judged submissions of a problem."""
    if not problem_id:
        return 0.0
    best = Submission.objects.filter(user=profile, problem_id=problem_id, status='D', case_total__gt=0) \
        .annotate(ratio=F('case_points') / F('case_total')).aggregate(m=Max('ratio'))['m']
    return float(best or 0)


@dataclass
class BlockState:
    done: bool = False
    score: float = 0.0
    maximum: float = 0.0
    attempts: int = 0
    work: CourseWork = None


@dataclass
class Progress:
    """Everything known about one learner in one course, loaded with a handful of queries."""
    enrollment: CourseEnrollment
    lessons: list
    blocks: dict
    states: dict = field(default_factory=dict)
    progress: dict = field(default_factory=dict)
    complete: dict = field(default_factory=dict)
    available: dict = field(default_factory=dict)
    percent: int = 0
    score_percent: int = None
    finished: bool = False
    counted: list = field(default_factory=list)


def lesson_is_open(lesson, now=None):
    return not lesson.is_draft and (lesson.open_at is None or lesson.open_at <= (now or timezone.now()))


def lesson_is_closed(lesson, now=None):
    """After the deadline tests and assignments stop accepting new work."""
    return lesson.deadline is not None and lesson.deadline < (now or timezone.now())


def build_progress(enrollment, lessons=None, blocks=None):
    course = enrollment.course
    if lessons is None:
        lessons = ordered_lessons(course)
    if blocks is None:
        blocks = blocks_by_lesson(course)
    data = Progress(enrollment=enrollment, lessons=lessons, blocks=blocks)
    marks = {p.lesson_id: p for p in CourseProgress.objects.filter(enrollment=enrollment)}
    data.progress = marks
    best = {}
    counts = defaultdict(int)
    for attempt in CourseAttempt.objects.filter(enrollment=enrollment):
        counts[attempt.block_id] += 1
        if attempt.block_id not in best or attempt.score > best[attempt.block_id].score:
            best[attempt.block_id] = attempt
    works = {}
    for work in CourseWork.objects.filter(enrollment=enrollment).order_by('submitted', 'id'):
        works[work.block_id] = work
    ratios = {}
    for lesson in lessons:
        for block in blocks.get(lesson.id, ()):
            if not block.graded:
                continue
            state = BlockState(maximum=block_max(block))
            if block.type == CourseBlock.TEST:
                attempt = best.get(block.id)
                state.attempts = counts[block.id]
                if attempt:
                    state.score = attempt.score
                    state.done = attempt.percent >= int(block_setting(block, 'pass_percent', 0))
            elif block.type == CourseBlock.ASSIGNMENT:
                work = works.get(block.id)
                state.work = work
                if work and work.status == CourseWork.GRADED:
                    state.score = min(work.grade or 0, state.maximum)
                    need = int(block_setting(block, 'pass_percent', 0))
                    state.done = state.maximum == 0 or 100 * state.score >= need * state.maximum
            else:
                if block.problem_id not in ratios:
                    ratios[block.problem_id] = problem_ratio(enrollment.profile, block.problem_id)
                ratio = ratios[block.problem_id]
                state.score = round(ratio * state.maximum, 2)
                need = int(block_setting(block, 'pass_percent', 100))
                state.done = block.problem_id is not None and ratio * 100 >= need
            data.states[block.id] = state
    for lesson in lessons:
        mark = marks.get(lesson.id)
        done = mark is not None
        if done and lesson.mark_required and not mark.marked_at:
            done = False
        if done:
            for block in blocks.get(lesson.id, ()):
                if block.graded and block.is_required and not data.states[block.id].done:
                    done = False
                    break
        data.complete[lesson.id] = done
    counted = [lesson for lesson in lessons if lesson.is_required] or list(lessons)
    data.counted = counted
    if counted:
        data.percent = round(100 * sum(1 for lesson in counted if data.complete[lesson.id]) / len(counted))
    earned = total = 0.0
    for lesson in counted:
        for block in blocks.get(lesson.id, ()):
            if block.graded and block.is_required:
                earned += data.states[block.id].score
                total += data.states[block.id].maximum
    data.score_percent = round(100 * earned / total) if total else None
    data.finished = bool(counted) and all(data.complete[lesson.id] for lesson in counted) and \
        (data.score_percent is None or data.score_percent >= course.pass_percent)
    # Availability: the date opens a lesson, and in a sequential course the earlier required lessons come first.
    now = timezone.now()
    blocked = False
    for lesson in lessons:
        data.available[lesson.id] = lesson_is_open(lesson, now) and not (course.sequential and blocked)
        if lesson.is_required and not data.complete[lesson.id]:
            blocked = True
    return data


def autograde(work, block=None):
    """Automatic mode: an assignment counts as soon as it is handed in (full points, no teacher in the loop)."""
    block = block or work.block
    work.status, work.grade, work.graded_at = work.GRADED, block_max(block), timezone.now()
    work.save(update_fields=['status', 'grade', 'graded_at'])


def autograde_pending(course):
    """Counts the works that were waiting for a teacher when a course went automatic; returns how many."""
    works = list(CourseWork.objects.filter(block__lesson__course=course, status=CourseWork.PENDING)
                 .select_related('block', 'enrollment'))
    for work in works:
        autograde(work)
    for enrollment in {w.enrollment_id: w.enrollment for w in works}.values():
        refresh(enrollment)
    return len(works)


def full_name(user):
    """The name printed on certificates: surname, name, patronymic ('' when not filled in)."""
    return ' '.join(part for part in (user.last_name.strip(), user.first_name.strip()) if part)


def split_name(user):
    """(surname, name, patronymic) for the form; the patronymic is kept after the name in first_name."""
    name, _sep, patronymic = user.first_name.strip().partition(' ')
    return user.last_name.strip(), name, patronymic.strip()


def save_name(user, surname, name, patronymic):
    user.last_name = surname
    user.first_name = ' '.join(part for part in (name, patronymic) if part)
    user.save(update_fields=['first_name', 'last_name'])


def new_certificate_code():
    while True:
        code = ''.join(secrets.choice(CERT_ALPHABET) for _unused in range(10))
        if not CourseEnrollment.objects.filter(certificate_code=code).exists():
            return code


def refresh(enrollment, progress=None):
    """Stores finished lessons and the course result (and the certificate number) after any change."""
    progress = progress or build_progress(enrollment)
    now = timezone.now()
    for lesson in progress.lessons:
        mark = progress.progress.get(lesson.id)
        if mark is None:
            continue
        done_now = progress.complete[lesson.id]
        if done_now and mark.completed_at is None:
            CourseProgress.objects.filter(id=mark.id).update(completed_at=now)
        elif not done_now and mark.completed_at is not None:
            CourseProgress.objects.filter(id=mark.id).update(completed_at=None)
    if progress.finished and enrollment.completed_at is None:
        enrollment.completed_at = now
        if enrollment.course.certificate and not enrollment.certificate_code:
            enrollment.certificate_code = new_certificate_code()
        enrollment.save(update_fields=['completed_at', 'certificate_code'])
    return progress


def touch_lesson(enrollment, lesson, mark=False):
    obj, _created = CourseProgress.objects.get_or_create(enrollment=enrollment, lesson=lesson)
    if mark and obj.marked_at is None:
        obj.marked_at = timezone.now()
        obj.save(update_fields=['marked_at'])
    return obj


# ---------------------------------------------------------------- tests

def normalize(text):
    return re.sub(r'\s+', ' ', (text or '').strip().lower())


def to_number(text):
    try:
        return float(str(text).strip().replace(',', '.').replace(' ', ''))
    except ValueError:
        return None


def check_answer(question, answer, options):
    """True when the answer is right. `options` are the question's options (already loaded)."""
    if question.type == CourseQuestion.SINGLE:
        right = [o.id for o in options if o.is_correct]
        return answer in right[:1] if not isinstance(answer, list) else answer == right[:1]
    if question.type == CourseQuestion.MULTI:
        right = sorted(o.id for o in options if o.is_correct)
        return isinstance(answer, list) and sorted(answer) == right
    if question.type == CourseQuestion.NUMBER:
        given = to_number(answer)
        if given is None:
            return False
        for option in options:
            wanted = to_number(option.text)
            if wanted is not None and abs(wanted - given) <= 1e-9 * max(1.0, abs(wanted)):
                return True
        return False
    given = normalize(answer)
    return bool(given) and any(normalize(o.text) == given for o in options)


def read_answers(questions, post):
    """The learner's answers from a form post: {question id: option id | [option ids] | text}."""
    answers = {}
    for question in questions:
        key = 'q%d' % question.id
        if question.type == CourseQuestion.MULTI:
            answers[str(question.id)] = [int(x) for x in post.getlist(key) if x.isdigit()]
        elif question.type == CourseQuestion.SINGLE:
            value = post.get(key, '')
            answers[str(question.id)] = int(value) if value.isdigit() else None
        else:
            answers[str(question.id)] = post.get(key, '').strip()[:300]
    return answers


def grade_test(block, answers):
    """(score, total, per-question results) for a test block."""
    score = total = 0.0
    results = {}
    for question in block.questions.all().prefetch_related('options'):
        total += question.points
        ok = check_answer(question, answers.get(str(question.id)), list(question.options.all()))
        if ok:
            score += question.points
        results[question.id] = ok
    return score, total, results


def test_questions(block, shuffle=False):
    questions = list(block.questions.all().prefetch_related('options'))
    if shuffle:
        import random
        random.shuffle(questions)
    return questions
