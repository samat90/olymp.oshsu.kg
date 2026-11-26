from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from judge.models import TypingResult
from judge.views.typing import clear_records_cache


class WorkspaceFileAdmin(admin.ModelAdmin):
    """Compiler projects and files of every user, read-only: for checking a student's work."""

    list_display = ('name', 'kind', 'owner_link', 'project', 'language', 'modified')
    list_filter = ('is_folder', 'language')
    search_fields = ('name', 'owner__user__username', 'content')
    list_select_related = ('owner__user', 'parent')
    date_hierarchy = 'modified'
    fields = ('owner', 'path', 'is_folder', 'language', 'modified', 'code', 'stdin', 'share_key')
    readonly_fields = fields

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    @admin.display(description=_('type'), ordering='is_folder')
    def kind(self, obj):
        return _('folder') if obj.is_folder else _('file')

    @admin.display(description=_('user'), ordering='owner__user__username')
    def owner_link(self, obj):
        return format_html('<a href="{}">{}</a>', reverse('user_page', args=[obj.owner.user.username]),
                           obj.owner.user.username)

    @admin.display(description=_('project'))
    def project(self, obj):
        node = obj
        while node.parent_id is not None:
            node = node.parent
        return node.name if node.is_folder and node.pk != obj.pk else '—'

    @admin.display(description=_('path'))
    def path(self, obj):
        parts = [obj.name]
        node = obj
        while node.parent_id is not None:
            node = node.parent
            parts.append(node.name)
        return '/'.join(reversed(parts))

    @admin.display(description=_('code'))
    def code(self, obj):
        return format_html('<pre style="max-height:60vh;overflow:auto;white-space:pre;font-size:13px">{}</pre>',
                           obj.content)


class TypingResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'mode', 'layout', 'lesson', 'cpm', 'accuracy', 'seconds', 'checked', 'created')
    list_filter = ('checked', 'mode', 'layout')
    search_fields = ('user__user__username',)
    list_select_related = ('user__user',)
    date_hierarchy = 'created'
    actions = ('exclude_from_records', 'return_to_records')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    # A dishonest result is not deleted: without `checked` it leaves the records and levels and can come back.
    @admin.action(description=_('Remove from records (the result is kept)'), permissions=['delete'])
    def exclude_from_records(self, request, queryset):
        self._set_checked(request, queryset, False)

    @admin.action(description=_('Return to records'), permissions=['delete'])
    def return_to_records(self, request, queryset):
        self._set_checked(request, queryset, True)

    def _set_checked(self, request, queryset, checked):
        results = list(queryset.exclude(checked=checked).select_related('user__user'))
        TypingResult.objects.filter(pk__in=[r.pk for r in results]).update(checked=checked)
        for result in results:
            self.log_change(request, result, '%s: %s, %s %s, %s cpm, %s%%, checked=%s' % (
                'returned to records' if checked else 'removed from records', result.user.user.username,
                result.mode, result.layout, result.cpm, result.accuracy, checked))
        clear_records_cache()
        self.message_user(request, _('Results changed: %d') % len(results))
