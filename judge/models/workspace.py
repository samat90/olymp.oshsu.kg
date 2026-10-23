import secrets

from django.db import models
from django.db.models import CASCADE
from django.utils.translation import gettext_lazy as _

from judge.models.profile import Profile

__all__ = ['WorkspaceFile']

MAX_FILES_PER_USER = 500
MAX_FILE_SIZE = 65536
MAX_DEPTH = 8


class WorkspaceFile(models.Model):
    """A file or a folder in a user's personal workspace (the "Песочница" page)."""

    owner = models.ForeignKey(Profile, verbose_name=_('owner'), related_name='workspace_files', on_delete=CASCADE)
    parent = models.ForeignKey('self', verbose_name=_('folder'), null=True, blank=True, related_name='children',
                               on_delete=CASCADE)
    name = models.CharField(verbose_name=_('name'), max_length=100)
    is_folder = models.BooleanField(verbose_name=_('is folder'), default=False)
    language = models.CharField(verbose_name=_('language'), max_length=6, blank=True)
    content = models.TextField(verbose_name=_('content'), blank=True)
    stdin = models.TextField(verbose_name=_('input'), blank=True)
    share_key = models.CharField(verbose_name=_('share key'), max_length=24, null=True, blank=True, unique=True)
    created = models.DateTimeField(verbose_name=_('created'), auto_now_add=True)
    modified = models.DateTimeField(verbose_name=_('modified'), auto_now=True)

    class Meta:
        verbose_name = _('workspace file')
        verbose_name_plural = _('workspace files')
        ordering = ['-is_folder', 'name']
        constraints = [
            models.UniqueConstraint(fields=['owner', 'parent', 'name'], name='workspace_unique_name'),
            models.UniqueConstraint(fields=['owner', 'name'], condition=models.Q(parent__isnull=True),
                                    name='workspace_unique_root_name'),
        ]

    def __str__(self):
        return self.name

    def make_share_key(self):
        if not self.share_key:
            self.share_key = secrets.token_urlsafe(12)
        return self.share_key

    def depth(self):
        depth = 0
        node = self.parent
        while node is not None:
            depth += 1
            node = node.parent
        return depth

    def is_inside(self, folder):
        node = self
        while node is not None:
            if node.pk == folder.pk:
                return True
            node = node.parent
        return False

    def as_dict(self, with_content=False):
        data = {
            'id': self.id,
            'parent': self.parent_id,
            'name': self.name,
            'folder': self.is_folder,
            'language': self.language,
            'modified': self.modified.isoformat() if self.modified else None,
            'shared': bool(self.share_key),
        }
        if with_content:
            data['content'] = self.content
            data['stdin'] = self.stdin
            data['share_key'] = self.share_key
        return data
