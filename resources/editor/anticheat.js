/* Contest integrity: warns when a participant leaves the contest tab and
 * reports it to the server. The server decides when to disqualify. */
(function (window, document) {
    'use strict';

    var cfg = window.OLYMP_ANTICHEAT;
    if (!cfg) return;

    var warnings = cfg.warnings;
    var lastSent = 0;
    var queueKey = 'anticheat-queue:' + cfg.contest;
    var disqualified = false;

    function readQueue() {
        try { return JSON.parse(localStorage.getItem(queueKey) || '[]'); } catch (e) { return []; }
    }
    function writeQueue(q) {
        try { localStorage.setItem(queueKey, JSON.stringify(q.slice(-20))); } catch (e) { /* ignore */ }
    }

    function send(event) {
        return fetch(cfg.url, {
            method: 'POST',
            credentials: 'same-origin',
            keepalive: true,
            headers: {'Content-Type': 'application/json', 'X-CSRFToken': cfg.csrf},
            body: JSON.stringify(event)
        }).then(function (r) { return r.json(); });
    }

    function flushQueue() {
        var q = readQueue();
        if (!q.length) return;
        writeQueue([]);
        q.reduce(function (p, ev) {
            return p.then(function () { return send(ev).then(handle); });
        }, Promise.resolve()).catch(function () { writeQueue(readQueue().concat(q)); });
    }

    function report(kind, detail) {
        if (disqualified) return;
        var now = Date.now();
        // "blur" and "hidden" arrive together on a tab switch; send one of them.
        if (kind !== 'paste' && now - lastSent < 1500) return;
        lastSent = now;
        var event = {kind: kind, detail: detail || ''};
        send(event).then(handle).catch(function () {
            writeQueue(readQueue().concat([event]));
        });
    }

    function handle(res) {
        if (!res || !res.tracking) return;
        if (res.disqualified) {
            disqualified = true;
            showModal('Вы дисквалифицированы',
                'Вы слишком часто покидали страницу олимпиады. Ваши решения больше не учитываются в рейтинге. ' +
                'Если это ошибка, обратитесь к наблюдателю.', 'Понятно', function () { location.reload(); }, true);
            return;
        }
        if (res.counted) {
            warnings = res.warnings;
            updateBadge();
            var left = res.max - res.warnings;
            showModal('Предупреждение ' + res.warnings + ' из ' + res.max,
                'Во время олимпиады нельзя переходить на другие вкладки, в другие программы и вставлять код со стороны. ' +
                (left > 0
                    ? 'Осталось предупреждений: ' + left + '. После них следующее нарушение приведёт к дисквалификации.'
                    : 'Это было последнее предупреждение. Следующее нарушение приведёт к дисквалификации.'),
                'Вернуться к олимпиаде');
        }
    }

    var modal = null;

    function showModal(title, text, button, onClose, danger) {
        if (modal) modal.remove();
        modal = document.createElement('div');
        modal.className = 'ac-backdrop';
        modal.innerHTML = '<div class="ac-modal' + (danger ? ' ac-danger' : '') + '" role="alertdialog" aria-modal="true">' +
            '<div class="ac-icon">!</div><div class="ac-title"></div><div class="ac-text"></div>' +
            '<button type="button" class="ac-btn"></button></div>';
        modal.querySelector('.ac-title').textContent = title;
        modal.querySelector('.ac-text').textContent = text;
        var btn = modal.querySelector('.ac-btn');
        btn.textContent = button;
        btn.addEventListener('click', function () {
            modal.remove();
            modal = null;
            if (onClose) onClose();
        });
        document.body.appendChild(modal);
        btn.focus();
    }

    document.addEventListener('visibilitychange', function () {
        if (document.visibilityState === 'hidden') report('hidden', 'вкладка скрыта');
    });

    window.addEventListener('blur', function () {
        // Focus moving into an iframe on our own page is not leaving the page.
        setTimeout(function () {
            var active = document.activeElement;
            if (active && active.tagName === 'IFRAME') return;
            if (document.hasFocus()) return;
            report('blur', 'окно потеряло фокус');
        }, 300);
    });

    var badge = document.createElement('div');
    function updateBadge() {
        badge.className = 'ac-badge' + (warnings ? ' ac-warned' : '');
        badge.textContent = 'Олимпиада: не покидайте вкладку · предупреждений ' + warnings + ' из ' + cfg.max;
    }
    document.addEventListener('DOMContentLoaded', function () {
        updateBadge();
        document.body.appendChild(badge);
    });

    window.addEventListener('online', flushQueue);
    flushQueue();

    window.OlympAnticheat = {
        onPaste: function (text, undo) {
            undo();
            report('paste', 'вставлено ' + text.length + ' символов');
        },
        warnings: function () { return warnings; }
    };
})(window, document);
