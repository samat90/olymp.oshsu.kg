/* Online editor for olymp.oshsu.kg: Monaco + code runner.
 *
 * Used on the problem "solve" page and in the sandbox. Needs window.OLYMP_EDITOR = {
 *   monacoBase: '/static/vendor/monaco/vs', tokenUrl: '/runner/token/', csrf: '...', locale: 'ru'
 * }.
 */
(function (window, document) {
    'use strict';

    var cfg = window.OLYMP_EDITOR || {};
    var SETTINGS_KEY = 'olymp-editor-settings';
    var DEFAULTS = {
        theme: 'auto',          // auto | light | dark | contrast
        fontSize: 15,
        tabSize: 4,
        wordWrap: false,
        minimap: false,
        suggestions: true,
        ligatures: false,
        lineNumbers: true
    };

    var ACE_TO_MONACO = {
        c_cpp: 'cpp', python: 'python', java: 'java', csharp: 'csharp', javascript: 'javascript',
        golang: 'go', kotlin: 'kotlin', pascal: 'pascal', text: 'plaintext', perl: 'perl', ruby: 'ruby',
        rust: 'rust', php: 'php', swift: 'swift', scala: 'scala', lua: 'lua', haskell: 'plaintext',
        objectivec: 'objective-c', fsharp: 'fsharp', vbscript: 'vb', sh: 'shell', d: 'plaintext'
    };

    var T = {
        run: 'Запустить', running: 'Выполняется…', compiling: 'Компиляция…',
        compileError: 'Ошибка компиляции', ok: 'Готово', tle: 'Превышено время', mle: 'Превышена память',
        ole: 'Слишком большой вывод', rte: 'Ошибка во время выполнения', error: 'Ошибка',
        sampleOk: 'Совпало', sampleBad: 'Не совпало', expected: 'Ожидалось', got: 'Получено',
        noOutput: '(пустой вывод)', exitCode: 'код возврата', time: 'время', memory: 'память',
        network: 'Нет связи с сервером запуска. Попробуйте ещё раз.'
    };

    function loadSettings() {
        var s = {};
        try { s = JSON.parse(localStorage.getItem(SETTINGS_KEY) || '{}') || {}; } catch (e) { s = {}; }
        var out = {};
        for (var k in DEFAULTS) out[k] = (k in s) ? s[k] : DEFAULTS[k];
        return out;
    }

    function saveSettings(s) {
        try { localStorage.setItem(SETTINGS_KEY, JSON.stringify(s)); } catch (e) { /* private mode */ }
    }

    function siteIsDark() {
        var t = document.documentElement.getAttribute('data-theme') || 'auto';
        if (t === 'dark') return true;
        if (t === 'light') return false;
        return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    }

    function monacoTheme(settings) {
        if (settings.theme === 'light') return 'vs';
        if (settings.theme === 'dark') return 'vs-dark';
        if (settings.theme === 'contrast') return 'hc-black';
        return siteIsDark() ? 'vs-dark' : 'vs';
    }

    function monacoLanguage(ace) {
        return ACE_TO_MONACO[ace] || 'plaintext';
    }

    var monacoPromise = null;

    function loadMonaco() {
        if (monacoPromise) return monacoPromise;
        monacoPromise = new Promise(function (resolve, reject) {
            if (window.monaco && window.monaco.editor) return resolve(window.monaco);
            var base = cfg.monacoBase || '/static/vendor/monaco/vs';
            var script = document.createElement('script');
            script.src = base + '/loader.js';
            script.onerror = function () { reject(new Error('monaco loader')); };
            script.onload = function () {
                var amdRequire = window.require;
                var conf = {paths: {vs: base}};
                if (cfg.locale && cfg.locale !== 'en') {
                    conf['vs/nls'] = {availableLanguages: {'*': cfg.locale === 'ky' ? 'ru' : cfg.locale}};
                }
                amdRequire.config(conf);
                amdRequire(['vs/editor/editor.main'], function () { resolve(window.monaco); }, reject);
            };
            document.head.appendChild(script);
        });
        return monacoPromise;
    }

    var editors = [];

    function editorOptions(settings) {
        return {
            fontSize: settings.fontSize,
            tabSize: settings.tabSize,
            insertSpaces: true,
            detectIndentation: false,
            wordWrap: settings.wordWrap ? 'on' : 'off',
            minimap: {enabled: settings.minimap},
            quickSuggestions: settings.suggestions,
            suggestOnTriggerCharacters: settings.suggestions,
            wordBasedSuggestions: settings.suggestions ? 'currentDocument' : 'off',
            fontLigatures: settings.ligatures,
            lineNumbers: settings.lineNumbers ? 'on' : 'off'
        };
    }

    function applySettings(settings) {
        if (!window.monaco) return;
        window.monaco.editor.setTheme(monacoTheme(settings));
        editors.forEach(function (ed) {
            ed.updateOptions(editorOptions(settings));
            var model = ed.getModel();
            if (model) model.updateOptions({tabSize: settings.tabSize, insertSpaces: true});
        });
    }

    /* Creates an editor in `el`. Returns a promise of a small wrapper. */
    function create(el, opts) {
        opts = opts || {};
        return loadMonaco().then(function (monaco) {
            var settings = loadSettings();
            var options = editorOptions(settings);
            options.value = opts.value || '';
            options.language = monacoLanguage(opts.ace);
            options.theme = monacoTheme(settings);
            options.automaticLayout = true;
            options.scrollBeyondLastLine = false;
            options.readOnly = !!opts.readOnly;
            options.renderWhitespace = 'selection';
            options.bracketPairColorization = {enabled: true};
            options.guides = {bracketPairs: true, indentation: true};
            options.fontFamily = "'JetBrains Mono', 'Fira Code', Consolas, 'Courier New', monospace";
            options.padding = {top: 8};
            options.contextmenu = true;
            options.stickyScroll = {enabled: false};
            var editor = monaco.editor.create(el, options);
            editors.push(editor);

            var wrapper = {
                editor: editor,
                getValue: function () { return editor.getValue(); },
                setValue: function (v) { editor.setValue(v || ''); },
                setLanguage: function (ace) { monaco.editor.setModelLanguage(editor.getModel(), monacoLanguage(ace)); },
                focus: function () { editor.focus(); },
                layout: function () { editor.layout(); }
            };

            if (opts.onRun) {
                editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, opts.onRun);
            }
            if (opts.onSubmit) {
                editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.Enter, opts.onSubmit);
            }
            if (opts.onSave) {
                editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, opts.onSave);
            }
            if (opts.onChange) {
                editor.onDidChangeModelContent(function () { opts.onChange(editor.getValue()); });
            }
            if (opts.onExternalPaste) watchPaste(editor, el, opts.onExternalPaste);
            return wrapper;
        });
    }

    /* Text copied inside the page is fine to paste; anything else is reported. */
    var internalClipboard = [];

    function rememberCopy() {
        var text = '';
        var active = document.activeElement;
        editors.forEach(function (ed) {
            if (ed.hasTextFocus()) {
                var sel = ed.getSelection();
                text = sel && !sel.isEmpty() ? ed.getModel().getValueInRange(sel)
                    : ed.getModel().getLineContent(sel.startLineNumber) + '\n';
            }
        });
        if (!text && window.getSelection) text = String(window.getSelection());
        if (!text && active && typeof active.value === 'string') {
            text = active.value.substring(active.selectionStart, active.selectionEnd);
        }
        if (text) {
            internalClipboard.push(normalize(text));
            if (internalClipboard.length > 20) internalClipboard.shift();
        }
    }

    function normalize(text) {
        return String(text).replace(/\r\n/g, '\n').replace(/\s+$/g, '');
    }

    document.addEventListener('copy', rememberCopy, true);
    document.addEventListener('cut', rememberCopy, true);

    function watchPaste(editor, el, callback) {
        editor.onDidPaste(function (e) {
            var text = normalize(editor.getModel().getValueInRange(e.range));
            if (text.length < 40) return;
            for (var i = 0; i < internalClipboard.length; i++) {
                var known = internalClipboard[i];
                if (known.indexOf(text) !== -1 || text.indexOf(known) !== -1 && known.length > text.length * 0.8) return;
            }
            callback(text, function undo() { editor.trigger('anticheat', 'undo'); });
        });
    }

    /* ---- Runner ---- */

    function Runner(options) {
        this.problem = options.problem || null;
        this.token = null;
        this.expires = 0;
        this.url = null;
    }

    Runner.prototype.getToken = function () {
        var self = this;
        if (self.token && self.expires - Date.now() / 1000 > 30) return Promise.resolve(self.token);
        return fetch(cfg.tokenUrl || '/runner/token/', {
            method: 'POST',
            credentials: 'same-origin',
            headers: {'Content-Type': 'application/json', 'X-CSRFToken': cfg.csrf},
            body: JSON.stringify({problem: self.problem})
        }).then(function (r) {
            return r.json().then(function (data) {
                if (!data.ok) throw new Error(data.error || T.error);
                self.token = data.token;
                self.expires = data.expires;
                self.url = data.url.replace(/\/$/, '');
                return self.token;
            });
        });
    };

    Runner.prototype.run = function (language, source, stdin) {
        var self = this;
        return self.getToken().then(function (token) {
            return fetch(self.url + '/run', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({token: token, language: language, source: source, stdin: stdin || ''})
            }).catch(function () {
                throw new Error(T.network);
            }).then(function (r) {
                return r.json().catch(function () { throw new Error(T.network); });
            }).then(function (result) {
                if (result.status === 'error' && /устарела/.test(result.message || '')) self.token = null;
                return result;
            });
        });
    };

    /* ---- Result rendering ---- */

    function esc(s) {
        return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
            return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c];
        });
    }

    function verdictText(result) {
        if (result.status === 'compile_error') return T.compileError;
        if (result.status !== 'ok') return T.error;
        return {OK: T.ok, TLE: T.tle, MLE: T.mle, OLE: T.ole, RTE: T.rte}[result.verdict] || result.verdict;
    }

    function verdictClass(result) {
        if (result.status === 'ok' && result.verdict === 'OK') return 'oe-ok';
        if (result.status === 'compile_error') return 'oe-ce';
        return 'oe-bad';
    }

    function stats(result) {
        if (result.status !== 'ok') return '';
        var parts = [T.time + ' ' + result.time.toFixed(2) + ' c', T.memory + ' ' + Math.round(result.memory / 1024) + ' МБ'];
        if (result.exit_code) parts.push(T.exitCode + ' ' + result.exit_code);
        return parts.join(' · ');
    }

    function renderResult(result) {
        var html = '<div class="oe-verdict ' + verdictClass(result) + '">' + esc(verdictText(result)) +
            '<span class="oe-stats">' + esc(stats(result)) + '</span></div>';
        if (result.status === 'compile_error') {
            html += '<pre class="oe-out oe-err">' + esc(result.compile_output) + '</pre>';
        } else if (result.status !== 'ok') {
            html += '<pre class="oe-out oe-err">' + esc(result.message) + '</pre>';
        } else {
            html += '<pre class="oe-out">' + (result.stdout ? esc(result.stdout) : '<span class="oe-muted">' + T.noOutput + '</span>') + '</pre>';
            if (result.stderr) html += '<pre class="oe-out oe-err">' + esc(result.stderr) + '</pre>';
        }
        return html;
    }

    function sameOutput(a, b) {
        function lines(s) {
            return String(s || '').replace(/\r\n/g, '\n').split('\n').map(function (l) { return l.replace(/\s+$/, ''); })
                .join('\n').replace(/\n+$/, '');
        }
        return lines(a) === lines(b);
    }

    function renderSample(index, sample, result) {
        var passed = result.status === 'ok' && result.verdict === 'OK' && sameOutput(result.stdout, sample.output);
        var head = '<div class="oe-sample-head ' + (passed ? 'oe-ok' : 'oe-bad') + '">' +
            (passed ? '✓ ' : '✗ ') + 'Пример ' + (index + 1) + ': ' +
            esc(passed ? T.sampleOk : (result.status === 'ok' && result.verdict === 'OK' ? T.sampleBad : verdictText(result))) +
            '<span class="oe-stats">' + esc(stats(result)) + '</span></div>';
        if (passed) return {passed: true, html: head};
        var body = '';
        if (result.status === 'compile_error') {
            body = '<pre class="oe-out oe-err">' + esc(result.compile_output) + '</pre>';
        } else if (result.status !== 'ok') {
            body = '<pre class="oe-out oe-err">' + esc(result.message) + '</pre>';
        } else {
            body = '<div class="oe-compare"><div><div class="oe-label">' + T.expected + '</div><pre class="oe-out">' +
                esc(sample.output) + '</pre></div><div><div class="oe-label">' + T.got + '</div><pre class="oe-out">' +
                (result.stdout ? esc(result.stdout) : '<span class="oe-muted">' + T.noOutput + '</span>') + '</pre></div></div>';
            if (result.stderr) body += '<pre class="oe-out oe-err">' + esc(result.stderr) + '</pre>';
        }
        return {passed: false, html: head + body, stop: result.status === 'compile_error'};
    }

    /* ---- Settings dialog ---- */

    function openSettings() {
        var s = loadSettings();
        var old = document.getElementById('oe-settings');
        if (old) old.remove();
        var box = document.createElement('div');
        box.id = 'oe-settings';
        box.className = 'oe-modal-backdrop';
        box.innerHTML =
            '<div class="oe-modal" role="dialog" aria-label="Настройки редактора">' +
            '<div class="oe-modal-title">Настройки редактора<button type="button" class="oe-close" aria-label="Закрыть">×</button></div>' +
            row('Тема', '<select name="theme"><option value="auto">Как на сайте</option><option value="light">Светлая</option>' +
                '<option value="dark">Тёмная</option><option value="contrast">Контрастная</option></select>') +
            row('Размер шрифта', '<select name="fontSize">' + [12, 13, 14, 15, 16, 18, 20, 22, 24].map(function (n) {
                return '<option value="' + n + '">' + n + '</option>';
            }).join('') + '</select>') +
            row('Отступ', '<select name="tabSize"><option value="2">2 пробела</option><option value="4">4 пробела</option>' +
                '<option value="8">8 пробелов</option></select>') +
            check('wordWrap', 'Переносить длинные строки') +
            check('minimap', 'Мини-карта кода справа') +
            check('suggestions', 'Подсказки при наборе') +
            check('lineNumbers', 'Номера строк') +
            check('ligatures', 'Лигатуры шрифта') +
            '<div class="oe-modal-foot"><button type="button" class="oe-btn oe-reset">Сбросить</button>' +
            '<button type="button" class="oe-btn oe-primary oe-done">Готово</button></div></div>';
        document.body.appendChild(box);

        function row(label, control) { return '<label class="oe-row"><span>' + label + '</span>' + control + '</label>'; }
        function check(name, label) {
            return '<label class="oe-row oe-check"><input type="checkbox" name="' + name + '"><span>' + label + '</span></label>';
        }

        function fill(values) {
            box.querySelectorAll('select, input').forEach(function (input) {
                if (input.type === 'checkbox') input.checked = !!values[input.name];
                else input.value = String(values[input.name]);
            });
        }

        function read() {
            box.querySelectorAll('select, input').forEach(function (input) {
                if (input.type === 'checkbox') s[input.name] = input.checked;
                else if (input.name === 'theme') s.theme = input.value;
                else s[input.name] = parseInt(input.value, 10);
            });
            saveSettings(s);
            applySettings(s);
        }

        fill(s);
        box.addEventListener('change', read);
        box.querySelector('.oe-reset').onclick = function () {
            s = Object.assign({}, DEFAULTS);
            fill(s);
            saveSettings(s);
            applySettings(s);
        };
        function close() { box.remove(); }
        box.querySelector('.oe-close').onclick = close;
        box.querySelector('.oe-done').onclick = close;
        box.addEventListener('click', function (e) { if (e.target === box) close(); });
        document.addEventListener('keydown', function onKey(e) {
            if (e.key === 'Escape') { close(); document.removeEventListener('keydown', onKey); }
        });
    }

    // Follow the site's light/dark switch.
    new MutationObserver(function () { applySettings(loadSettings()); })
        .observe(document.documentElement, {attributes: true, attributeFilter: ['data-theme']});
    if (window.matchMedia) {
        var mq = window.matchMedia('(prefers-color-scheme: dark)');
        if (mq.addEventListener) mq.addEventListener('change', function () { applySettings(loadSettings()); });
    }

    window.OlympEditor = {
        create: create,
        load: loadMonaco,
        Runner: Runner,
        renderResult: renderResult,
        renderSample: renderSample,
        openSettings: openSettings,
        monacoLanguage: monacoLanguage,
        escape: esc,
        T: T
    };
})(window, document);
