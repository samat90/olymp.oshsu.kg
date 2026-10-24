/* Problem "solve" page: statement on the left, editor and run panel on the right. */
document.addEventListener('DOMContentLoaded', function () {
    'use strict';

    var data = window.OLYMP_SOLVE;
    var E = window.OlympEditor;
    var $ = function (sel) { return document.querySelector(sel); };
    var languages = {};
    data.languages.forEach(function (lang) { languages[String(lang.id)] = lang; });

    var select = $('#id_language');
    var status = $('#oe-status');
    var form = $('#problem_submit');
    var runner = data.runnerEnabled ? new E.Runner({problem: data.problem}) : null;
    var editor = null;
    var currentLang = select ? select.value : null;

    function storageGet(key) { try { return localStorage.getItem(key); } catch (e) { return null; } }
    function storageSet(key, value) { try { localStorage.setItem(key, value); } catch (e) { /* ignore */ } }

    function draftKey(langId) {
        var lang = languages[String(langId)];
        return 'draft:' + data.problem + ':' + (lang ? lang.key : langId);
    }

    function sourceFor(langId) {
        var saved = storageGet(draftKey(langId));
        if (saved !== null) return saved;
        var lang = languages[String(langId)];
        return lang ? lang.template || '' : '';
    }

    var statusTimer = null;
    function setStatus(text) {
        if (!status) return;
        status.textContent = text || '';
        clearTimeout(statusTimer);
        if (text) statusTimer = setTimeout(function () { status.textContent = ''; }, 3000);
    }

    /* ---- running: the program works in the console below the editor ---- */
    var terminal = $('#oe-terminal');
    var cons = runner && terminal && window.Terminal ? new window.OlympConsole(terminal, runner) : null;
    var runBtn = $('#oe-run-btn');
    var stopBtn = $('#oe-stop-btn');
    if (cons) cons.onState = function (on) {
        if (runBtn) runBtn.disabled = on;
        if (stopBtn) stopBtn.disabled = !on;
    };

    function language() {
        var lang = languages[String(select.value)];
        return lang ? lang.key : null;
    }

    function run() {
        if (!cons || !editor || cons.running()) return;
        cons.run(language(), editor.getValue());
    }

    if (runBtn) runBtn.addEventListener('click', run);
    if (stopBtn) stopBtn.addEventListener('click', function () { if (cons) cons.stop(); });

    /* ---- submit ---- */
    var submitting = false;
    form.addEventListener('submit', function (e) {
        if (!editor) { e.preventDefault(); return; }
        var source = editor.getValue();
        if (!source.trim()) {
            e.preventDefault();
            setStatus(E.T.emptyCode);
            return;
        }
        if (source.length > 65536) {
            e.preventDefault();
            alert(E.T.tooLong);
            return;
        }
        if (submitting) { e.preventDefault(); return; }
        submitting = true;
        $('#id_source').value = source;
        var btn = $('#oe-submit-btn');
        if (btn) btn.disabled = true;
    });

    /* ---- editor ---- */
    var initial = data.initialSource !== null ? data.initialSource : (select ? sourceFor(select.value) : '');
    var lang0 = select ? languages[String(select.value)] : null;

    E.create($('#oe-editor'), {
        value: initial,
        ace: lang0 ? lang0.ace : 'text',
        onRun: run,
        onSubmit: function () { if (form.requestSubmit) form.requestSubmit(); else form.submit(); },
        onSave: function () { storageSet(draftKey(currentLang), editor.getValue()); setStatus(E.T.saved); },
        onChange: function (value) { if (currentLang) storageSet(draftKey(currentLang), value); },
        onExternalPaste: window.OlympAnticheat ? window.OlympAnticheat.onPaste : null
    }).then(function (ed) {
        editor = ed;
        var loading = document.querySelector('.oe-editor-loading');
        if (loading) loading.remove();
        ed.focus();
    }).catch(function () {
        $('#oe-editor').innerHTML = '<div class="oe-editor-loading">' + E.escape(E.T.editorFailed) + '</div>';
    });

    if (select) {
        select.addEventListener('change', function () {
            if (!editor) return;
            var lang = languages[String(select.value)];
            var old = editor.getValue();
            var oldLang = languages[String(currentLang)];
            // Keep the code when the user only switches between versions of one language (C++14 -> C++17).
            var keep = oldLang && lang && oldLang.ace === lang.ace && old.trim() && old !== oldLang.template;
            currentLang = select.value;
            editor.setLanguage(lang ? lang.ace : 'text');
            if (!keep) editor.setValue(sourceFor(select.value));
            storageSet(draftKey(currentLang), editor.getValue());
        });
    }

    /* ---- resizable split ---- */
    function dragger(handle, onMove) {
        if (!handle) return;
        handle.addEventListener('mousedown', function (e) {
            e.preventDefault();
            handle.classList.add('oe-dragging');
            function move(ev) { onMove(ev); }
            function up() {
                handle.classList.remove('oe-dragging');
                document.removeEventListener('mousemove', move);
                document.removeEventListener('mouseup', up);
            }
            document.addEventListener('mousemove', move);
            document.addEventListener('mouseup', up);
        });
    }

    var solve = $('#oe-solve');
    var split = storageGet('oe-split');
    if (split) solve.style.gridTemplateColumns = split + 'fr 6px 1fr';
    dragger($('#oe-splitter'), function (ev) {
        var rect = solve.getBoundingClientRect();
        var x = Math.min(Math.max(ev.clientX - rect.left, 260), rect.width - 320);
        var ratio = (x / (rect.width - x - 6)).toFixed(3);
        solve.style.gridTemplateColumns = ratio + 'fr 6px 1fr';
        storageSet('oe-split', ratio);
        if (cons) cons.refit();
    });

    var panel = $('#oe-panel');
    var panelHeight = storageGet('oe-panel-h');
    if (panel && panelHeight) panel.style.flexBasis = panelHeight + 'px';
    dragger($('#oe-hsplit'), function (ev) {
        var work = panel.parentNode.getBoundingClientRect();
        var h = Math.min(Math.max(work.bottom - ev.clientY, 90), work.height - 160);
        panel.style.flexBasis = h + 'px';
        storageSet('oe-panel-h', Math.round(h));
        if (cons) cons.refit();
    });
});
