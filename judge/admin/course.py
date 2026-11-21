from django.contrib import admin, messages
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from judge.models import Course, CourseBlock, CourseLesson, CourseModule, CourseOption, CourseQuestion
from judge.utils import quiz_images  # noqa: F401  (removes picture files together with their rows)

DISABLE_NOTE = ('Чтобы временно закрыть запись, сдачу работ и правки (например, на время олимпиады), добавьте в '
                '«Misc configs» ключ courses_disabled со значением — текстом для пользователей. '
                'Удалите ключ, чтобы снова разрешить.')


class ModuleInline(admin.TabularInline):
    model = CourseModule
    extra = 0
    fields = ('title', 'order')


class LessonInline(admin.TabularInline):
    model = CourseLesson
    extra = 0
    fields = ('title', 'module', 'order', 'is_draft', 'is_required', 'mark_required', 'open_at', 'deadline')
    show_change_link = True


class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'author_link', 'status', 'access', 'is_hidden', 'is_deleted', 'lesson_count',
                    'enrollments_count', 'updated')
    list_filter = ('status', 'access', 'is_hidden', 'is_deleted', 'language')
    search_fields = ('title', 'description', 'subject', 'key', 'author__user__username')
    list_select_related = ('author__user',)
    date_hierarchy = 'updated'
    raw_id_fields = ('author', 'coauthors', 'organization')
    fieldsets = (
        (None, {'fields': ('title', 'author', 'coauthors', 'key', 'site_links', 'subject', 'language', 'description',
                           'cover')}),
        ('Доступ', {'fields': ('status', 'access', 'organization', 'is_hidden', 'is_deleted')}),
        ('Правила', {'fields': ('sequential', 'pass_percent', 'certificate', 'reviews_on', 'auto_mode')}),
        ('Служебное', {'fields': ('enrollments_count', 'created', 'updated')}),
        ('Остановить запись и работы', {'fields': (), 'description': DISABLE_NOTE}),
    )
    readonly_fields = ('site_links', 'enrollments_count', 'created', 'updated')
    inlines = [ModuleInline, LessonInline]
    actions = ('hide', 'unhide', 'publish', 'unpublish')

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(lessons_total=Count('lessons', distinct=True))

    def get_changeform_initial_data(self, request):
        data = super().get_changeform_initial_data(request)
        data.setdefault('author', request.user.profile.pk)
        return data

    def save_model(self, request, obj, form, change):
        if not obj.key:
            from judge.models.course import new_key
            obj.key = new_key()
        super().save_model(request, obj, form, change)

    def changelist_view(self, request, extra_context=None):
        if request.method == 'GET' and not request.GET:
            self.message_user(request, DISABLE_NOTE, messages.INFO)
        return super().changelist_view(request, extra_context)

    @admin.display(description=_('author'), ordering='author__user__username')
    def author_link(self, obj):
        return format_html('<a href="{}">{}</a>', reverse('user_page', args=[obj.author.user.username]),
                           obj.author.user.username)

    @admin.display(description='Уроков', ordering='lessons_total')
    def lesson_count(self, obj):
        return obj.lessons_total

    @admin.display(description='На сайте')
    def site_links(self, obj):
        if not obj.pk or not obj.key:
            return '—'
        return format_html('<a href="{}">страница</a> · <a href="{}">конструктор</a> · <a href="{}">слушатели</a>',
                           reverse('course_detail', args=[obj.key]), reverse('course_edit', args=[obj.key]),
                           reverse('course_students', args=[obj.key]))

    @admin.action(description='Скрыть выбранные курсы')
    def hide(self, request, queryset):
        self.message_user(request, 'Скрыто: %d' % queryset.update(is_hidden=True), messages.SUCCESS)

    @admin.action(description='Показать выбранные курсы')
    def unhide(self, request, queryset):
        self.message_user(request, 'Показано: %d' % queryset.update(is_hidden=False), messages.SUCCESS)

    @admin.action(description='Опубликовать выбранные курсы')
    def publish(self, request, queryset):
        self.message_user(request, 'Опубликовано: %d' % queryset.update(status=Course.PUBLISHED), messages.SUCCESS)

    @admin.action(description='Перевести выбранные курсы в черновики')
    def unpublish(self, request, queryset):
        self.message_user(request, 'В черновиках: %d' % queryset.update(status=Course.DRAFT), messages.SUCCESS)


class QuestionInline(admin.StackedInline):
    model = CourseQuestion
    extra = 0
    fields = ('order', 'type', 'text', 'points', 'explanation')
    show_change_link = True


class BlockInline(admin.StackedInline):
    model = CourseBlock
    extra = 0
    fields = ('order', 'type', 'title', 'text', 'youtube_id', 'image', 'file', 'problem', 'points', 'is_required',
              'data')
    raw_id_fields = ('problem',)
    show_change_link = True


class CourseLessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'module', 'order', 'is_draft', 'is_required')
    list_filter = ('is_draft', 'is_required')
    search_fields = ('title', 'course__title')
    raw_id_fields = ('course', 'module')
    inlines = [BlockInline]

    def has_add_permission(self, request):
        return False


class OptionInline(admin.TabularInline):
    model = CourseOption
    extra = 0
    fields = ('order', 'text', 'is_correct')


class CourseQuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'block', 'type', 'points')
    search_fields = ('text', 'block__lesson__course__title')
    raw_id_fields = ('block',)
    inlines = [OptionInline]

    def has_module_permission(self, request):
        return False


class CourseBlockAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'type', 'order')
    raw_id_fields = ('lesson', 'problem')
    inlines = [QuestionInline]

    def has_module_permission(self, request):
        return False


class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('profile', 'course', 'joined', 'completed_at', 'certificate_code')
    list_filter = ('completed_at',)
    search_fields = ('profile__user__username', 'course__title', 'certificate_code')
    list_select_related = ('profile__user', 'course')
    raw_id_fields = ('profile', 'course', 'last_lesson')
    date_hierarchy = 'joined'


class CourseWorkAdmin(admin.ModelAdmin):
    list_display = ('learner', 'block', 'status', 'grade', 'submitted')
    list_filter = ('status',)
    search_fields = ('enrollment__profile__user__username', 'block__lesson__course__title')
    list_select_related = ('enrollment__profile__user', 'block__lesson')
    raw_id_fields = ('enrollment', 'block', 'graded_by')
    date_hierarchy = 'submitted'

    @admin.display(description=_('user'))
    def learner(self, obj):
        return obj.enrollment.profile.user.username


class CourseCommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'lesson', 'short', 'created')
    search_fields = ('text', 'author__user__username')
    raw_id_fields = ('author', 'lesson', 'parent')

    @admin.display(description=_('text'))
    def short(self, obj):
        return obj.text[:100]


class CourseReviewAdmin(admin.ModelAdmin):
    list_display = ('profile', 'course', 'rating', 'created')
    list_filter = ('rating',)
    search_fields = ('profile__user__username', 'course__title', 'text')
    raw_id_fields = ('profile', 'course')
