"""Courses: a teacher builds lessons out of free-form blocks, learners enrol, work through them and get graded."""
import os
import re
import secrets
import uuid

from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models import CASCADE, SET_NULL
from django.utils.translation import gettext_lazy as _

from judge.models.profile import Profile

YOUTUBE_ID = re.compile(r'^[A-Za-z0-9_-]{11}$')
YOUTUBE_URL = re.compile(r'(?:youtu\.be/|youtube(?:-nocookie)?\.com/(?:watch\?(?:[^#\s]*&)?v=|embed/|shorts/|live/|v/))'
                         r'([A-Za-z0-9_-]{11})')


def youtube_id(value):
    """The 11-character video id from any YouTube link (or the id itself); '' when there is none."""
    value = (value or '').strip()
    if YOUTUBE_ID.match(value):
        return value
    found = YOUTUBE_URL.search(value)
    return found.group(1) if found else ''


def _upload(folder, filename):
    return 'courses/%s/%s%s' % (folder, uuid.uuid4().hex, os.path.splitext(filename)[1].lower()[:10])


def cover_path(instance, filename):
    return _upload('covers', filename)


def image_path(instance, filename):
    return _upload('images', filename)


def file_path(instance, filename):
    return _upload('files', filename)


def work_path(instance, filename):
    return _upload('work', filename)


def new_key():
    alphabet = 'abcdefghjkmnpqrstuvwxyz23456789'
    while True:
        key = ''.join(secrets.choice(alphabet) for _unused in range(8))
        if not Course.objects.filter(key=key).exists():
            return key


class Course(models.Model):
    PUBLIC = 'public'
    LINK = 'link'
    ORG = 'org'
    ACCESS = ((PUBLIC, _('Открытый')), (LINK, _('По ссылке')), (ORG, _('Для организации')))
    DRAFT = 'draft'
    PUBLISHED = 'published'
    STATUS = ((DRAFT, _('Черновик')), (PUBLISHED, _('Опубликован')))
    LANGUAGES = (('ru', 'Русский'), ('ky', 'Кыргызча'), ('en', 'English'))

    author = models.ForeignKey(Profile, verbose_name=_('author'), related_name='courses', on_delete=CASCADE)
    coauthors = models.ManyToManyField(Profile, verbose_name=_('coauthors'), related_name='coauthored_courses',
                                       blank=True)
    title = models.CharField(verbose_name=_('title'), max_length=120)
    description = models.TextField(verbose_name=_('description'), blank=True, max_length=10000)
    cover = models.ImageField(verbose_name=_('cover'), upload_to=cover_path, blank=True)
    subject = models.CharField(verbose_name=_('subject'), max_length=60, blank=True, db_index=True)
    language = models.CharField(verbose_name=_('language'), max_length=2, choices=LANGUAGES, default='ru')
    key = models.CharField(verbose_name=_('link key'), max_length=12, unique=True)
    access = models.CharField(verbose_name=_('access'), max_length=6, choices=ACCESS, default=PUBLIC)
    organization = models.ForeignKey('Organization', verbose_name=_('organization'), null=True, blank=True,
                                     on_delete=SET_NULL, related_name='courses')
    status = models.CharField(verbose_name=_('status'), max_length=9, choices=STATUS, default=DRAFT, db_index=True)
    is_hidden = models.BooleanField(verbose_name=_('hidden by admin'), default=False)
    is_deleted = models.BooleanField(verbose_name=_('deleted by the author'), default=False)
    sequential = models.BooleanField(verbose_name=_('lessons open one after another'), default=False)
    pass_percent = models.PositiveSmallIntegerField(verbose_name=_('pass mark, %'), default=0,
                                                    validators=[MaxValueValidator(100)])
    certificate = models.BooleanField(verbose_name=_('certificate'), default=True)
    reviews_on = models.BooleanField(verbose_name=_('reviews'), default=True)
    enrollments_count = models.PositiveIntegerField(verbose_name=_('learners'), default=0)
    created = models.DateTimeField(verbose_name=_('created'), auto_now_add=True)
    updated = models.DateTimeField(verbose_name=_('updated'), auto_now=True, db_index=True)

    class Meta:
        verbose_name = _('course')
        verbose_name_plural = _('courses')
        ordering = ['-updated']

    def __str__(self):
        return self.title

    @staticmethod
    def is_admin(user):
        """Site admins manage every course: superusers and staff allowed to change courses."""
        return user.is_authenticated and (user.is_superuser or (user.is_staff and user.has_perm('judge.change_course')))

    def is_owner(self, user):
        return user.is_authenticated and self.author_id == user.profile.id

    def is_team(self, user):
        """Author or coauthor."""
        if not user.is_authenticated:
            return False
        pid = user.profile.id
        return self.author_id == pid or self.coauthors.filter(id=pid).exists()

    def can_edit(self, user):
        if not user.is_authenticated or self.is_deleted:
            return False
        return self.is_admin(user) or self.is_team(user)

    def can_delete(self, user):
        return user.is_authenticated and not self.is_deleted and (self.is_admin(user) or self.is_owner(user))

    def can_view(self, user):
        if self.is_deleted:
            return False
        if self.can_edit(user):
            return True
        if self.is_hidden or self.status != self.PUBLISHED:
            return False
        if self.access == self.ORG:
            return user.is_authenticated and self.organization_id is not None and \
                user.profile.organizations.filter(id=self.organization_id).exists()
        return True

    @property
    def in_catalog(self):
        return self.access == self.PUBLIC and self.status == self.PUBLISHED and not self.is_hidden \
            and not self.is_deleted


class CourseModule(models.Model):
    course = models.ForeignKey(Course, verbose_name=_('course'), related_name='modules', on_delete=CASCADE)
    title = models.CharField(verbose_name=_('title'), max_length=120)
    order = models.PositiveSmallIntegerField(verbose_name=_('order'), default=0)

    class Meta:
        verbose_name = _('module')
        verbose_name_plural = _('modules')
        ordering = ['course', 'order', 'id']

    def __str__(self):
        return self.title


class CourseLesson(models.Model):
    course = models.ForeignKey(Course, verbose_name=_('course'), related_name='lessons', on_delete=CASCADE)
    module = models.ForeignKey(CourseModule, verbose_name=_('module'), null=True, blank=True, related_name='lessons',
                               on_delete=SET_NULL)
    order = models.PositiveSmallIntegerField(verbose_name=_('order'), default=0)
    title = models.CharField(verbose_name=_('title'), max_length=160)
    is_draft = models.BooleanField(verbose_name=_('draft'), default=False)
    is_required = models.BooleanField(verbose_name=_('required'), default=True)
    mark_required = models.BooleanField(verbose_name=_('needs the "Learned" mark'), default=True)
    open_at = models.DateTimeField(verbose_name=_('opens at'), null=True, blank=True)
    deadline = models.DateTimeField(verbose_name=_('deadline'), null=True, blank=True)
    created = models.DateTimeField(verbose_name=_('created'), auto_now_add=True)

    class Meta:
        verbose_name = _('lesson')
        verbose_name_plural = _('lessons')
        ordering = ['course', 'module__order', 'order', 'id']

    def __str__(self):
        return self.title


class CourseBlock(models.Model):
    TEXT = 'text'
    VIDEO = 'video'
    IMAGE = 'image'
    FILE = 'file'
    TEST = 'test'
    ASSIGNMENT = 'assignment'
    PROBLEM = 'problem'
    TYPES = (
        (TEXT, _('Текст')), (VIDEO, _('Видео')), (IMAGE, _('Картинка')), (FILE, _('Файл')),
        (TEST, _('Тест')), (ASSIGNMENT, _('Задание')), (PROBLEM, _('Задача сайта')),
    )
    GRADED = (TEST, ASSIGNMENT, PROBLEM)

    lesson = models.ForeignKey(CourseLesson, verbose_name=_('lesson'), related_name='blocks', on_delete=CASCADE)
    order = models.PositiveSmallIntegerField(verbose_name=_('order'), default=0)
    type = models.CharField(verbose_name=_('type'), max_length=10, choices=TYPES, default=TEXT)
    title = models.CharField(verbose_name=_('title'), max_length=200, blank=True)
    text = models.TextField(verbose_name=_('text'), blank=True, max_length=30000)
    youtube_id = models.CharField(verbose_name=_('YouTube'), max_length=11, blank=True)
    image = models.ImageField(verbose_name=_('image'), upload_to=image_path, blank=True)
    file = models.FileField(verbose_name=_('file'), upload_to=file_path, blank=True)
    problem = models.ForeignKey('Problem', verbose_name=_('problem'), null=True, blank=True, on_delete=SET_NULL,
                                related_name='+')
    points = models.PositiveSmallIntegerField(verbose_name=_('points'), default=10)
    is_required = models.BooleanField(verbose_name=_('required'), default=True)
    data = models.JSONField(verbose_name=_('parameters'), default=dict, blank=True)

    class Meta:
        verbose_name = _('lesson block')
        verbose_name_plural = _('lesson blocks')
        ordering = ['lesson', 'order', 'id']

    def __str__(self):
        return '%s: %s' % (self.get_type_display(), self.title or self.lesson.title)

    @property
    def graded(self):
        return self.type in self.GRADED


class CourseQuestion(models.Model):
    SINGLE = 'single'
    MULTI = 'multi'
    NUMBER = 'number'
    TEXT = 'text'
    TYPES = ((SINGLE, _('Один вариант')), (MULTI, _('Несколько верных')), (NUMBER, _('Число')),
             (TEXT, _('Короткий ответ')))

    block = models.ForeignKey(CourseBlock, verbose_name=_('block'), related_name='questions', on_delete=CASCADE)
    order = models.PositiveSmallIntegerField(verbose_name=_('order'), default=0)
    type = models.CharField(verbose_name=_('type'), max_length=8, choices=TYPES, default=SINGLE)
    text = models.TextField(verbose_name=_('text'), max_length=3000)
    explanation = models.TextField(verbose_name=_('explanation'), blank=True, max_length=2000)
    points = models.PositiveSmallIntegerField(verbose_name=_('points'), default=1)

    class Meta:
        verbose_name = _('test question')
        verbose_name_plural = _('test questions')
        ordering = ['block', 'order', 'id']

    def __str__(self):
        return self.text[:60]


class CourseOption(models.Model):
    """A choice for single/multi questions; for number/text questions every row is an accepted answer."""
    question = models.ForeignKey(CourseQuestion, verbose_name=_('question'), related_name='options', on_delete=CASCADE)
    order = models.PositiveSmallIntegerField(verbose_name=_('order'), default=0)
    text = models.CharField(verbose_name=_('text'), max_length=300)
    is_correct = models.BooleanField(verbose_name=_('correct'), default=False)

    class Meta:
        verbose_name = _('answer option')
        verbose_name_plural = _('answer options')
        ordering = ['question', 'order', 'id']

    def __str__(self):
        return self.text


class CourseEnrollment(models.Model):
    course = models.ForeignKey(Course, verbose_name=_('course'), related_name='enrollments', on_delete=CASCADE)
    profile = models.ForeignKey(Profile, verbose_name=_('user'), related_name='course_enrollments', on_delete=CASCADE)
    joined = models.DateTimeField(verbose_name=_('joined'), auto_now_add=True)
    completed_at = models.DateTimeField(verbose_name=_('completed'), null=True, blank=True)
    certificate_code = models.CharField(verbose_name=_('certificate'), max_length=16, unique=True, null=True,
                                        blank=True)
    last_lesson = models.ForeignKey(CourseLesson, verbose_name=_('last lesson'), null=True, blank=True,
                                    on_delete=SET_NULL, related_name='+')

    class Meta:
        verbose_name = _('course enrollment')
        verbose_name_plural = _('course enrollments')
        ordering = ['-joined']
        constraints = [models.UniqueConstraint(fields=['course', 'profile'], name='course_enrollment_unique')]

    def __str__(self):
        return '%s — %s' % (self.profile, self.course)


class CourseProgress(models.Model):
    enrollment = models.ForeignKey(CourseEnrollment, verbose_name=_('enrollment'), related_name='progress',
                                   on_delete=CASCADE)
    lesson = models.ForeignKey(CourseLesson, verbose_name=_('lesson'), related_name='progress', on_delete=CASCADE)
    opened = models.DateTimeField(verbose_name=_('opened'), auto_now_add=True)
    marked_at = models.DateTimeField(verbose_name=_('marked as learned'), null=True, blank=True)
    completed_at = models.DateTimeField(verbose_name=_('completed'), null=True, blank=True)

    class Meta:
        verbose_name = _('lesson progress')
        verbose_name_plural = _('lesson progress')
        constraints = [models.UniqueConstraint(fields=['enrollment', 'lesson'], name='course_progress_unique')]


class CourseAttempt(models.Model):
    enrollment = models.ForeignKey(CourseEnrollment, verbose_name=_('enrollment'), related_name='attempts',
                                   on_delete=CASCADE)
    block = models.ForeignKey(CourseBlock, verbose_name=_('block'), related_name='attempts', on_delete=CASCADE)
    answers = models.JSONField(verbose_name=_('answers'), default=dict, blank=True)
    score = models.FloatField(verbose_name=_('score'), default=0)
    total = models.FloatField(verbose_name=_('total'), default=0)
    created = models.DateTimeField(verbose_name=_('created'), auto_now_add=True)

    class Meta:
        verbose_name = _('test attempt')
        verbose_name_plural = _('test attempts')
        ordering = ['-created']

    @property
    def percent(self):
        return round(100 * self.score / self.total) if self.total else 0


class CourseWork(models.Model):
    PENDING = 'pending'
    GRADED = 'graded'
    RETURNED = 'returned'
    STATUS = ((PENDING, _('Ждёт проверки')), (GRADED, _('Оценено')), (RETURNED, _('На доработку')))

    enrollment = models.ForeignKey(CourseEnrollment, verbose_name=_('enrollment'), related_name='submissions',
                                   on_delete=CASCADE)
    block = models.ForeignKey(CourseBlock, verbose_name=_('block'), related_name='submissions', on_delete=CASCADE)
    text = models.TextField(verbose_name=_('answer'), blank=True, max_length=20000)
    file = models.FileField(verbose_name=_('file'), upload_to=work_path, blank=True)
    file_name = models.CharField(verbose_name=_('file name'), max_length=120, blank=True)
    submitted = models.DateTimeField(verbose_name=_('submitted'), auto_now_add=True, db_index=True)
    status = models.CharField(verbose_name=_('status'), max_length=8, choices=STATUS, default=PENDING, db_index=True)
    grade = models.FloatField(verbose_name=_('grade'), null=True, blank=True)
    comment = models.TextField(verbose_name=_('comment'), blank=True, max_length=5000)
    graded_by = models.ForeignKey(Profile, verbose_name=_('graded by'), null=True, blank=True, on_delete=SET_NULL,
                                  related_name='+')
    graded_at = models.DateTimeField(verbose_name=_('graded at'), null=True, blank=True)

    class Meta:
        verbose_name = _('assignment submission')
        verbose_name_plural = _('assignment submissions')
        ordering = ['-submitted']


class CourseComment(models.Model):
    lesson = models.ForeignKey(CourseLesson, verbose_name=_('lesson'), related_name='comments', on_delete=CASCADE)
    author = models.ForeignKey(Profile, verbose_name=_('author'), related_name='course_comments', on_delete=CASCADE)
    parent = models.ForeignKey('self', verbose_name=_('reply to'), null=True, blank=True, related_name='replies',
                               on_delete=CASCADE)
    text = models.TextField(verbose_name=_('text'), max_length=3000)
    created = models.DateTimeField(verbose_name=_('created'), auto_now_add=True)

    class Meta:
        verbose_name = _('lesson comment')
        verbose_name_plural = _('lesson comments')
        ordering = ['created', 'id']


class CourseReview(models.Model):
    course = models.ForeignKey(Course, verbose_name=_('course'), related_name='reviews', on_delete=CASCADE)
    profile = models.ForeignKey(Profile, verbose_name=_('user'), related_name='course_reviews', on_delete=CASCADE)
    rating = models.PositiveSmallIntegerField(verbose_name=_('rating'), default=5)
    text = models.TextField(verbose_name=_('review'), blank=True, max_length=2000)
    created = models.DateTimeField(verbose_name=_('created'), auto_now=True)

    class Meta:
        verbose_name = _('course review')
        verbose_name_plural = _('course reviews')
        ordering = ['-created']
        constraints = [models.UniqueConstraint(fields=['course', 'profile'], name='course_review_unique')]
