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
    var stdin = $('#oe-stdin');
    var form = $('#problem_submit');
    var runner = data.runnerEnabled ? new E.Runner({problem: data.problem}) : null;
    var editor = null;
    var busy = false;
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

    function setStatus(text) { if (status) status.textContent = text || ''; }

    /* ---- panel tabs ---- */
    function showPane(name) {
        document.querySelectorAll('.oe-tab').forEach(function (t) { t.classList.toggle('oe-active', t.dataset.pane === name); });
        document.querySelectorAll('.oe-pane').forEach(function (p) { p.classList.toggle('oe-active', p.dataset.pane === name); });
    }
    document.querySelectorAll('.oe-tab').forEach(function (tab) {
        tab.addEventListener('click', function () { showPane(tab.dataset.pane); });
    });

    if (stdin) {
        var stdinKey = 'stdin:' + data.problem;
        var savedInput = storageGet(stdinKey);
        stdin.value = savedInput !== null ? savedInput : (data.samples.length ? data.samples[0].input : '');
        stdin.addEventListener('input', function () { storageSet(stdinKey, stdin.value); });
        stdin.addEventListener('keydown', function (e) {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') { e.preventDefault(); run(); }
        });
    }

    var badge = $('#oe-samples-badge');
    if (badge) badge.textContent = data.samples.length || '';
    var samplesBtn = $('#oe-samples-btn');
    if (samplesBtn && !data.samples.length) {
        samplesBtn.disabled = true;
        samplesBtn.title = 'В условии не найдено примеров';
    }

    /* ---- running ---- */
    function language() {
        var lang = languages[String(select.value)];
        return lang ? lang.key : null;
    }

    function setBusy(on, text) {
        busy = on;
        ['#oe-run-btn', '#oe-samples-btn'].forEach(function (sel) {
            var b = $(sel);
            if (b) b.disabled = on || (sel === '#oe-samples-btn' && !data.samples.length);
        });
        setStatus(on ? text : '');
    }

    function run() {
        if (!runner || busy || !editor) return;
        showPane('result');
        var out = $('#oe-result');
        out.innerHTML = '<div class="oe-placeholder">' + E.T.running + '</div>';
        setBusy(true, E.T.running);
        runner.run(language(), editor.getValue(), stdin.value).then(function (result) {
            out.innerHTML = E.renderResult(result);
        }).catch(function (err) {
            out.innerHTML = E.renderResult({status: 'error', message: err.message});
        }).then(function () { setBusy(false); });
    }

    function runSamples() {
        if (!runner || busy || !editor || !data.samples.length) return;
        showPane('samples');
        var out = $('#oe-samples');
        out.innerHTML = '';
        setBusy(true, E.T.running);
        var source = editor.getValue();
        var lang = language();
        var passed = 0;
        var i = 0;

        function next() {
            if (i >= data.samples.length) return Promise.resolve();
            var index = i++;
            var holder = document.createElement('div');
            holder.innerHTML = '<div class="oe-sample-head">Пример ' + (index + 1) + ': ' + E.T.running + '</div>';
            out.appendChild(holder);
            return runner.run(lang, source, data.samples[index].input).then(function (result) {
                var r = E.renderSample(index, data.samples[index], result);
                holder.innerHTML = r.html;
                if (r.passed) passed++;
                if (!r.stop) return next();
            });
        }

        next().catch(function (err) {
            out.insertAdjacentHTML('beforeend', E.renderResult({status: 'error', message: err.message}));
        }).then(function () {
            setBusy(false);
            if (badge) {
                badge.textContent = passed + '/' + data.samples.length;
                badge.className = 'oe-badge ' + (passed === data.samples.length ? 'oe-ok' : 'oe-bad');
            }
        });
    }

    var runBtn = $('#oe-run-btn');
    if (runBtn) runBtn.addEventListener('click', run);
    if (samplesBtn) samplesBtn.addEventListener('click', runSamples);
    $('#oe-settings-btn').addEventListener('click', E.openSettings);

    /* ---- submit ---- */
    var submitting = false;
    form.addEventListener('submit', function (e) {
        if (!editor) { e.preventDefault(); return; }
        var source = editor.getValue();
        if (!source.trim()) {
            e.preventDefault();
            setStatus('Код пустой');
            return;
        }
        if (source.length > 65536) {
            e.preventDefault();
            alert('Код должен быть не длиннее 65536 символов.');
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
        onSave: function () { storageSet(draftKey(currentLang), editor.getValue()); setStatus('Черновик сохранён'); },
        onChange: function (value) { if (currentLang) storageSet(draftKey(currentLang), value); },
        onExternalPaste: window.OlympAnticheat ? window.OlympAnticheat.onPaste : null
    }).then(function (ed) {
        editor = ed;
        var loading = document.querySelector('.oe-editor-loading');
        if (loading) loading.remove();
        ed.focus();
    }).catch(function () {
        $('#oe-editor').innerHTML = '<div class="oe-editor-loading">Не удалось загрузить редактор. Обновите страницу.</div>';
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
    });

    var panel = $('#oe-panel');
    var panelHeight = storageGet('oe-panel-h');
    if (panel && panelHeight) panel.style.flexBasis = panelHeight + 'px';
    dragger($('#oe-hsplit'), function (ev) {
        var work = panel.parentNode.getBoundingClientRect();
        var h = Math.min(Math.max(work.bottom - ev.clientY, 90), work.height - 160);
        panel.style.flexBasis = h + 'px';
        storageSet('oe-panel-h', Math.round(h));
    });
});
