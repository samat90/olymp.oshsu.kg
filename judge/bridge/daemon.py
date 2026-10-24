import logging
import signal
import threading
from functools import partial

from django.conf import settings

from judge.bridge.django_handler import DjangoHandler
from judge.bridge.judge_handler import JudgeHandler
from judge.bridge.judge_list import JudgeList
from judge.bridge.server import Server
from judge.judge_priority import CONTEST_SUBMISSION_PRIORITY, DEFAULT_PRIORITY
from judge.models import Judge, Submission

logger = logging.getLogger('judge.bridge')


def reset_judges():
    Judge.objects.update(online=False, ping=None, load=None)


def unfinished_submissions():
    """Submissions that were waiting or being graded when the bridge stopped. They go back to
    the queue instead of being marked as internal errors, so a restart during an olympiad
    does not lose anyone's solution."""
    rows = list(Submission.objects.filter(status__in=Submission.IN_PROGRESS_GRADING_STATUS)
                .order_by('id').values_list('id', 'problem__code', 'language__key', 'source__source',
                                            'contest_object_id'))
    Submission.objects.filter(id__in=[row[0] for row in rows]).update(status='QU', result=None, error=None)
    return rows


def judge_daemon():
    reset_judges()
    pending = unfinished_submissions()
    judges = JudgeList()
    for sub_id, problem, language, source, contest_id in pending:
        if source is None:
            Submission.objects.filter(id=sub_id).update(status='IE', result='IE', error=None)
            continue
        priority = CONTEST_SUBMISSION_PRIORITY if contest_id else DEFAULT_PRIORITY
        judges.judge(sub_id, problem, language, source, None, priority)
    if pending:
        logger.info('Queued %d unfinished submissions again', len(pending))

    judge_server = Server(settings.BRIDGED_JUDGE_ADDRESS, partial(JudgeHandler, judges=judges))
    django_server = Server(settings.BRIDGED_DJANGO_ADDRESS, partial(DjangoHandler, judges=judges))

    threading.Thread(target=django_server.serve_forever).start()
    threading.Thread(target=judge_server.serve_forever).start()

    stop = threading.Event()

    def signal_handler(signum, _):
        logger.info('Exiting due to %s', signal.Signals(signum).name)
        stop.set()

    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, 'SIGQUIT'):
        signal.signal(signal.SIGQUIT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        stop.wait()
    finally:
        django_server.shutdown()
        judge_server.shutdown()
