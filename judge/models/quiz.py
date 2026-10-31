from django.db import models
from django.db.models import CASCADE, SET_NULL
from django.utils.translation import gettext_lazy as _

from judge.models.profile import Profile


class Quiz(models.Model):
    """A live classroom quiz: questions that players answer on their phones."""

    PUBLIC = 'public'
    LINK = 'link'
    ACCESS = ((PUBLIC, 'Открытая'), (LINK, 'По ссылке'))
    THEMES = (('steppe', 'Степь'), ('lake', 'Иссык-Куль'), ('night', 'Ночь'), ('felt', 'Шырдак'))

    author = models.ForeignKey(Profile, verbose_name=_('author'), related_name='quizzes', on_delete=CASCADE)
    title = models.CharField(verbose_name=_('title'), max_length=120)
    description = models.TextField(verbose_name=_('description'), blank=True, max_length=2000)
    cover = models.ImageField(verbose_name=_('cover'), upload_to='quiz/', blank=True)
    theme = models.CharField(verbose_name=_('theme'), max_length=10, choices=THEMES, default='steppe')
    subject = models.CharField(verbose_name=_('subject'), max_length=60, blank=True, db_index=True)
    access = models.CharField(verbose_name=_('access'), max_length=8, choices=ACCESS, default=LINK)
    key = models.CharField(verbose_name=_('link key'), max_length=12, unique=True)
    is_hidden = models.BooleanField(verbose_name=_('hidden by admin'), default=False)
    copied_from = models.ForeignKey('self', verbose_name=_('copied from'), null=True, blank=True, on_delete=SET_NULL,
                                    related_name='copies')
    plays = models.PositiveIntegerField(verbose_name=_('games played'), default=0)
    created = models.DateTimeField(verbose_name=_('created'), auto_now_add=True)
    updated = models.DateTimeField(verbose_name=_('updated'), auto_now=True, db_index=True)

    class Meta:
        verbose_name = _('quiz')
        verbose_name_plural = _('quizzes')
        ordering = ['-updated']

    def __str__(self):
        return self.title

    def can_edit(self, user):
        if not user.is_authenticated:
            return False
        return self.author_id == user.profile.id or user.is_superuser

    def can_view(self, user):
        if self.can_edit(user):
            return True
        return not self.is_hidden


class Question(models.Model):
    SINGLE = 'single'
    TRUEFALSE = 'truefalse'
    MULTI = 'multi'
    WORD = 'word'
    ORDER = 'order'
    CODE = 'code'
    TEXT = 'text'
    SLIDER = 'slider'
    PIN = 'pin'
    POLL = 'poll'
    CLOUD = 'cloud'
    OPEN = 'open'
    TYPES = (
        (SINGLE, 'Один вариант'),
        (TRUEFALSE, 'Верно / Неверно'),
        (MULTI, 'Несколько верных'),
        (WORD, 'Собери слово'),
        (ORDER, 'Расставь по порядку'),
        (CODE, 'Что выведет код'),
        (TEXT, 'Введи ответ'),
        (SLIDER, 'Ползунок'),
        (PIN, 'Точка на картинке'),
        (POLL, 'Опрос'),
        (CLOUD, 'Облако слов'),
        (OPEN, 'Открытый ответ'),
    )
    UNSCORED = (POLL, CLOUD, OPEN)
    WEIGHTS = ((1, 'Обычный'), (2, 'Двойные очки'), (0, 'Без очков'))

    quiz = models.ForeignKey(Quiz, verbose_name=_('quiz'), related_name='questions', on_delete=CASCADE)
    order = models.PositiveSmallIntegerField(verbose_name=_('order'), default=0)
    type = models.CharField(verbose_name=_('type'), max_length=10, choices=TYPES, default=SINGLE)
    text = models.TextField(verbose_name=_('text'), max_length=2000, blank=True)
    code = models.TextField(verbose_name=_('code'), max_length=4000, blank=True)
    code_language = models.CharField(verbose_name=_('code language'), max_length=20, blank=True)
    image = models.ImageField(verbose_name=_('image'), upload_to='quiz/', blank=True)
    time_limit = models.PositiveSmallIntegerField(verbose_name=_('time, s'), default=20)
    weight = models.PositiveSmallIntegerField(verbose_name=_('points'), choices=WEIGHTS, default=1)
    explanation = models.TextField(verbose_name=_('explanation'), max_length=2000, blank=True)
    data = models.JSONField(verbose_name=_('parameters'), default=dict, blank=True)

    class Meta:
        verbose_name = _('quiz question')
        verbose_name_plural = _('quiz questions')
        ordering = ['quiz', 'order', 'id']

    def __str__(self):
        return '%s #%d' % (self.quiz, self.order + 1)

    @property
    def scored(self):
        return self.type not in self.UNSCORED and self.weight > 0


class Option(models.Model):
    question = models.ForeignKey(Question, verbose_name=_('question'), related_name='options', on_delete=CASCADE)
    order = models.PositiveSmallIntegerField(verbose_name=_('order'), default=0)
    text = models.CharField(verbose_name=_('text'), max_length=300, blank=True)
    image = models.ImageField(verbose_name=_('image'), upload_to='quiz/', blank=True)
    is_correct = models.BooleanField(verbose_name=_('correct'), default=False)

    class Meta:
        verbose_name = _('quiz option')
        verbose_name_plural = _('quiz options')
        ordering = ['question', 'order', 'id']

    def __str__(self):
        return self.text


class GameSession(models.Model):
    HOST_SCREEN = 'screen'
    HOST_REMOTE = 'remote'
    AUTO = 'auto'
    SOLO = 'solo'
    MODES = (
        (HOST_SCREEN, 'С ведущим и экраном'),
        (HOST_REMOTE, 'С ведущим без экрана'),
        (AUTO, 'Автоматически'),
        (SOLO, 'В одиночку'),
    )
    LOBBY = 'lobby'
    QUESTION = 'question'
    REVEAL = 'reveal'
    LEADERBOARD = 'leaderboard'
    FINISHED = 'finished'
    STATUSES = ((LOBBY, 'Лобби'), (QUESTION, 'Вопрос'), (REVEAL, 'Разбор'), (LEADERBOARD, 'Таблица'),
                (FINISHED, 'Завершена'))
    MAX_PLAYERS = 1000

    quiz = models.ForeignKey(Quiz, verbose_name=_('quiz'), related_name='games', on_delete=CASCADE)
    host = models.ForeignKey(Profile, verbose_name=_('host'), null=True, blank=True, related_name='hosted_games',
                             on_delete=SET_NULL)
    pin = models.CharField(verbose_name=_('PIN'), max_length=6, db_index=True)
    mode = models.CharField(verbose_name=_('mode'), max_length=6, choices=MODES, default=HOST_SCREEN)
    status = models.CharField(verbose_name=_('status'), max_length=12, choices=STATUSES, default=LOBBY)
    current = models.SmallIntegerField(verbose_name=_('current question'), default=-1)
    phase_started = models.DateTimeField(verbose_name=_('phase started'), null=True, blank=True)
    settings = models.JSONField(verbose_name=_('settings'), default=dict, blank=True)
    question_ids = models.JSONField(verbose_name=_('question order'), default=list, blank=True)
    created = models.DateTimeField(verbose_name=_('created'), auto_now_add=True, db_index=True)
    finished = models.DateTimeField(verbose_name=_('finished'), null=True, blank=True)

    class Meta:
        verbose_name = _('quiz game')
        verbose_name_plural = _('quiz games')
        ordering = ['-created']

    def __str__(self):
        return '%s (%s)' % (self.quiz, self.pin)

    @property
    def is_active(self):
        return self.status != self.FINISHED


class Player(models.Model):
    game = models.ForeignKey(GameSession, verbose_name=_('game'), related_name='players', on_delete=CASCADE)
    profile = models.ForeignKey(Profile, verbose_name=_('user'), null=True, blank=True, related_name='quiz_players',
                                on_delete=SET_NULL)
    nickname = models.CharField(verbose_name=_('nickname'), max_length=24)
    token = models.CharField(verbose_name=_('guest token'), max_length=32, blank=True)
    score = models.IntegerField(verbose_name=_('score'), default=0)
    streak = models.PositiveSmallIntegerField(verbose_name=_('streak'), default=0)
    correct = models.PositiveSmallIntegerField(verbose_name=_('correct answers'), default=0)
    rank = models.PositiveIntegerField(verbose_name=_('place'), null=True, blank=True)
    is_removed = models.BooleanField(verbose_name=_('removed'), default=False)
    joined = models.DateTimeField(verbose_name=_('joined'), auto_now_add=True)

    class Meta:
        verbose_name = _('quiz player')
        verbose_name_plural = _('quiz players')
        ordering = ['game', '-score']
        indexes = [models.Index(fields=['game', '-score'])]

    def __str__(self):
        return self.nickname


class Answer(models.Model):
    player = models.ForeignKey(Player, verbose_name=_('player'), related_name='answers', on_delete=CASCADE)
    question = models.ForeignKey(Question, verbose_name=_('question'), related_name='answers', on_delete=CASCADE)
    value = models.JSONField(verbose_name=_('answer'), null=True, blank=True)
    is_correct = models.BooleanField(verbose_name=_('correct'), default=False)
    fraction = models.FloatField(verbose_name=_('share correct'), default=0)
    points = models.IntegerField(verbose_name=_('points'), default=0)
    time_ms = models.PositiveIntegerField(verbose_name=_('time, ms'), default=0)
    created = models.DateTimeField(verbose_name=_('date'), auto_now_add=True)

    class Meta:
        verbose_name = _('quiz answer')
        verbose_name_plural = _('quiz answers')
        unique_together = ('player', 'question')


class QuizReport(models.Model):
    quiz = models.ForeignKey(Quiz, verbose_name=_('quiz'), related_name='reports', on_delete=CASCADE)
    author = models.ForeignKey(Profile, verbose_name=_('author'), null=True, blank=True, on_delete=SET_NULL)
    reason = models.TextField(verbose_name=_('reason'), max_length=1000)
    is_resolved = models.BooleanField(verbose_name=_('resolved'), default=False)
    created = models.DateTimeField(verbose_name=_('date'), auto_now_add=True)

    class Meta:
        verbose_name = _('quiz report')
        verbose_name_plural = _('quiz reports')
        ordering = ['is_resolved', '-created']
