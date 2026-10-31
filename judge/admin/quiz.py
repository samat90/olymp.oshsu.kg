from django.contrib import admin, messages
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html, format_html_join
from django.utils.translation import gettext_lazy as _

from judge.models import Quiz
from judge.utils import quiz_images  # noqa: F401  (deletes picture files together with quizzes)

DISABLE_NOTE = ('Чтобы временно запретить новые игры (например, на время олимпиады), добавьте в «Misc configs» '
                'ключ quiz_disabled со значением — текстом, который увидят пользователи. Удалите ключ, '
                'чтобы снова разрешить игры.')


class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'author_link', 'access', 'is_hidden', 'is_deleted', 'question_count', 'plays', 'updated')
    list_filter = ('access', 'is_hidden', 'is_deleted', 'theme')
    search_fields = ('title', 'description', 'subject', 'key', 'author__user__username')
    list_select_related = ('author__user',)
    date_hierarchy = 'updated'
    fieldsets = (
        (None, {'fields': ('title', 'author', 'key', 'site_links', 'subject', 'description', 'theme', 'access',
                           'is_hidden', 'is_deleted', 'copied_from', 'plays', 'created', 'updated', 'question_list')}),
        ('Остановить игры', {'fields': (), 'description': DISABLE_NOTE}),
    )
    readonly_fields = ('author', 'key', 'site_links', 'copied_from', 'plays', 'created', 'updated', 'question_list')
    actions = ('hide', 'unhide')

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(questions_total=Count('questions'))

    def has_add_permission(self, request):
        return False

    def changelist_view(self, request, extra_context=None):
        if request.method == 'GET' and not request.GET:
            self.message_user(request, DISABLE_NOTE, messages.INFO)
        return super().changelist_view(request, extra_context)

    @admin.display(description=_('author'), ordering='author__user__username')
    def author_link(self, obj):
        return format_html('<a href="{}">{}</a>', reverse('user_page', args=[obj.author.user.username]),
                           obj.author.user.username)

    @admin.display(description='Вопросов', ordering='questions_total')
    def question_count(self, obj):
        return obj.questions_total

    @admin.display(description='На сайте')
    def site_links(self, obj):
        return format_html('<a href="{}">страница</a> · <a href="{}">редактор</a>',
                           reverse('quiz_detail', args=[obj.key]), reverse('quiz_edit', args=[obj.key]))

    @admin.display(description='Вопросы')
    def question_list(self, obj):
        rows = obj.questions.order_by('order', 'id').values_list('order', 'type', 'text')
        names = dict(obj.questions.model.TYPES)
        if not rows:
            return '—'
        return format_html('<ol style="margin:0;padding-left:20px">{}</ol>', format_html_join(
            '', '<li><b>{}</b>: {}</li>', ((names.get(t, t), (text or '')[:160]) for _o, t, text in rows)))

    @admin.action(description='Скрыть выбранные викторины')
    def hide(self, request, queryset):
        count = queryset.update(is_hidden=True)
        self.message_user(request, 'Скрыто: %d' % count, messages.SUCCESS)

    @admin.action(description='Показать выбранные викторины')
    def unhide(self, request, queryset):
        count = queryset.update(is_hidden=False)
        self.message_user(request, 'Показано: %d' % count, messages.SUCCESS)


class QuizReportAdmin(admin.ModelAdmin):
    list_display = ('quiz_link', 'author', 'short_reason', 'is_resolved', 'quiz_hidden', 'created')
    list_filter = ('is_resolved',)
    search_fields = ('quiz__title', 'quiz__key', 'reason', 'author__user__username')
    list_select_related = ('quiz', 'author__user')
    date_hierarchy = 'created'
    fields = ('quiz_link', 'author', 'reason', 'is_resolved', 'created')
    readonly_fields = ('quiz_link', 'author', 'reason', 'created')
    actions = ('resolve', 'hide_quiz')

    def has_add_permission(self, request):
        return False

    @admin.display(description=_('quiz'), ordering='quiz__title')
    def quiz_link(self, obj):
        return format_html('<a href="{}">{}</a> (<a href="{}">в админке</a>)',
                           reverse('quiz_detail', args=[obj.quiz.key]), obj.quiz.title,
                           reverse('admin:judge_quiz_change', args=[obj.quiz_id]))

    @admin.display(description=_('reason'))
    def short_reason(self, obj):
        return obj.reason[:120]

    @admin.display(description='Скрыта', boolean=True)
    def quiz_hidden(self, obj):
        return obj.quiz.is_hidden

    @admin.action(description='Отметить как рассмотренные')
    def resolve(self, request, queryset):
        count = queryset.update(is_resolved=True)
        self.message_user(request, 'Рассмотрено: %d' % count, messages.SUCCESS)

    @admin.action(description='Скрыть викторины и отметить рассмотренными')
    def hide_quiz(self, request, queryset):
        count = Quiz.objects.filter(id__in=queryset.values('quiz_id')).update(is_hidden=True)
        queryset.update(is_resolved=True)
        self.message_user(request, 'Скрыто викторин: %d' % count, messages.SUCCESS)


class GameSessionAdmin(admin.ModelAdmin):
    list_display = ('pin', 'quiz', 'host', 'mode', 'status', 'player_count', 'created', 'finished')
    list_filter = ('mode', 'status')
    search_fields = ('pin', 'quiz__title', 'host__user__username')
    list_select_related = ('quiz', 'host__user')
    date_hierarchy = 'created'
    fields = ('pin', 'quiz', 'host', 'mode', 'status', 'current', 'player_count', 'settings', 'created', 'finished',
              'report_link')
    readonly_fields = fields

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(players_total=Count('players'))

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.display(description='Игроков', ordering='players_total')
    def player_count(self, obj):
        return obj.players_total

    @admin.display(description='Отчёт')
    def report_link(self, obj):
        return format_html('<a href="{}">открыть</a>', reverse('quiz_game_report', args=[obj.id]))
