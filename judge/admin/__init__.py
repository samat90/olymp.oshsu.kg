from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import User
from django.contrib.flatpages.models import FlatPage

from judge.admin.comments import CommentAdmin
from judge.admin.contest import ContestAdmin, ContestParticipationAdmin, ContestTagAdmin
from judge.admin.interface import BlogPostAdmin, FlatPageAdmin, LicenseAdmin, LogEntryAdmin, NavigationBarAdmin
from judge.admin.organization import ClassAdmin, OrganizationAdmin, OrganizationRequestAdmin
from judge.admin.problem import ProblemAdmin, ProblemPointsVoteAdmin
from judge.admin.profile import ProfileAdmin, UserAdmin
from judge.admin.quiz import GameSessionAdmin, QuizAdmin, QuizReportAdmin
from judge.admin.runtime import JudgeAdmin, LanguageAdmin
from judge.admin.submission import SubmissionAdmin
from judge.admin.taxon import ProblemGroupAdmin, ProblemTypeAdmin
from judge.admin.ticket import TicketAdmin
from judge.admin.workspace import TypingResultAdmin, WorkspaceFileAdmin
from judge.models import BlogPost, Class, Comment, CommentLock, Contest, ContestParticipation, \
    ContestTag, GameSession, Judge, Language, License, MiscConfig, NavigationBar, Organization, \
    OrganizationRequest, Problem, ProblemGroup, ProblemPointsVote, ProblemType, Profile, Quiz, QuizReport, \
    Submission, Ticket, TypingResult, WorkspaceFile

admin.site.register(BlogPost, BlogPostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(CommentLock)
admin.site.register(Contest, ContestAdmin)
admin.site.register(ContestParticipation, ContestParticipationAdmin)
admin.site.register(ContestTag, ContestTagAdmin)
admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageAdmin)
admin.site.register(Judge, JudgeAdmin)
admin.site.register(Language, LanguageAdmin)
admin.site.register(License, LicenseAdmin)
admin.site.register(LogEntry, LogEntryAdmin)
admin.site.register(MiscConfig)
admin.site.register(NavigationBar, NavigationBarAdmin)
admin.site.register(Class, ClassAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(OrganizationRequest, OrganizationRequestAdmin)
admin.site.register(Problem, ProblemAdmin)
admin.site.register(ProblemGroup, ProblemGroupAdmin)
admin.site.register(ProblemPointsVote, ProblemPointsVoteAdmin)
admin.site.register(ProblemType, ProblemTypeAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(WorkspaceFile, WorkspaceFileAdmin)
admin.site.register(TypingResult, TypingResultAdmin)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(QuizReport, QuizReportAdmin)
admin.site.register(GameSession, GameSessionAdmin)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# The quiz lives in the judge app too; show it as its own block in the admin, apart from olympiads.
QUIZ_MODELS = {'Quiz', 'QuizReport', 'GameSession'}
_judge_app_list = admin.site.get_app_list


def get_app_list(request, app_label=None):
    apps = []
    for app in _judge_app_list(request, app_label):
        if app['app_label'] != 'judge':
            apps.append(app)
            continue
        quiz = [m for m in app['models'] if m['object_name'] in QUIZ_MODELS]
        rest = [m for m in app['models'] if m['object_name'] not in QUIZ_MODELS]
        if rest:
            apps.append(dict(app, name='Олимпиады и задачи', models=rest))
        if quiz:
            apps.append(dict(app, name='Викторина', models=quiz, app_url=quiz[0].get('admin_url') or app['app_url']))
    return apps


admin.site.get_app_list = get_app_list
