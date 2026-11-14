import json
import os

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, JsonResponse
from django.utils.html import escape

# One JSON object per line, written by scripts/server/autodeploy.sh after every deploy, rollback or skip.
DEFAULT_FILE = os.path.join(settings.BASE_DIR, '.deploy-history.jsonl')
LIMIT = 20


def read_history(limit=LIMIT):
    path = getattr(settings, 'DMOJ_DEPLOY_HISTORY_FILE', DEFAULT_FILE)
    try:
        with open(path, encoding='utf-8') as f:
            lines = f.readlines()[-limit:]
    except OSError:
        return []
    rows = []
    for line in lines:
        try:
            rows.append(json.loads(line))
        except ValueError:
            continue
    rows.reverse()
    return rows


@staff_member_required
def deploy_status(request):
    rows = read_history()
    if request.GET.get('format') == 'json':
        return JsonResponse({'deploys': rows}, json_dumps_params={'ensure_ascii': False})
    head = ['time', 'commit', 'result', 'seconds', 'subject', 'error']
    body = ''.join(
        '<tr>%s</tr>' % ''.join('<td>%s</td>' % escape(row.get(k, '')) for k in head) for row in rows
    )
    html = (
        '<!doctype html><meta charset="utf-8"><title>Deploys</title>'
        '<style>body{font:14px sans-serif;margin:2em}td,th{border:1px solid #bbb;padding:4px 8px;text-align:left}'
        'table{border-collapse:collapse}</style>'
        '<h1>Last %d deploys</h1><table><tr>%s</tr>%s</table>'
        '<p>JSON: <a href="?format=json">?format=json</a></p>'
        % (LIMIT, ''.join('<th>%s</th>' % h for h in head), body or '<tr><td colspan="6">no records yet</td></tr>')
    )
    return HttpResponse(html)
