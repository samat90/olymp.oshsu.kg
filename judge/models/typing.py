from django.db import models
from django.db.models import CASCADE
from django.utils.translation import gettext_lazy as _

from judge.models.profile import Profile


class TypingResult(models.Model):
    """One finished exercise of the typing trainer."""

    LESSON = 'lesson'
    TEST = 'test'
    CODE = 'code'
    MODES = (
        (LESSON, _('lesson')),
        (TEST, _('speed test')),
        (CODE, _('code')),
    )
    LAYOUTS = (('ru', 'Русская'), ('en', 'English'), ('ky', 'Кыргызча'))

    user = models.ForeignKey(Profile, verbose_name=_('user'), related_name='typing_results', on_delete=CASCADE)
    mode = models.CharField(verbose_name=_('mode'), max_length=8, choices=MODES)
    layout = models.CharField(verbose_name=_('layout'), max_length=2, choices=LAYOUTS)
    lesson = models.PositiveSmallIntegerField(verbose_name=_('lesson'), null=True, blank=True)
    seconds = models.FloatField(verbose_name=_('time, s'))
    chars = models.PositiveIntegerField(verbose_name=_('characters'))
    errors = models.PositiveIntegerField(verbose_name=_('errors'))
    cpm = models.PositiveIntegerField(verbose_name=_('characters per minute'), db_index=True)
    accuracy = models.FloatField(verbose_name=_('accuracy, %'))
    created = models.DateTimeField(verbose_name=_('date'), auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = _('typing result')
        verbose_name_plural = _('typing results')
        ordering = ['-created']
        indexes = [models.Index(fields=['mode', 'layout', '-cpm'])]

    @property
    def wpm(self):
        return round(self.cpm / 5)
