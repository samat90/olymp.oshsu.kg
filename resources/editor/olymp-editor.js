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
        lineNumbers: true,
        terminal: 'light'     // light | dark | black | blue
    };

    var ACE_TO_MONACO = {
        c_cpp: 'cpp', python: 'python', java: 'java', csharp: 'csharp', javascript: 'javascript',
        golang: 'go', kotlin: 'kotlin', pascal: 'pascal', text: 'plaintext', perl: 'perl', ruby: 'ruby',
        rust: 'rust', php: 'php', swift: 'swift', scala: 'scala', lua: 'lua', haskell: 'plaintext',
        objectivec: 'objective-c', fsharp: 'fsharp', vbscript: 'vb', sh: 'shell', d: 'plaintext'
    };

    var T = Object.assign({
        run: 'Запустить', running: 'Выполняется…', compiling: 'Компиляция…', queued: 'Ожидание в очереди…',
        compileError: 'Ошибка компиляции', ok: 'Готово', tle: 'Превышено время', mle: 'Превышена память',
        ole: 'Слишком большой вывод', rte: 'Ошибка во время выполнения', error: 'Ошибка', serverError: 'Ошибка сервера',
        sample: 'Пример', sampleOk: 'Совпало', sampleBad: 'Не совпало', expected: 'Ожидалось', got: 'Получено',
        noOutput: '(пустой вывод)', exitCode: 'код возврата', time: 'время', memory: 'память', sec: 'с', mb: 'МБ',
        network: 'Нет связи с сервером запуска. Попробуйте ещё раз.',
        editorSettings: 'Настройки редактора', theme: 'Тема', themeAuto: 'Как на сайте', themeLight: 'Светлая',
        themeDark: 'Тёмная', themeContrast: 'Контрастная', fontSize: 'Размер шрифта', indent: 'Отступ',
        spaces: 'пробелов', wordWrap: 'Переносить длинные строки', minimap: 'Мини-карта', suggestions: 'Подсказки',
        lineNumbers: 'Номера строк', ligatures: 'Лигатуры шрифта', reset: 'Сбросить', close: 'Закрыть',
        terminal: 'Консоль', term_light: 'Белая', term_dark: 'Тёмная', term_black: 'Чёрная', term_blue: 'Синяя',
        download: 'Скачать', kb: 'КБ', scratchUpload: 'Загрузить .sb3', scratchEditor: 'Редактор Scratch',
        scratchEmpty: 'Проект не загружен',
        scratchHint: 'Соберите программу в редакторе Scratch, сохраните её (Файл → Сохранить на компьютер) и загрузите сюда. ' +
            '«Спросить и ждать» читает строку ввода, «сказать» печатает строку.',
        scratchBad: 'Это не проект Scratch 3 (.sb3).', scratchTooBig: 'Проект больше 190 КБ.'
    }, window.OLYMP_STRINGS || {});

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

    // Colours of the program console (Compiler and the problem page).
    var TERMINALS = {
        light: {background: '#ffffff', foreground: '#1b2430', cursor: '#1b2430', selectionBackground: '#cfe0f5'},
        dark: {background: '#1e1e1e', foreground: '#e3e6ea', cursor: '#e3e6ea', selectionBackground: '#3a4250'},
        black: {background: '#000000', foreground: '#33ff66', cursor: '#33ff66', selectionBackground: '#1f4d2b'},
        blue: {background: '#0f2a4a', foreground: '#e8f0fb', cursor: '#ffd36b', selectionBackground: '#2a4f82'}
    };

    function terminalTheme() {
        return TERMINALS[loadSettings().terminal] || TERMINALS.light;
    }

    function applySettings(settings) {
        document.dispatchEvent(new CustomEvent('olymp-terminal-theme'));
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

    /* `stdin` may be a list: the program is compiled once and run on every input (result.runs). */
    /* `stdin` may be a list: the program is compiled once and run on every input (result.runs).
     * When the runner is busy (HTTP 503) the request waits in line and is retried a few times. */
    Runner.prototype.run = function (language, source, stdin, onWait, extra) {
        var self = this;
        var body = Object.assign({language: language, source: source}, extra || {});
        if (Array.isArray(stdin)) body.stdins = stdin; else body.stdin = stdin || '';
        var attempt = 0;

        function once(token) {
            body.token = token;
            return fetch(self.url + '/run', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(body)
            }).catch(function () {
                throw new Error(T.network);
            }).then(function (r) {
                if (r.status === 503 && attempt < 6) {
                    attempt++;
                    if (onWait) onWait(attempt);
                    var delay = 1500 + Math.random() * 2500 * attempt;
                    return new Promise(function (resolve) { setTimeout(resolve, delay); }).then(function () {
                        return once(token);
                    });
                }
                return r.json().catch(function () { throw new Error(T.network); });
            });
        }

        return self.getToken().then(once).then(function (result) {
            if (result.status === 'error' && /устарела/.test(result.message || '')) self.token = null;
            return result;
        });
    };

    /* ---- Terminal connection ----
     * Looks like a WebSocket (onopen, onmessage, onclose, send, close) for the interactive console.
     * Tries a real WebSocket first; when the network does not pass it (a proxy in the way), the same
     * session runs over plain HTTP requests: POST /poll/start, long-polled GET /poll/<id>, POST /poll/<id>/send.
     * After one failed WebSocket the page goes straight to HTTP. */

    var noWebSocket = false;
    try { noWebSocket = sessionStorage.getItem('olymp-no-ws') === '1'; } catch (e) { /* private mode */ }

    function TerminalSocket(runner) {
        var self = this;
        self.base = runner.url;
        self.readyState = 0;
        self.onopen = self.onmessage = self.onerror = self.onclose = function () {};
        if (noWebSocket || typeof WebSocket === 'undefined') {
            setTimeout(function () { self.usePolling(); }, 0);
            return;
        }
        var url = /^https?:/.test(self.base) ? self.base.replace(/^http/, 'ws') + '/session'
            : location.origin.replace(/^http/, 'ws') + self.base + '/session';
        var socket = self.socket = new WebSocket(url);
        var opened = false;
        socket.onopen = function () { opened = true; self.readyState = 1; self.onopen(); };
        socket.onmessage = function (event) { self.onmessage(event); };
        socket.onerror = function () { if (opened) self.onerror(); };
        socket.onclose = function () {
            if (opened) { self.readyState = 3; self.onclose(); return; }
            noWebSocket = true;
            try { sessionStorage.setItem('olymp-no-ws', '1'); } catch (e) { /* private mode */ }
            self.socket = null;
            self.usePolling();
        };
    }

    TerminalSocket.prototype.usePolling = function () {
        this.polling = true;
        this.queue = Promise.resolve();
        this.readyState = 1;
        this.onopen();
    };

    TerminalSocket.prototype.post = function (path, message) {
        return fetch(this.base + path, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(message)
        }).then(function (r) { return r.json(); });
    };

    TerminalSocket.prototype.deliver = function (message) {
        this.onmessage({data: JSON.stringify(message)});
    };

    TerminalSocket.prototype.finish = function () {
        if (this.readyState === 3) return;
        this.readyState = 3;
        this.onclose();
    };

    TerminalSocket.prototype.send = function (text) {
        var self = this;
        if (!self.polling) { if (self.socket) self.socket.send(text); return; }
        if (self.readyState !== 1) return;
        var message = JSON.parse(text);
        // Messages go one after another, so typed input keeps its order.
        self.queue = self.queue.then(function () {
            if (!self.id) {
                return self.post('/poll/start', message).then(function (r) {
                    if (r.status !== 'ok') {
                        self.deliver({type: 'compile_error', output: r.message || T.error});
                        self.finish();
                        return;
                    }
                    self.id = r.id;
                    self.pollLoop(0, 0);
                });
            }
            return self.post('/poll/' + self.id + '/send', message);
        }).catch(function () {
            if (!self.id) { self.onerror(); self.finish(); }
        });
    };

    TerminalSocket.prototype.pollLoop = function (since, failures) {
        var self = this;
        if (self.readyState !== 1) return;
        fetch(self.base + '/poll/' + self.id + '?since=' + since).then(function (r) {
            if (r.status === 404) return {messages: [], next: since, done: true};
            return r.json();
        }).then(function (r) {
            r.messages.forEach(function (m) { self.deliver(m); });
            if (r.done) self.finish();
            else self.pollLoop(r.next, 0);
        }).catch(function () {
            if (failures >= 5) { self.onerror(); self.finish(); return; }
            setTimeout(function () { self.pollLoop(since, failures + 1); }, 1000 * (failures + 1));
        });
    };

    TerminalSocket.prototype.close = function () {
        if (!this.polling) { if (this.socket) this.socket.close(); return; }
        if (this.id && this.readyState === 1) this.post('/poll/' + this.id + '/send', {type: 'kill'}).catch(function () {});
        this.finish();
    };

    /* ---- Result rendering ---- */

    // kotlinc cannot unpack its colour library into /tmp inside the sandbox and says so; the build is fine.
    // The runner drops this line too (runner_clean.py); this covers a runner that is not updated yet.
    function compileWarning(text) {
        return String(text || '').replace(/^[^\n]*jansi-[\w.-]*\.lck \(Permission denied\)\r?(?:\n|$)/gm, '');
    }

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
        var parts = [T.time + ' ' + result.time.toFixed(2) + ' ' + T.sec, T.memory + ' ' + Math.round(result.memory / 1024) + ' ' + T.mb];
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
            (passed ? '✓ ' : '✗ ') + T.sample + ' ' + (index + 1) + ': ' +
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
            '<div class="oe-modal" role="dialog" aria-label="' + T.editorSettings + '">' +
            '<div class="oe-modal-title">' + T.editorSettings + '<button type="button" class="oe-close" aria-label="' + T.close + '">×</button></div>' +
            row(T.theme, '<select name="theme"><option value="auto">' + T.themeAuto + '</option><option value="light">' + T.themeLight + '</option>' +
                '<option value="dark">' + T.themeDark + '</option><option value="contrast">' + T.themeContrast + '</option></select>') +
            row(T.fontSize, '<select name="fontSize">' + [12, 13, 14, 15, 16, 18, 20, 22, 24].map(function (n) {
                return '<option value="' + n + '">' + n + '</option>';
            }).join('') + '</select>') +
            row(T.indent, '<select name="tabSize">' + [2, 4, 8].map(function (n) {
                return '<option value="' + n + '">' + n + ' ' + T.spaces + '</option>';
            }).join('') + '</select>') +
            row(T.terminal, '<select name="terminal">' + ['light', 'dark', 'black', 'blue'].map(function (k) {
                return '<option value="' + k + '">' + T['term_' + k] + '</option>';
            }).join('') + '</select>') +
            check('wordWrap', T.wordWrap) +
            check('minimap', T.minimap) +
            check('suggestions', T.suggestions) +
            check('lineNumbers', T.lineNumbers) +
            check('ligatures', T.ligatures) +
            '<div class="oe-modal-foot"><button type="button" class="oe-btn oe-reset">' + T.reset + '</button>' +
            '<button type="button" class="oe-btn oe-primary oe-done">' + T.ok + '</button></div></div>';
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
                else if (input.name === 'theme' || input.name === 'terminal') s[input.name] = input.value;
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

    /* ---- Scratch: the program is a .sb3 project file, kept as base64 text ---- */

    var SCRATCH_EDITOR = 'https://scratch.mit.edu/projects/editor/';
    var MAX_PROJECT = 262144;   // base64 characters, about 190 KB of .sb3
    // "When the flag is clicked: say Hello, World!" (one empty costume each for the stage and the sprite).
    var SCRATCH_HELLO = 'UEsDBBQAAAAIAICLXl0Rbimd9AEAANcEAAAMAAAAcHJvamVjdC5qc29u3VPJbtswEP2VlGfBEFPbrXUrgnQBUvTgAG0RGMGIHMuEKY5AUopdw//eoZbU7SnIsRfpzdMsbxadRARfYQyieDgJE9YRKhRF9C1mwkHNWAxcJjrwBkqL7Hs6Z8KaEEdYegKt4I9tSe1HrKiu0U1fVOs9WzcUYpuS58mhx4OCsWQJaq89NZLLQggYv2hm5Wr7XuZyXi5W82WpV3KVX8tluVTvdDnPywU713qBh/gC31noKvbXEOEj+RpSzEB5ihANuRvWif6HKOS/3E/mzptMBGqdTroZd2T7hmTOLVk4ov/mNfq+w4h1Q6JYMuyMRrr34EIDPAh1FMVionnOMTVPTqSYQ7yndYOodnfgqrbfi2utPWcXi9qCDRebaryJKF+3KwHpQY0inXJhx70+Pu3QbS1Uyhq1R82Z3TDfkmHfQhxUZcK4pp2Sbg1aPeKwA01Pz1IjNXec205HdhDFnCdwTK8k5y8RlmgfHgMcnwsPtabKrPmisPh6u15/+HTLG5HZg+Ssn9Fayq6+k7f6jdhsXiqtJ86vvd6R+w+OV6bTDIYP6WJdw7b4GcyvKUgbjyoVEcUqmR6qCvqwcbaTiHU8JlaAtVfgkwaR1NTkTCQ/6uEpoAvsPdo1xv44A9ZdkiXezvJZns68ZiOfXfcG/xD9TYjz+TdQSwMEFAAAAAgAgIteXYnK8y5OAAAAVQAAACQAAAAxOWY4MTAxNGI1OTQ2YmQ5MTkwMjE2YjZjN2RiNDBiNS5zdmcdyssNgCAMANBVmg5gm3ozwMFZJJRExQihjO/n9g7P1Z5gHPtZPWpr10JkZpPNU7kTCTPTOxAsb009CoLGnLT97DnaWoZHBgYBweC+HR5QSwECFAMUAAAACACAi15dEW4pnfQBAADXBAAADAAAAAAAAAAAAAAAgAEAAAAAcHJvamVjdC5qc29uUEsBAhQDFAAAAAgAgIteXYnK8y5OAAAAVQAAACQAAAAAAAAAAAAAAIABHgIAADE5ZjgxMDE0YjU5NDZiZDkxOTAyMTZiNmM3ZGI0MGI1LnN2Z1BLBQYAAAAAAgACAIwAAACuAgAAAAA=';

    function readProject(file) {
        return new Promise(function (resolve, reject) {
            var reader = new FileReader();
            reader.onload = function () {
                var data = String(reader.result).split(',')[1] || '';
                if (data.slice(0, 4) !== 'UEsD') reject(new Error(T.scratchBad));  // a zip file starts with PK\3\4
                else if (data.length > MAX_PROJECT) reject(new Error(T.scratchTooBig));
                else resolve(data);
            };
            reader.onerror = function () { reject(new Error(T.scratchBad)); };
            reader.readAsDataURL(file);
        });
    }

    function projectBlob(data) {
        var bin = atob(data);
        var bytes = new Uint8Array(bin.length);
        for (var i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
        return new Blob([bytes], {type: 'application/x.scratch.sb3'});
    }

    function downloadProject(name, data) {
        var a = document.createElement('a');
        a.href = URL.createObjectURL(projectBlob(data));
        a.download = name;
        document.body.appendChild(a);
        a.click();
        setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 1000);
    }

    /* Shown instead of the code editor for a Scratch program. opts: {onLoad(data, fileName), onError(message)}.
     * show(data, name) displays a project; hide() brings the code editor back. */
    function ScratchPane(holder, opts) {
        var self = this;
        var el = this.el = document.createElement('div');
        el.className = 'oe-scratch';
        el.hidden = true;
        el.innerHTML =
            '<i class="fa fa-puzzle-piece oe-scratch-icon"></i>' +
            '<div class="oe-scratch-name"></div>' +
            '<div class="oe-scratch-actions">' +
            '<button type="button" class="oe-btn oe-primary oe-scratch-upload"><i class="fa fa-upload"></i> </button>' +
            '<button type="button" class="oe-btn oe-scratch-download"><i class="fa fa-download"></i> </button>' +
            '<a class="oe-btn" target="_blank" rel="noopener"><i class="fa fa-external-link"></i> </a>' +
            '</div><p class="oe-scratch-hint"></p><input type="file" accept=".sb3" hidden>';
        el.querySelector('.oe-scratch-upload').appendChild(document.createTextNode(T.scratchUpload));
        el.querySelector('.oe-scratch-download').appendChild(document.createTextNode(T.download));
        el.querySelector('a').href = SCRATCH_EDITOR;
        el.querySelector('a').appendChild(document.createTextNode(T.scratchEditor));
        el.querySelector('.oe-scratch-hint').textContent = T.scratchHint;
        var input = el.querySelector('input');
        el.querySelector('.oe-scratch-upload').addEventListener('click', function () { input.click(); });
        el.querySelector('.oe-scratch-download').addEventListener('click', function () {
            if (self.data) downloadProject(self.name, self.data);
        });
        input.addEventListener('change', function () {
            var file = input.files[0];
            input.value = '';
            if (!file) return;
            readProject(file).then(function (data) {
                self.show(data, self.name);
                if (opts.onLoad) opts.onLoad(data, file.name);
            }).catch(function (err) { if (opts.onError) opts.onError(err.message); else alert(err.message); });
        });
        holder.appendChild(el);
    }

    ScratchPane.prototype.show = function (data, name) {
        this.data = data || '';
        this.name = name || 'main.sb3';
        var size = Math.ceil(this.data.length * 3 / 4 / 1024);
        this.el.querySelector('.oe-scratch-name').textContent =
            this.data ? this.name + ' · ' + size + ' ' + T.kb : T.scratchEmpty;
        this.el.querySelector('.oe-scratch-download').disabled = !this.data;
        this.el.hidden = false;
        this.el.parentNode.classList.add('oe-scratch-on');
    };

    ScratchPane.prototype.hide = function () {
        this.el.hidden = true;
        this.el.parentNode.classList.remove('oe-scratch-on');
    };

    window.OlympEditor = {
        create: create,
        load: loadMonaco,
        Runner: Runner,
        TerminalSocket: TerminalSocket,
        renderResult: renderResult,
        renderSample: renderSample,
        openSettings: openSettings,
        terminalTheme: terminalTheme,
        monacoLanguage: monacoLanguage,
        escape: esc,
        compileWarning: compileWarning,
        ScratchPane: ScratchPane,
        readProject: readProject,
        downloadProject: downloadProject,
        SCRATCH_HELLO: SCRATCH_HELLO,
        MAX_PROJECT: MAX_PROJECT,
        T: T
    };
})(window, document);
