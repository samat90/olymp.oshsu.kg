from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as OldUserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.forms import BooleanField, ModelForm
from django.urls import reverse_lazy
from django.utils.html import format_html
from django.utils.translation import gettext, gettext_lazy as _, ngettext
from reversion.admin import VersionAdmin

from judge.models import Profile, WebAuthnCredential
from judge.utils.views import NoBatchDeleteMixin
from judge.widgets import AdminAceWidget, AdminMartorWidget, AdminSelect2Widget


TEACHER_LABEL = 'Преподаватель'
TEACHER_HELP = 'Может создавать курсы и проверять работы слушателей. Отметьте и сохраните.'


class ProfileForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        if 'current_contest' in self.base_fields:
            # form.fields['current_contest'] does not exist when the user has only view permission on the model.
            self.fields['current_contest'].queryset = self.instance.contest_history.select_related('contest') \
                .only('contest__name', 'user_id', 'virtual')
            self.fields['current_contest'].label_from_instance = \
                lambda obj: '%s v%d' % (obj.contest.name, obj.virtual) if obj.virtual else obj.contest.name

    class Meta:
        labels = {'is_teacher': TEACHER_LABEL}
        help_texts = {'is_teacher': TEACHER_HELP}
        widgets = {
            'timezone': AdminSelect2Widget,
            'language': AdminSelect2Widget,
            'ace_theme': AdminSelect2Widget,
            'current_contest': AdminSelect2Widget,
            'about': AdminMartorWidget(attrs={'data-markdownfy-url': reverse_lazy('profile_preview')}),
        }


class TimezoneFilter(admin.SimpleListFilter):
    title = _('timezone')
    parameter_name = 'timezone'

    def lookups(self, request, model_admin):
        return Profile.objects.values_list('timezone', 'timezone').distinct().order_by('timezone')

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        return queryset.filter(timezone=self.value())


class WebAuthnInline(admin.TabularInline):
    model = WebAuthnCredential
    readonly_fields = ('cred_id', 'public_key', 'counter')
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False


class ProfileAdmin(NoBatchDeleteMixin, VersionAdmin):
    fields = ('user', 'is_teacher', 'display_rank', 'about', 'organizations', 'timezone', 'language', 'ace_theme',
              'math_engine', 'last_access', 'ip', 'mute', 'is_unlisted', 'is_banned_from_problem_voting',
              'username_display_override', 'notes', 'is_totp_enabled', 'user_script', 'current_contest')
    readonly_fields = ('user',)
    list_display = ('admin_user_admin', 'email', 'teacher_flag', 'is_totp_enabled', 'timezone_full',
                    'date_joined', 'last_access', 'ip', 'show_public')
    ordering = ('user__username',)
    search_fields = ('user__username', 'ip', 'user__email')
    list_filter = ('is_teacher', 'language', TimezoneFilter)
    actions_on_top = True
    actions_on_bottom = True
    form = ProfileForm
    inlines = [WebAuthnInline]

    def has_add_permission(self, request, obj=None):
        return False

    # We can't use has_delete_permission here because we still want user profiles to be
    # deleteable through related objects (i.e. User). Thus, we simply hide the delete button.
    # If an admin wants to go directly to the delete endpoint to delete a profile, more
    # power to them.
    def render_change_form(self, request, context, **kwargs):
        context['show_delete'] = request.user.is_superuser
        return super().render_change_form(request, context, **kwargs)

    def get_queryset(self, request):
        return super(ProfileAdmin, self).get_queryset(request).select_related('user')

    def get_fields(self, request, obj=None):
        if request.user.has_perm('judge.totp'):
            fields = list(self.fields)
            fields.insert(fields.index('is_totp_enabled') + 1, 'totp_key')
            fields.insert(fields.index('totp_key') + 1, 'scratch_codes')
            return tuple(fields)
        else:
            return self.fields

    def get_readonly_fields(self, request, obj=None):
        fields = self.readonly_fields
        if not request.user.has_perm('judge.totp'):
            fields += ('is_totp_enabled',)
        return fields

    def get_actions(self, request):
        actions = super(ProfileAdmin, self).get_actions(request)

        for action in ('recalculate_points', 'mute_users', 'make_teachers', 'remove_teachers'):
            func, name, desc = self.get_action(action)
            actions[name] = (func, name, desc)

        if request.user.has_perm('judge.deactivate_users') or \
                request.user.has_perm('auth.change_user'):
            func, name, desc = self.get_action('deactivate_users')
            actions[name] = (func, name, desc)

        return actions

    @admin.display(description=TEACHER_LABEL, ordering='is_teacher', boolean=True)
    def teacher_flag(self, obj):
        return obj.is_teacher

    @admin.display(description='')
    def show_public(self, obj):
        return format_html('<a href="{0}" style="white-space:nowrap;">{1}</a>',
                           obj.get_absolute_url(), gettext('View on site'))

    @admin.display(description=_('user'), ordering='user__username')
    def admin_user_admin(self, obj):
        return obj.username

    @admin.display(description=_('email'), ordering='user__email')
    def email(self, obj):
        return obj.user.email

    @admin.display(description=_('timezone'), ordering='timezone')
    def timezone_full(self, obj):
        return obj.timezone

    @admin.display(description=_('date joined'), ordering='user__date_joined')
    def date_joined(self, obj):
        return obj.user.date_joined

    @admin.display(description=_('Recalculate scores'))
    def recalculate_points(self, request, queryset):
        count = 0
        for profile in queryset:
            profile.calculate_points()
            count += 1
        self.message_user(request, ngettext('%d user had scores recalculated.',
                                            '%d users had scores recalculated.',
                                            count) % count)

    @admin.display(description=_('Deactivate users'))
    def deactivate_users(self, request, queryset):
        if not request.user.has_perm('judge.deactivate_users') and not request.user.has_perm('auth.change_user'):
            self.message_user(request, gettext('You do not have permission to deactivate users.'), level=messages.ERROR)
            return

        count = 0
        for profile in queryset.select_related('user'):
            profile.user.is_active = False
            profile.user.save()
            count += 1
        self.message_user(request, ngettext('%d user was banned.',
                                            '%d users were banned.',
                                            count) % count)

    @admin.display(description='Сделать преподавателями')
    def make_teachers(self, request, queryset):
        self.message_user(request, 'Преподавателей назначено: %d' % queryset.update(is_teacher=True))

    @admin.display(description='Снять статус преподавателя')
    def remove_teachers(self, request, queryset):
        self.message_user(request, 'Статус снят у: %d' % queryset.update(is_teacher=False))

    @admin.display(description=_('Mute users'))
    def mute_users(self, request, queryset):
        count = queryset.update(mute=True)
        self.message_user(request, ngettext('%d user was muted.',
                                            '%d users were muted.',
                                            count) % count)

    def get_form(self, request, obj=None, **kwargs):
        form = super(ProfileAdmin, self).get_form(request, obj, **kwargs)
        if 'user_script' in form.base_fields:
            # form.base_fields['user_script'] does not exist when the user has only view permission on the model.
            form.base_fields['user_script'].widget = AdminAceWidget(
                mode='javascript', theme=request.profile.resolved_ace_theme,
            )
        return form


class UserForm(UserChangeForm):
    """The user page also sets the teacher status, so nobody has to look for it in the profile."""
    is_teacher = BooleanField(label=TEACHER_LABEL, required=False, help_text=TEACHER_HELP)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        profile = None
        if self.instance.pk:
            profile = Profile.objects.filter(user_id=self.instance.pk).only('is_teacher').first()
        self.fields['is_teacher'].initial = bool(profile and profile.is_teacher)


class UserAdmin(OldUserAdmin):
    form = UserForm
    fieldsets = (('Роль на сайте', {'fields': ('is_teacher',)}),) + tuple(OldUserAdmin.fieldsets)
    list_display = OldUserAdmin.list_display + ('teacher_flag',)
    list_filter = ('profile__is_teacher',) + tuple(OldUserAdmin.list_filter)
    list_select_related = ('profile',)
    actions = ['make_teachers', 'remove_teachers']

    @admin.display(description=TEACHER_LABEL, ordering='profile__is_teacher', boolean=True)
    def teacher_flag(self, obj):
        profile = getattr(obj, 'profile', None)
        return bool(profile and profile.is_teacher)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:
            Profile.objects.create(user=obj)
        elif 'is_teacher' in form.cleaned_data:
            Profile.objects.filter(user=obj).update(is_teacher=form.cleaned_data['is_teacher'])

    @admin.display(description='Сделать преподавателями')
    def make_teachers(self, request, queryset):
        self.message_user(request, 'Преподавателей назначено: %d' % Profile.objects.filter(user__in=queryset)
                          .update(is_teacher=True))

    @admin.display(description='Снять статус преподавателя')
    def remove_teachers(self, request, queryset):
        self.message_user(request, 'Статус снят у: %d' % Profile.objects.filter(user__in=queryset)
                          .update(is_teacher=False))
