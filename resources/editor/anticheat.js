/* Contest integrity: warns when a participant leaves the contest tab and
 * reports it to the server. The server decides when to disqualify. */
(function (window, document) {
    'use strict';

    var cfg = window.OLYMP_ANTICHEAT;
    if (!cfg) return;

    var T = cfg.t;
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
            showModal(T.dq, T.dqText, T.ok, function () { location.reload(); }, true);
            return;
        }
        if (res.counted) {
            warnings = res.warnings;
            updateBadge();
            var left = res.max - res.warnings;
            showModal(T.warning + ' ' + res.warnings + ' / ' + res.max,
                T.rule + ' ' + (left > 0 ? T.left + ' ' + left + '.' : T.last),
                T.back);
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

    // Going to another page of the site also hides this one for a moment; that is not a violation.
    // A download link or a cancelled form also fires beforeunload without leaving, so the flag
    // clears itself after a few seconds; otherwise every later tab switch would be missed.
    var leaving = false;
    var leavingTimer = null;
    function markLeaving() {
        leaving = true;
        clearTimeout(leavingTimer);
        leavingTimer = setTimeout(function () { leaving = false; }, 3000);
    }
    window.addEventListener('beforeunload', markLeaving);
    window.addEventListener('pagehide', markLeaving);
    window.addEventListener('pageshow', function () { leaving = false; });

    // Switching to another tab of this site (the Compiler, the problem list) is allowed.
    // Every page of the site notes in localStorage when it becomes active (see base.html).
    function anotherSiteTabActive() {
        try {
            var mark = JSON.parse(localStorage.getItem('olymp-active-tab') || 'null');
            return mark && mark.id !== window.OLYMP_TAB_ID && Date.now() - mark.t < 2000;
        } catch (e) {
            return false;
        }
    }

    document.addEventListener('visibilitychange', function () {
        if (document.visibilityState !== 'hidden') return;
        setTimeout(function () {
            if (!leaving && document.visibilityState === 'hidden' && !anotherSiteTabActive()) {
                report('hidden', 'вкладка скрыта');
            }
        }, 700);
    });

    window.addEventListener('blur', function () {
        setTimeout(function () {
            if (leaving || document.hasFocus() || anotherSiteTabActive()) return;
            // Focus moving into an iframe on our own page is not leaving the page.
            var active = document.activeElement;
            if (active && active.tagName === 'IFRAME') return;
            report('blur', 'окно потеряло фокус');
        }, 400);
    });

    var badge = document.createElement('div');
    function updateBadge() {
        badge.className = 'ac-badge' + (warnings ? ' ac-warned' : '');
        badge.textContent = T.badge + ' ' + warnings + ' / ' + cfg.max;
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
