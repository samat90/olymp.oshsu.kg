/* Interactive console for the problem page: xterm.js + the runner's /session WebSocket.
 * The program prints into it and reads what the student types. */
(function (window) {
    'use strict';

    var E = window.OlympEditor;
    var S = E.T;

    function theme() { return E.terminalTheme(); }

    function Console(el, runner) {
        var self = this;
        this.runner = runner;
        this.session = null;
        this.onState = function () {};
        this.term = new window.Terminal({
            fontFamily: "'JetBrains Mono', Consolas, 'Courier New', monospace",
            fontSize: 14, convertEol: true, cursorBlink: true, scrollback: 5000, theme: theme()
        });
        this.fit = new window.FitAddon.FitAddon();
        this.term.loadAddon(this.fit);
        this.term.open(el);
        this.refit();
        window.addEventListener('resize', function () { self.refit(); });
        function paint() { el.style.background = el.parentNode.style.background = theme().background; }
        paint();
        document.addEventListener('olymp-terminal-theme', function () { self.term.options.theme = theme(); paint(); });
        this.term.onData(function (data) { self.input(data); });
    }

    Console.prototype.refit = function () {
        var fit = this.fit;
        setTimeout(function () { try { fit.fit(); } catch (e) { /* hidden */ } }, 0);
    };

    Console.prototype.print = function (text, style) {
        var codes = {dim: '\x1b[2m', red: '\x1b[31m', green: '\x1b[32m', yellow: '\x1b[33m'};
        text = String(text || '').replace(/\r?\n/g, '\r\n');
        this.term.write((style ? codes[style] : '') + text + (style ? '\x1b[0m' : ''));
    };

    Console.prototype.clear = function () { this.term.reset(); };

    Console.prototype.send = function (message) {
        var s = this.session;
        if (s && s.socket.readyState === 1) s.socket.send(JSON.stringify(message));
    };

    Console.prototype.input = function (data) {
        var s = this.session;
        if (!s || !s.running) return;
        for (var i = 0; i < data.length; i++) {
            var ch = data[i];
            if (ch === '\r' || ch === '\n') {
                this.term.write('\r\n');
                this.send({type: 'in', data: s.line + '\n'});
                s.line = '';
            } else if (ch === '\x7f' || ch === '\b') {
                if (s.line.length) {
                    s.line = Array.from(s.line).slice(0, -1).join('');
                    this.term.write('\b \b');
                }
            } else if (ch === '\x03') {
                this.term.write('^C\r\n');
                this.stop();
                return;
            } else if (ch === '\x04') {
                if (s.line) { this.send({type: 'in', data: s.line}); s.line = ''; }
                this.send({type: 'eof'});
            } else if (ch === '\x1b') {
                var m = /^\x1b\[[0-9;]*[A-Za-z~]/.exec(data.slice(i));
                if (m) i += m[0].length - 1;
            } else if (ch >= ' ' || ch === '\t') {
                s.line += ch;
                this.term.write(ch);
            }
        }
    };

    Console.prototype.running = function () { return !!(this.session && this.session.running); };

    Console.prototype.socketUrl = function () {
        var base = this.runner.url;
        if (/^https?:/.test(base)) return base.replace(/^http/, 'ws') + '/session';
        return location.origin.replace(/^http/, 'ws') + base + '/session';
    };

    Console.prototype.exit = function (m) {
        var verdicts = {TLE: m.wall ? S.tleWait : S.tle, MLE: S.mle, OLE: S.ole, RTE: S.rte};
        if (m.verdict && m.verdict !== 'OK' && !(m.verdict === 'RTE' && m.exit_code)) {
            this.print('\n...' + (verdicts[m.verdict] || m.verdict) + '\n', 'red');
        }
        this.print('\n...' + S.finished + ' ' + (m.exit_code || 0), m.exit_code ? 'red' : 'green');
        this.print(' (' + (m.time || 0).toFixed(2) + ' ' + S.sec + ', ' + Math.round((m.memory || 0) / 1024) + ' ' + S.mb + ')\n', 'dim');
    };

    /* Runs `source` with the console as its stdin/stdout. opts: {main, files, args}. */
    Console.prototype.run = function (language, source, opts) {
        var self = this;
        if (this.running()) return;
        opts = opts || {};
        this.clear();
        this.refit();
        this.onState(true);
        this.runner.getToken().then(function (token) {
            var socket = new WebSocket(self.socketUrl());
            var current = self.session = {socket: socket, line: '', running: true};
            var opened = false;
            socket.onopen = function () {
                opened = true;
                socket.send(JSON.stringify({token: token, language: language, source: source,
                                            main: opts.main, files: opts.files || {}, args: opts.args || []}));
            };
            socket.onmessage = function (event) {
                var m = JSON.parse(event.data);
                if (m.type === 'status') self.print((m.text === 'queued' ? S.queued : S.compiling) + '\n', 'dim');
                else if (m.type === 'compile_error') { self.print(S.compileError + '\n', 'red'); self.print(m.output); }
                else if (m.type === 'started') {
                    self.clear();
                    if (m.warning && m.warning.trim()) self.print(m.warning, 'yellow');
                    self.term.focus();
                } else if (m.type === 'out') self.term.write(m.data.replace(/\r?\n/g, '\r\n'));
                else if (m.type === 'err') self.print(m.data, 'red');
                else if (m.type === 'exit') self.exit(m);
            };
            socket.onerror = function () { if (opened) self.print('\n' + S.network + '\n', 'red'); };
            socket.onclose = function () {
                current.running = false;
                if (self.session === current) self.session = null;
                if (opened) self.onState(false);
                else self.runPlain(language, source, opts);
            };
        }).catch(function (err) {
            self.print('\n' + (err.message || S.network) + '\n', 'red');
            self.onState(false);
        });
    };

    /* Without a WebSocket (a proxy that does not pass it): one plain run with empty input. */
    Console.prototype.runPlain = function (language, source, opts) {
        var self = this;
        this.print(S.noTerminalPlain + '\n\n', 'yellow');
        this.runner.run(language, source, '', function () {
            self.print(S.queued + '\n', 'dim');
        }, {main: opts.main, files: opts.files || {}, args: opts.args || []}).then(function (r) {
            if (r.status === 'compile_error') { self.print(S.compileError + '\n', 'red'); self.print(r.compile_output); }
            else if (r.status !== 'ok') self.print((r.message || S.error) + '\n', 'red');
            else {
                self.term.write((r.stdout || '').replace(/\r?\n/g, '\r\n'));
                if (r.stderr) self.print(r.stderr, 'red');
                self.exit(r);
            }
        }).catch(function (err) {
            self.print('\n' + (err.message || S.network) + '\n', 'red');
        }).then(function () { self.onState(false); });
    };

    Console.prototype.stop = function () {
        var s = this.session;
        if (!s) return;
        this.send({type: 'kill'});
        setTimeout(function () { try { s.socket.close(); } catch (e) { /* ignore */ } }, 500);
    };

    window.OlympConsole = Console;
})(window);
