/* Quiz game client: player, solo player, host screen and host remote. HTTP polling only. */
(function () {
    'use strict';

    var C = window.QUIZ;
    var stage = document.getElementById('qz-stage');
    var screenEl = document.getElementById('qz-screen');
    if (!C || !stage || !screenEl) return;

    var U = C.urls;
    var ROLE = C.role;          // player | screen | remote
    var MODE = C.mode;          // screen | remote | auto | solo
    var IS_HOST = ROLE === 'screen' || ROLE === 'remote';
    var LETTERS = 'АБВГДЕ';

    // ------------------------------------------------------------ small helpers

    function h(tag, props) {
        var node = document.createElement(tag);
        if (props) {
            for (var key in props) {
                if (!props.hasOwnProperty(key)) continue;
                var v = props[key];
                if (v === null || v === undefined || v === false) continue;
                if (key === 'cls') node.className = v;
                else if (key === 'text') node.textContent = v;
                else if (key === 'html') node.innerHTML = v;
                else if (key === 'style') node.style.cssText = v;
                else if (key.slice(0, 2) === 'on') node.addEventListener(key.slice(2), v);
                else node.setAttribute(key, v === true ? '' : v);
            }
        }
        for (var i = 2; i < arguments.length; i++) add(node, arguments[i]);
        return node;
    }

    function add(node, child) {
        if (child === null || child === undefined || child === false) return;
        if (Array.isArray(child)) {
            for (var i = 0; i < child.length; i++) add(node, child[i]);
            return;
        }
        node.appendChild(typeof child === 'object' ? child : document.createTextNode(String(child)));
    }

    function byId(id) { return document.getElementById(id); }

    function show(node) {
        screenEl.innerHTML = '';
        screenEl.appendChild(node);
        screenEl.scrollTop = 0;
    }

    function cookie(name) {
        var m = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)'));
        return m ? decodeURIComponent(m[1]) : '';
    }

    function place(n) { return n + '-е'; }

    function plural(n, one, few, many) {
        var a = Math.abs(n) % 100, b = a % 10;
        if (a > 10 && a < 20) return many;
        if (b > 1 && b < 5) return few;
        if (b === 1) return one;
        return many;
    }

    function spacedPin(pin) { return pin.slice(0, 3) + ' ' + pin.slice(3); }

    var toastTimer = null;
    function toast(text) {
        var el = byId('qz-toast');
        if (!el) {
            el = h('div', {id: 'qz-toast', cls: 'qz-toast', role: 'status'});
            stage.appendChild(el);
        }
        el.textContent = text;
        el.classList.add('qz-on');
        clearTimeout(toastTimer);
        toastTimer = setTimeout(function () { el.classList.remove('qz-on'); }, 3000);
    }

    function wait(text) {
        return h('div', {cls: 'qz-center'}, h('div', {cls: 'qz-wait'}, h('i'), h('i'), h('i')),
            text ? h('p', {cls: 'qz-wait-text', text: text}) : null);
    }

    // ------------------------------------------------------------ effects (resources/quiz/fx.js, optional)

    function fx() { return window.QuizFx || null; }

    var GAME_SEED = (function (s) {
        var n = 0;
        for (var i = 0; i < s.length; i++) n = (n * 31 + s.charCodeAt(i)) % 9973;
        return n;
    })(String(C.pin || location.pathname));

    function shape(i) {
        var f = fx();
        if (f && f.shape) {
            try { return h('span', {cls: 'qz-shape-box', 'aria-hidden': 'true', html: f.shape(i)}); } catch (e) { /* fall through */ }
        }
        return h('span', {cls: 'qz-shape-box qz-shape-letter', 'aria-hidden': 'true', text: LETTERS.charAt(i)});
    }

    function countUp(el, from, to, ms) {
        var f = fx();
        if (f && f.countUp && !(f.reducedMotion && f.reducedMotion())) {
            try { f.countUp(el, from, to, ms || 900); return; } catch (e) { /* fall through */ }
        }
        el.textContent = String(to);
    }

    // Visuals in time with the drums: a flash on hits and a soft glow that pulses with the kick.
    function reduced() { var f = fx(); return !!(f && f.reducedMotion && f.reducedMotion()); }
    function beatFlash(k) {
        if (!stage || reduced()) return;
        stage.style.setProperty('--qz-hit', String(k || 1));
        stage.classList.remove('qz-hit');
        void stage.offsetWidth;
        stage.classList.add('qz-hit');
    }
    function beatGlow() {
        var a = window.QuizAudio, last = -1;
        if (!stage || !a || !a.beat || reduced()) return;
        (function frame() {
            var b = 0;
            try { b = a.beat(); } catch (e) { b = 0; }
            if (Math.abs(b - last) > 0.01) {
                last = b;
                stage.style.setProperty('--qz-beat', b.toFixed(3));
            }
            requestAnimationFrame(frame);
        })();
    }
    // Last five seconds: tick-tock per second, a hit when the time is up.
    function clockSound(ui, t) {
        var n = Math.ceil(t.left);
        if (n === ui.lastSec) return;
        ui.lastSec = n;
        if (n > 0 && n <= 5) sound.sfx('clock', n);
        else if (n <= 0 && t.total > 0) sound.sfx('timeup');
    }

    function confetti(ms) {
        var f = fx();
        if (f && f.confetti) try { f.confetti(ms || 4000); } catch (e) { /* ignore */ }
    }

    function flip(container, mutate) {
        var f = fx();
        if (f && f.flip) {
            try { f.flip(container, mutate); return; } catch (e) { /* fall through */ }
        }
        mutate();
    }

    function makeRing(container) {
        container.innerHTML = '';
        var f = fx();
        if (f && f.ring) {
            try {
                var r = f.ring(container);
                if (r && r.set) return r;
            } catch (e) { /* fall through */ }
        }
        container.innerHTML = '<svg viewBox="0 0 44 44" class="qz-ring-svg"><circle cx="22" cy="22" r="19" class="qz-ring-bg"/>' +
            '<circle cx="22" cy="22" r="19" class="qz-ring-fg" pathLength="100" stroke-dasharray="100" stroke-dashoffset="0"/></svg>' +
            '<b class="qz-ring-num"></b>';
        var fg = container.querySelector('.qz-ring-fg'), num = container.querySelector('.qz-ring-num');
        return {
            set: function (fraction, seconds) {
                fg.setAttribute('stroke-dashoffset', String(100 - 100 * Math.max(0, Math.min(1, fraction))));
                num.textContent = String(seconds);
                container.classList.toggle('qz-ring-late', seconds <= 5);
            }
        };
    }

    // ------------------------------------------------------------ sound (resources/quiz/audio.js, optional)

    var sound = {
        want: null, opts: null, unlocked: false,
        api: function () { return window.QuizAudio || null; },
        call: function (method, arg, arg2) {
            var a = this.api();
            if (a && a[method]) {
                try { return a[method](arg, arg2); } catch (e) { /* ignore */ }
            }
            return undefined;
        },
        musicAllowed: function () {
            if (C.music === false) return false;
            // The host's device plays the music; phones of players only in games without a host.
            if (IS_HOST) return true;
            return MODE === 'auto' || MODE === 'solo';
        },
        // variant: the question number, so every question gets a different tune
        music: function (name, variant) {
            if (!this.musicAllowed()) name = null;
            var opts = ROLE === 'player' ? {quiet: true} : {};
            // Each game starts at its own place in the list, so the same quiz sounds different next time.
            if (typeof variant === 'number') opts.variant = variant + (name === 'question' ? GAME_SEED : 0);
            var want = name ? name + ':' + (typeof variant === 'number' ? variant : '') : null;
            if (want === this.want) return;
            this.want = want;
            this.call('music', name, opts);
        },
        urgent: function (on) { this.call('urgent', on); },
        sfx: function (name, arg) { this.call('sfx', name, arg); },
        vibrate: function (pattern) {
            var a = this.api();
            if (a && a.vibrate) this.call('vibrate', pattern);
            else if (navigator.vibrate) try { navigator.vibrate(pattern); } catch (e) { /* ignore */ }
        },
        muted: function () { return !!this.call('isMuted'); },
        toggle: function () {
            this.unlock();
            this.call('setMuted', !this.muted());
            updateSoundButtons();
        },
        unlock: function () {
            if (this.unlocked) return;
            this.unlocked = true;
            this.call('unlock');
        }
    };

    function updateSoundButtons() {
        var off = sound.muted();
        var buttons = document.querySelectorAll('#qz-sound i, [data-act="sound"] i');
        for (var i = 0; i < buttons.length; i++) buttons[i].className = off ? 'fa fa-volume-off' : 'fa fa-volume-up';
    }

    document.addEventListener('pointerdown', function () { sound.unlock(); }, true);
    document.addEventListener('keydown', function () { sound.unlock(); }, true);

    // ------------------------------------------------------------ network

    var clock = {offset: 0, rtt: 1e9, samples: 0};

    function syncClock(serverNow, t0, t1) {
        if (typeof serverNow !== 'number') return;
        var rtt = (t1 - t0) / 1000;
        clock.samples++;
        if (rtt <= clock.rtt * 1.3 + 0.03 || clock.samples % 20 === 0) {
            clock.rtt = rtt;
            clock.offset = serverNow - (t0 + t1) / 2000;
        }
    }

    function serverNow() { return Date.now() / 1000 + clock.offset; }

    function request(method, url, body, asForm) {
        var opts = {method: method, credentials: 'same-origin', cache: 'no-store', headers: {}};
        if (method === 'POST') {
            opts.headers['X-CSRFToken'] = cookie('csrftoken');
            if (asForm) {
                opts.body = new URLSearchParams(body || {});
            } else {
                opts.headers['Content-Type'] = 'application/json';
                opts.body = JSON.stringify(body || {});
            }
        }
        return fetch(url, opts).then(function (r) {
            return r.json().then(function (d) { return {status: r.status, data: d || {}}; },
                function () { return {status: r.status, data: {}}; });
        });
    }

    function setOffline(on) {
        var el = byId('qz-net');
        if (el) el.hidden = !on;
    }

    // One request at a time; the server says how often to ask; back off on errors.
    function Poller(buildUrl, onData, onGone, fixed) {
        var self = {interval: fixed || 1000, fails: 0, busy: false, stopped: false, again: false, timer: null};

        function schedule(ms) {
            clearTimeout(self.timer);
            if (!self.stopped) self.timer = setTimeout(run, ms);
        }

        function failed() {
            self.busy = false;
            self.fails++;
            if (self.fails >= 2) setOffline(true);
            schedule(Math.min(1000 * Math.pow(1.7, self.fails), 10000));
        }

        function run() {
            if (self.busy || self.stopped) return;
            self.busy = true;
            var t0 = Date.now();
            fetch(buildUrl(), {credentials: 'same-origin', cache: 'no-store'}).then(function (r) {
                return r.json().then(function (d) { return {status: r.status, data: d}; },
                    function () { return {status: r.status, data: null}; });
            }).then(function (res) {
                if (res.status === 404 && res.data && res.data.gone) {
                    self.busy = false;
                    self.stopped = true;
                    setOffline(false);
                    onGone();
                    return;
                }
                if (res.status !== 200 || !res.data) {
                    failed();
                    return;
                }
                self.busy = false;
                self.fails = 0;
                setOffline(false);
                syncClock(res.data.now, t0, Date.now());
                if (res.data.poll && !fixed) self.interval = res.data.poll;
                onData(res.data);
                if (self.again) {
                    self.again = false;
                    schedule(0);
                } else {
                    schedule(document.hidden ? Math.max(self.interval, 4000) : self.interval);
                }
            }).catch(failed);
        }

        self.now = function () {
            if (self.stopped) return;
            if (self.busy) self.again = true;
            else schedule(0);
        };
        self.stop = function () {
            self.stopped = true;
            clearTimeout(self.timer);
        };
        self.start = function () { schedule(0); };
        document.addEventListener('visibilitychange', function () {
            if (!document.hidden) self.now();
        });
        return self;
    }

    function keepAwake() {
        if (!navigator.wakeLock || !navigator.wakeLock.request) return;
        function ask() {
            if (document.visibilityState === 'visible') navigator.wakeLock.request('screen').catch(function () {});
        }
        ask();
        document.addEventListener('visibilitychange', ask);
    }

    // ------------------------------------------------------------ math (MathJax on demand, like problem pages)

    var mathLoading = null;

    function typeset(node) {
        if (!node || !/\$|\\\(|\\\[|~/.test(node.textContent)) return;
        if (!mathLoading) {
            mathLoading = new Promise(function (resolve, reject) {
                if (window.MathJax && window.MathJax.typesetPromise) {
                    resolve();
                    return;
                }
                window.MathJax = {
                    tex: {inlineMath: [['$', '$'], ['~', '~'], ['\\(', '\\)']]},
                    options: {enableMenu: false},
                    startup: {
                        typeset: false,
                        ready: function () {
                            window.MathJax.startup.defaultReady();
                            window.MathJax.startup.promise.then(resolve);
                        }
                    }
                };
                var s = document.createElement('script');
                s.src = 'https://cdnjs.cloudflare.com/ajax/libs/mathjax/3.2.0/es5/tex-chtml.min.js';
                s.async = true;
                s.onerror = reject;
                document.head.appendChild(s);
            });
        }
        mathLoading.then(function () {
            if (document.body.contains(node)) window.MathJax.typesetPromise([node]).catch(function () {});
        }, function () {});
    }

    // ------------------------------------------------------------ question parts shared by every role

    function isChoice(q) {
        return q.type === 'single' || q.type === 'truefalse' || q.type === 'poll' || q.type === 'multi' ||
            (q.type === 'code' && !q.input);
    }

    function optionIndex(q, id) {
        for (var i = 0; i < q.options.length; i++) if (q.options[i].id === id) return i;
        return -1;
    }

    function optionLabel(q, id) {
        var i = optionIndex(q, id);
        if (i < 0) return '?';
        return q.options[i].text || 'картинка ' + (i + 1);
    }

    function questionHead(q, big) {
        var badges = [h('span', {cls: 'qz-q-type', text: q.type_name})];
        if (q.weight === 2) badges.push(h('span', {cls: 'qz-badge qz-badge-x2', text: 'x2'}));
        if (!q.scored) badges.push(h('span', {cls: 'qz-badge', text: 'без очков'}));
        var text = q.text ? h('div', {cls: 'qz-q-text', html: q.text}) : null;
        var box = h('div', {cls: 'qz-q-head' + (big ? ' qz-big' : '')},
            h('div', {cls: 'qz-q-badges'}, badges),
            text,
            q.code ? h('pre', {cls: 'qz-code', 'data-lang': q.lang || ''}, h('code', {text: q.code})) : null,
            q.image && q.type !== 'pin' ? h('div', {cls: 'qz-q-img'}, h('img', {src: q.image, alt: ''})) : null);
        if (text) setTimeout(function () { typeset(text); }, 0);
        return box;
    }

    function optionContent(q, o, i, colour) {
        var mark = shape(i);
        if (colour) mark.classList.add('qz-c' + i);
        return [mark,
            h('span', {cls: 'qz-opt-body'},
                o.image ? h('img', {src: o.image, alt: '', cls: 'qz-opt-img'}) : null,
                o.text ? h('span', {cls: 'qz-opt-text', text: o.text}) : null)];
    }

    function longOptions(q) {
        for (var i = 0; i < q.options.length; i++) {
            if ((q.options[i].text || '').length > 32 || q.options[i].image) return true;
        }
        return q.options.length > 4;
    }

    // The statistics after a question: bars, histogram, points on the image, word cloud...
    function revealView(q, rv, opts) {
        opts = opts || {};
        var t = rv.type, box = h('div', {cls: 'qz-viz'});
        if (rv.counts && q && q.options.length) {
            var max = 1, total = 0, correct = rv.correct || [];
            q.options.forEach(function (o) {
                var c = rv.counts[String(o.id)] || 0;
                max = Math.max(max, c);
                total += c;
            });
            var bars = h('div', {cls: 'qz-sbars' + (q.options.length > 4 ? ' qz-sbars-many' : '')});
            q.options.forEach(function (o, i) {
                var c = rv.counts[String(o.id)] || 0;
                var ok = correct.indexOf(o.id) >= 0;
                var mine = opts.mine && (opts.mine === o.id || (Array.isArray(opts.mine) && opts.mine.indexOf(o.id) >= 0));
                var bar = h('div', {cls: 'qz-sbar' + (ok ? ' qz-right' : (t !== 'poll' ? ' qz-dim' : '')) +
                        (mine ? ' qz-mine' : ''), style: '--p:0'},
                    h('span', {cls: 'qz-sbar-track'}, h('span', {cls: 'qz-sbar-fill qz-c' + i}),
                        h('b', {cls: 'qz-sbar-n', text: String(c)})),
                    h('span', {cls: 'qz-sbar-label'}, optionContent(q, o, i, true),
                        mine ? h('span', {cls: 'qz-mine-tag', text: 'вы'}) : null,
                        ok ? h('i', {cls: 'fa fa-check qz-tick', 'aria-label': 'верно'}) : null));
                bars.appendChild(bar);
                grow(bar, c / max);
            });
            box.appendChild(bars);
        } else if (t === 'order' && q) {
            box.appendChild(h('ol', {cls: 'qz-order-key'}, (rv.correct || []).map(function (id) {
                var i = optionIndex(q, id);
                return h('li', {cls: 'qz-c' + Math.max(i, 0)}, i >= 0 ? optionContent(q, q.options[i], i) : '?');
            })));
        } else if (t === 'word') {
            box.appendChild(h('div', {cls: 'qz-tiles qz-tiles-key'}, String(rv.correct || '').split('').map(function (ch) {
                return h('span', {cls: 'qz-tile', text: ch});
            })));
        } else if (t === 'text' || t === 'code') {
            box.appendChild(h('div', {cls: 'qz-key-text'}, h('span', {cls: 'qz-muted', text: 'Правильный ответ: '}),
                h('b', {text: (rv.correct || []).join(' / ') || '—'})));
            if (rv.top && rv.top.length) {
                var accepted = (rv.correct || []).map(function (a) { return String(a).trim().toLowerCase().replace(/ё/g, 'е'); });
                var topMax = rv.top[0][1] || 1;
                var list = h('div', {cls: 'qz-sbars qz-sbars-text'});
                rv.top.forEach(function (row) {
                    var ok = accepted.indexOf(String(row[0])) >= 0;
                    var bar = h('div', {cls: 'qz-sbar' + (ok ? ' qz-right' : ' qz-dim'), style: '--p:0'},
                        h('span', {cls: 'qz-sbar-track'}, h('span', {cls: 'qz-sbar-fill ' + (ok ? 'qz-c0' : 'qz-c5')}), h('b', {cls: 'qz-sbar-n', text: String(row[1])})),
                        h('span', {cls: 'qz-sbar-label'}, h('span', {cls: 'qz-opt-text', text: row[0]}),
                            ok ? h('i', {cls: 'fa fa-check qz-tick'}) : null));
                    list.appendChild(bar);
                    grow(bar, row[1] / topMax);
                });
                box.appendChild(list);
            }
        } else if (t === 'slider') {
            box.appendChild(histogram(q, rv, opts.mine));
        } else if (t === 'pin') {
            box.appendChild(pinView(q, rv, opts.mine));
        } else if (t === 'cloud') {
            box.appendChild(cloudView(rv.words || []));
        } else if (t === 'open') {
            box.appendChild(openView(rv.texts || [], opts.hideable));
        }
        return box;
    }

    function grow(bar, fraction) {
        requestAnimationFrame(function () {
            requestAnimationFrame(function () { bar.style.setProperty('--p', String(fraction)); });
        });
    }

    function histogram(q, rv, mine) {
        var s = (q && q.slider) || {min: 0, max: 100, unit: ''};
        var lo = Number(s.min), hi = Number(s.max), bins = 12, counts = [], max = 1;
        if (!(hi > lo)) hi = lo + 1;
        for (var i = 0; i < bins; i++) counts.push(0);
        (rv.values || []).forEach(function (v) {
            var b = Math.min(bins - 1, Math.max(0, Math.floor((v - lo) / (hi - lo) * bins)));
            counts[b]++;
        });
        counts.forEach(function (c) { max = Math.max(max, c); });
        var tol = Number(rv.tolerance || 0), ans = Number(rv.correct);
        var cols = h('div', {cls: 'qz-hist'});
        counts.forEach(function (c, b) {
            var a = lo + (hi - lo) * b / bins, z = lo + (hi - lo) * (b + 1) / bins;
            var hit = z >= ans - tol && a <= ans + tol;
            var col = h('div', {cls: 'qz-hist-col' + (hit ? ' qz-right' : ''), style: '--p:0',
                title: Math.round(a) + '–' + Math.round(z) + ': ' + c}, h('span', {cls: 'qz-hist-fill'}),
                c ? h('b', {text: String(c)}) : null);
            cols.appendChild(col);
            grow(col, c / max);
        });
        var pos = (ans - lo) / (hi - lo) * 100;
        cols.appendChild(h('span', {cls: 'qz-hist-mark', style: 'left:' + Math.max(0, Math.min(100, pos)) + '%'}));
        if (typeof mine === 'number') {
            cols.appendChild(h('span', {cls: 'qz-hist-mine', style: 'left:' + Math.max(0, Math.min(100, (mine - lo) / (hi - lo) * 100)) + '%',
                title: 'Ваш ответ'}));
        }
        return h('div', {cls: 'qz-hist-box'}, cols,
            h('div', {cls: 'qz-hist-axis'}, h('span', {text: String(lo)}), h('span', {text: String(hi)})),
            h('div', {cls: 'qz-key-text'}, h('span', {cls: 'qz-muted', text: 'Правильно: '}),
                h('b', {text: rv.correct + (s.unit ? ' ' + s.unit : '') + (tol ? ' ± ' + tol : '')}),
                typeof mine === 'number' ? h('span', {cls: 'qz-muted', text: ' · ваш ответ ' + mine}) : null));
    }

    function pinView(q, rv, mine) {
        var wrap = h('div', {cls: 'qz-pin-wrap qz-pin-result'}, h('img', {src: (q && q.image) || '', alt: ''}));
        var c = rv.correct || {x: 50, y: 50, r: 10};
        wrap.appendChild(h('span', {cls: 'qz-pin-target', style: 'left:' + c.x + '%;top:' + c.y + '%;width:' + (2 * c.r) +
                '%;height:' + (2 * c.r) + '%'}));
        (rv.points || []).forEach(function (p, i) {
            wrap.appendChild(h('span', {cls: 'qz-pin-dot', style: 'left:' + p.x + '%;top:' + p.y + '%;animation-delay:' +
                    Math.min(i * 15, 1200) + 'ms'}));
        });
        if (mine && typeof mine === 'object') {
            wrap.appendChild(h('span', {cls: 'qz-pin-marker qz-pin-mine', style: 'left:' + mine.x + '%;top:' + mine.y + '%'}));
        }
        return wrap;
    }

    function cloudView(words) {
        var box = h('div', {cls: 'qz-cloud'});
        if (!words.length) {
            box.appendChild(h('p', {cls: 'qz-muted', text: 'Слов пока нет'}));
            return box;
        }
        var max = words[0][1] || 1;
        // Biggest words in the middle, the rest alternate around them.
        var ordered = [];
        words.forEach(function (w, i) {
            if (i % 2) ordered.push(w);
            else ordered.unshift(w);
        });
        ordered.forEach(function (w) {
            var k = w[1] / max;
            box.appendChild(h('span', {cls: 'qz-cloud-word qz-c' + (w[0].length % 6), title: String(w[1]),
                style: 'font-size:' + (0.9 + 2.6 * k).toFixed(2) + 'em;opacity:' + (0.6 + 0.4 * k).toFixed(2), text: w[0]}));
        });
        return box;
    }

    var hiddenTexts = {};

    function openView(texts, hideable) {
        var box = h('div', {cls: 'qz-open-list'});
        if (!texts.length) box.appendChild(h('p', {cls: 'qz-muted', text: 'Ответов нет'}));
        texts.forEach(function (row, i) {
            var card = h('div', {cls: 'qz-open-card qz-pop' + (hiddenTexts[row.id] ? ' qz-hidden-text' : ''),
                style: 'animation-delay:' + Math.min(i * 60, 1500) + 'ms'}, h('span', {text: row.text}));
            if (hideable) {
                card.appendChild(h('button', {type: 'button', cls: 'qz-open-hide', title: 'Скрыть ответ',
                    onclick: function () {
                        hiddenTexts[row.id] = !hiddenTexts[row.id];
                        card.classList.toggle('qz-hidden-text', hiddenTexts[row.id]);
                        this.textContent = hiddenTexts[row.id] ? 'показать' : 'скрыть';
                    }, text: hiddenTexts[row.id] ? 'показать' : 'скрыть'}));
            }
            box.appendChild(card);
        });
        return box;
    }

    function revealSummary(rv) {
        if (rv.type === 'poll' || rv.type === 'cloud' || rv.type === 'open') {
            return h('p', {cls: 'qz-summary', text: 'Ответили: ' + rv.answered + ' из ' + rv.players});
        }
        return h('p', {cls: 'qz-summary'}, 'Верно: ', h('b', {text: String(rv.correct_count)}), ' из ' + rv.players,
            rv.answered < rv.players ? h('span', {cls: 'qz-muted', text: ' · не ответили ' + (rv.players - rv.answered)}) : null);
    }

    function explanation(rv) {
        if (!rv.explanation) return null;
        var el = h('div', {cls: 'qz-explain'}, h('b', {text: 'Пояснение'}), h('div', {html: rv.explanation}));
        setTimeout(function () { typeset(el); }, 0);
        return el;
    }

    function leaderRows(top, me, limit) {
        var list = h('ol', {cls: 'qz-board'});
        top.slice(0, limit || 5).forEach(function (row) {
            list.appendChild(h('li', {cls: 'qz-board-row' + (me && row.id === me ? ' qz-me' : ''), 'data-key': String(row.id)},
                h('span', {cls: 'qz-board-place', text: String(row.rank)}),
                h('span', {cls: 'qz-board-nick', text: row.nick || row.nickname}),
                row.streak >= 2 ? h('span', {cls: 'qz-streak', text: '🔥 ' + row.streak}) : null,
                h('b', {cls: 'qz-board-score', text: String(row.score)})));
        });
        return list;
    }

    function podium(top, me) {
        var box = h('div', {cls: 'qz-podium'});
        [1, 0, 2].forEach(function (k, n) {
            var row = top[k];
            if (!row) {
                box.appendChild(h('div', {cls: 'qz-pod qz-pod-empty qz-pod-' + (k + 1)}));
                return;
            }
            box.appendChild(h('div', {cls: 'qz-pod qz-pod-' + (k + 1) + (me && row.id === me ? ' qz-me' : ''),
                    style: 'animation-delay:' + [2000, 3300, 1000][n] + 'ms'},
                h('span', {cls: 'qz-pod-nick', text: row.nickname || row.nick}),
                h('span', {cls: 'qz-pod-score', text: String(row.score)}),
                h('span', {cls: 'qz-pod-block'}, h('b', {text: String(k + 1)}))));
        });
        return box;
    }

    // ------------------------------------------------------------ the timer shared by every role

    var game = {st: null};
    var tickHandlers = [];

    function timing() {
        var st = game.st;
        if (!st || st.ph !== 'question') return null;
        var now = st.paused ? st.paused.at : serverNow();
        return {now: now, toStart: st.start - now, left: Math.max(0, st.end - now),
            total: Math.max(1, st.end - st.start)};
    }

    setInterval(function () {
        for (var i = 0; i < tickHandlers.length; i++) tickHandlers[i](timing());
    }, 100);

    function setPaused(on) {
        var el = byId('qz-pause');
        if (!el) {
            el = h('div', {id: 'qz-pause', cls: 'qz-pause', hidden: true}, h('div', {}, h('i', {cls: 'fa fa-pause'}), h('b', {text: 'Пауза'})));
            stage.appendChild(el);
        }
        el.hidden = !on;
        stage.classList.toggle('qz-paused', !!on);
    }

    function countdownEl() {
        return h('div', {cls: 'qz-countdown', hidden: true}, h('b'));
    }

    // Shows 3-2-1 before the answers open; returns true while counting.
    function runCountdown(view, t, withSound) {
        var el = view.querySelector('.qz-countdown');
        if (!el) return false;
        if (t && t.toStart > 0) {
            var n = Math.ceil(t.toStart);
            el.hidden = false;
            if (el.getAttribute('data-n') !== String(n)) {
                el.setAttribute('data-n', String(n));
                var b = el.querySelector('b');
                b.textContent = String(n);
                b.classList.remove('qz-count');
                void b.offsetWidth;
                b.classList.add('qz-count');
                if (withSound) {
                    // The first question of the game opens with a big drum hit, then a drum per number.
                    var first = game.st && game.st.i === 0 && el.getAttribute('data-gong') !== '1';
                    if (first) el.setAttribute('data-gong', '1');
                    sound.sfx(first ? 'start' : 'count', n);
                }
                beatFlash(first ? 1 : 0.6);
            }
            return true;
        }
        if (!el.hidden) {
            el.hidden = true;
            if (withSound) sound.sfx('go');
            beatFlash(1);
        }
        return false;
    }

    function setQnum(st) {
        var el = byId('qz-qnum');
        if (el) el.textContent = st && st.i >= 0 && st.ph !== 'finished' ? 'Вопрос ' + (st.i + 1) + ' из ' + st.n : '';
    }

    // ============================================================ player (and solo)

    function startPlayer() {
        var P = {q: null, qFor: -1, loadingQ: -1, res: null, resFor: -1, loadingR: -1, fin: null, loadingF: false,
            answered: false, sending: false, mine: null, view: '', score: null, timeUp: false, effectsFor: -1,
            ui: null};
        var ringBox = byId('qz-ring');
        var ring = ringBox ? makeRing(ringBox) : null;
        var poller = Poller(function () { return U.state + '?v=' + (game.st ? game.st.v : 0); }, onState, gone);

        var soundBtn = byId('qz-sound');
        if (soundBtn) soundBtn.addEventListener('click', function () { sound.toggle(); });
        updateSoundButtons();
        keepAwake();

        function gone() {
            sound.music(null);
            P.view = 'gone';
            show(h('div', {cls: 'qz-center qz-msg'}, h('i', {cls: 'fa fa-flag-checkered qz-msg-icon'}),
                h('h2', {text: 'Игра закончилась'}), h('a', {cls: 'qz-btn qz-btn-primary', href: U.join, text: 'Войти в другую игру'})));
        }

        function onState(d) {
            if (d.kicked) {
                poller.stop();
                sound.music(null);
                P.view = 'kicked';
                show(h('div', {cls: 'qz-center qz-msg'}, h('i', {cls: 'fa fa-user-times qz-msg-icon'}),
                    h('h2', {text: 'Ведущий удалил вас из игры'}),
                    h('a', {cls: 'qz-btn qz-btn-primary', href: U.join, text: 'Войти снова'})));
                return;
            }
            if (!d.v) return;
            applyState(d);
        }

        function applyState(d) {
            var prev = game.st;
            game.st = d;
            if (prev && prev.i !== d.i) {
                P.answered = false;
                P.mine = null;
                P.timeUp = false;
            }
            setPaused(!!d.paused);
            setQnum(d);
            var ph = d.ph;
            // A new phase usually arrives with its data; the separate requests are only a fallback.
            if (d.question && d.question.i === d.i) {
                P.q = d.question;
                P.qFor = d.i;
                if (d.question.answered) P.answered = true;
            }
            if (d.result && d.result.reveal && d.result.reveal.i === d.i) {
                P.res = d.result;
                P.resFor = d.i;
                if (d.result.me) setScore(d.result.me.score);
            }
            if (d.final && !P.fin) {
                P.fin = d.final;
                if (d.final.me) setScore(d.final.me.score);
            }
            if ((ph === 'question' || ph === 'reveal' || ph === 'leaderboard') && P.qFor !== d.i) loadQuestion(d.i);
            if ((ph === 'reveal' || ph === 'leaderboard') && P.resFor !== d.i) loadResult(d.i);
            if (ph === 'finished' && !P.fin) loadFinal();
            render();
        }

        function loadQuestion(i) {
            if (P.loadingQ === i) return;
            P.loadingQ = i;
            request('GET', U.question).then(function (r) {
                P.loadingQ = -1;
                if (r.status !== 200) {
                    if (game.st && game.st.i === i && r.status >= 500) setTimeout(function () { loadQuestion(i); }, 1500);
                    return;
                }
                if (!game.st || r.data.i !== game.st.i) return;
                P.q = r.data;
                P.qFor = r.data.i;
                if (r.data.answered) P.answered = true;
                render();
            }, function () {
                P.loadingQ = -1;
                setTimeout(function () { if (game.st && game.st.i === i && P.qFor !== i) loadQuestion(i); }, 1500);
            });
        }

        function loadResult(i) {
            if (P.loadingR === i) return;
            P.loadingR = i;
            request('GET', U.result).then(function (r) {
                P.loadingR = -1;
                if (r.status !== 200 || !r.data.reveal) {
                    setTimeout(function () { if (game.st && game.st.i === i && P.resFor !== i) loadResult(i); }, 1200);
                    return;
                }
                if (!game.st || r.data.reveal.i !== game.st.i) return;
                P.res = r.data;
                P.resFor = i;
                if (r.data.me) setScore(r.data.me.score);
                render();
            }, function () {
                P.loadingR = -1;
                setTimeout(function () { if (game.st && game.st.i === i && P.resFor !== i) loadResult(i); }, 1500);
            });
        }

        function loadFinal() {
            if (P.loadingF) return;
            P.loadingF = true;
            request('GET', U.final).then(function (r) {
                P.loadingF = false;
                if (r.status !== 200) {
                    setTimeout(loadFinal, 1500);
                    return;
                }
                P.fin = r.data;
                if (r.data.me) setScore(r.data.me.score);
                render();
            }, function () {
                P.loadingF = false;
                setTimeout(loadFinal, 1500);
            });
        }

        function setScore(score) {
            var el = byId('qz-score');
            if (!el || typeof score !== 'number') return;
            el.hidden = false;
            if (P.score === null) {
                el.textContent = String(score);
            } else if (score !== P.score) {
                countUp(el, P.score, score, 900);
            }
            P.score = score;
        }

        function render() {
            var st = game.st;
            if (!st) return;
            var key;
            if (st.ph === 'lobby') key = 'lobby';
            else if (st.ph === 'question') key = P.q && P.qFor === st.i ? (P.answered ? 'qa' : 'q') + st.i : 'wait';
            else if (st.ph === 'reveal') key = P.res && P.resFor === st.i && P.q && P.qFor === st.i ? 'r' + st.i : 'wait';
            else if (st.ph === 'leaderboard') key = P.res && P.resFor === st.i ? 'b' + st.i : 'wait';
            else if (st.ph === 'finished') key = P.fin ? 'fin' : 'wait';
            else key = 'wait';
            if (ringBox) ringBox.hidden = st.ph !== 'question';
            if (key === P.view) return;
            P.view = key;
            P.ui = null;
            if (key === 'lobby') return showLobby();
            if (key === 'wait') {
                show(wait(st.ph === 'question' ? '' : 'Подсчёт…'));
                return;
            }
            if (key.charAt(0) === 'q' && key.charAt(1) === 'a') return showAnswered();
            if (key.charAt(0) === 'q') return showQuestion();
            if (key.charAt(0) === 'r') return showReveal();
            if (key.charAt(0) === 'b') return showBoard();
            if (key === 'fin') return showFinal();
        }

        function showLobby() {
            sound.music('lobby');
            var box = h('div', {cls: 'qz-center qz-lobby-me'},
                h('div', {cls: 'qz-me-badge qz-pop'}, h('i', {cls: 'fa fa-check'})),
                h('h2', {text: MODE === 'solo' ? C.title : 'Вы в игре!'}),
                h('p', {cls: 'qz-me-nick', text: C.nickname}));
            if (MODE === 'solo') {
                box.appendChild(h('button', {type: 'button', cls: 'qz-btn qz-btn-primary qz-btn-xl', text: 'Начать',
                    onclick: function () { soloNext(this); }}));
            } else {
                box.appendChild(h('div', {cls: 'qz-wait'}, h('i'), h('i'), h('i')));
                box.appendChild(h('p', {cls: 'qz-wait-text', text: 'Ждём начала игры. Смотрите на экран ведущего.'}));
            }
            show(box);
        }

        function soloNext(btn) {
            if (btn) btn.disabled = true;
            request('POST', U.next, {}).then(function (r) {
                if (r.status === 200 && r.data.v) applyState(r.data);
                else {
                    if (btn) btn.disabled = false;
                    toast(r.data.error || 'Не получилось');
                }
                poller.now();
            }, function () {
                if (btn) btn.disabled = false;
                toast('Нет связи');
            });
        }

        // ---------------- answering

        function showQuestion() {
            var q = P.q;
            sound.music(null);
            var answer = h('div', {cls: 'qz-answer qz-locked'});
            var view = h('div', {cls: 'qz-q qz-enter'}, questionHead(q, false), answer, countdownEl(),
                h('div', {cls: 'qz-timeup', hidden: true}, h('i', {cls: 'fa fa-clock-o'}), ' Время вышло'));
            P.ui = {view: view, answer: answer, opened: false};
            buildAnswer(q, answer);
            show(view);
            playerTick(timing());
        }

        function playerTick(t) {
            var st = game.st;
            if (ring && t) ring.set(t.toStart > 0 ? 1 : t.left / t.total, Math.ceil(t.toStart > 0 ? t.total : t.left));
            if (!t || !P.ui) return;
            var counting = runCountdown(P.ui.view, t, MODE !== 'screen');
            if (!counting && !P.ui.opened) {
                P.ui.opened = true;
                P.ui.answer.classList.remove('qz-locked');
                if (st.ph === 'question') sound.music('question', st.i);
                var first = P.ui.answer.querySelector('input:not([type=range]), textarea');
                if (first && !('ontouchstart' in window)) first.focus();
            }
            if (P.ui.opened && st.ph === 'question') {
                sound.urgent(t.left <= 5 && t.left > 0);
                if (sound.musicAllowed() && !P.answered && !st.paused) clockSound(P.ui, t);
            }
            if (P.ui.opened && t.left <= 0 && !P.answered && !P.timeUp && !st.paused) {
                P.timeUp = true;
                sound.urgent(false);
                sound.music(null);
                P.ui.answer.classList.add('qz-locked');
                var tu = P.ui.view.querySelector('.qz-timeup');
                if (tu) tu.hidden = false;
                setTimeout(function () { poller.now(); }, 700);
            }
        }
        tickHandlers.push(function (t) { if (!IS_HOST) playerTick(t); });

        function submit(value) {
            if (P.sending || P.answered || P.timeUp || !P.q) return;
            P.sending = true;
            if (P.ui) P.ui.answer.classList.add('qz-sending');
            request('POST', U.answer, {i: P.q.i, value: value}).then(function (r) {
                P.sending = false;
                if (P.ui) P.ui.answer.classList.remove('qz-sending');
                var already = r.status === 409 && /уже принят/i.test(r.data.error || '');
                if (r.status === 200 || already) {
                    P.answered = true;
                    P.mine = value;
                    sound.sfx('answer');
                    sound.vibrate(30);
                    render();
                    poller.now();
                } else {
                    toast(r.data.error || 'Ответ не принят');
                    if (r.status === 409) poller.now();
                }
            }, function () {
                P.sending = false;
                if (P.ui) P.ui.answer.classList.remove('qz-sending');
                toast('Нет связи, попробуйте ещё раз');
            });
        }

        function submitButton(label, getValue) {
            var btn = h('button', {type: 'button', cls: 'qz-btn qz-btn-primary qz-btn-xl qz-submit', disabled: true,
                text: label || 'Ответить'});
            btn.addEventListener('click', function () {
                var v = getValue();
                if (v !== null && v !== undefined) submit(v);
            });
            return btn;
        }

        function buildAnswer(q, box) {
            var t = q.type;
            if (isChoice(q) && t !== 'multi') return choiceUI(q, box);
            if (t === 'multi') return multiUI(q, box);
            if (t === 'order') return orderUI(q, box);
            if (t === 'word') return wordUI(q, box);
            if (t === 'slider') return sliderUI(q, box);
            if (t === 'pin') return pinUI(q, box);
            return textUI(q, box);
        }

        function choiceUI(q, box) {
            var grid = h('div', {cls: 'qz-opts' + (longOptions(q) ? ' qz-opts-long' : '') + (q.type === 'truefalse' ? ' qz-opts-tf' : '')});
            q.options.forEach(function (o, i) {
                grid.appendChild(h('button', {type: 'button', cls: 'qz-opt qz-c' + i, 'data-id': String(o.id),
                    onclick: function () {
                        if (box.classList.contains('qz-locked')) return;
                        sound.sfx('tap');
                        this.classList.add('qz-chosen');
                        submit(o.id);
                    }}, optionContent(q, o, i)));
            });
            box.appendChild(grid);
        }

        function multiUI(q, box) {
            var chosen = [];
            var btn = submitButton('Ответить', function () { return chosen.length ? chosen.slice() : null; });
            var grid = h('div', {cls: 'qz-opts qz-opts-multi' + (longOptions(q) ? ' qz-opts-long' : '')});
            q.options.forEach(function (o, i) {
                grid.appendChild(h('button', {type: 'button', cls: 'qz-opt qz-c' + i, 'aria-pressed': 'false',
                    onclick: function () {
                        if (box.classList.contains('qz-locked')) return;
                        sound.sfx('tap');
                        var at = chosen.indexOf(o.id);
                        if (at >= 0) chosen.splice(at, 1);
                        else chosen.push(o.id);
                        this.classList.toggle('qz-on', at < 0);
                        this.setAttribute('aria-pressed', at < 0 ? 'true' : 'false');
                        btn.disabled = !chosen.length;
                    }}, optionContent(q, o, i), h('i', {cls: 'qz-check fa fa-check'})));
            });
            box.appendChild(h('p', {cls: 'qz-hint', text: 'Отметьте все верные варианты'}));
            box.appendChild(grid);
            box.appendChild(btn);
        }

        function orderUI(q, box) {
            var list = h('ol', {cls: 'qz-order'});
            var btn = submitButton('Ответить', function () {
                return Array.prototype.map.call(list.children, function (li) { return Number(li.getAttribute('data-id')); });
            });
            btn.disabled = false;
            function move(li, dir) {
                var other = dir < 0 ? li.previousElementSibling : li.nextElementSibling;
                if (!other) return;
                flip(list, function () {
                    if (dir < 0) list.insertBefore(li, other);
                    else list.insertBefore(other, li);
                });
                sound.sfx('tap');
            }
            q.options.forEach(function (o, i) {
                var li = h('li', {cls: 'qz-order-item qz-c' + i, 'data-id': String(o.id), 'data-key': String(o.id)},
                    h('span', {cls: 'qz-grip', 'aria-hidden': 'true'}, h('i', {cls: 'fa fa-bars'})),
                    h('span', {cls: 'qz-opt-body'}, o.image ? h('img', {src: o.image, alt: '', cls: 'qz-opt-img'}) : null,
                        h('span', {cls: 'qz-opt-text', text: o.text})),
                    h('span', {cls: 'qz-order-btns'},
                        h('button', {type: 'button', cls: 'qz-mini', 'aria-label': 'Выше', onclick: function () { move(li, -1); }},
                            h('i', {cls: 'fa fa-chevron-up'})),
                        h('button', {type: 'button', cls: 'qz-mini', 'aria-label': 'Ниже', onclick: function () { move(li, 1); }},
                            h('i', {cls: 'fa fa-chevron-down'}))));
                dragSort(list, li);
                list.appendChild(li);
            });
            box.appendChild(h('p', {cls: 'qz-hint', text: 'Перетащите или двигайте стрелками'}));
            box.appendChild(list);
            box.appendChild(btn);
        }

        function dragSort(list, li) {
            var drag = null;
            li.addEventListener('pointerdown', function (e) {
                if (e.target.closest('button') || (e.button !== undefined && e.button > 0)) return;
                if (list.closest('.qz-locked')) return;
                var r = li.getBoundingClientRect();
                drag = {grabY: e.clientY - r.top, id: e.pointerId};
                try { li.setPointerCapture(e.pointerId); } catch (err) { /* ignore */ }
                li.classList.add('qz-dragging');
                e.preventDefault();
            });
            li.addEventListener('pointermove', function (e) {
                if (!drag || e.pointerId !== drag.id) return;
                var items = Array.prototype.slice.call(list.children);
                for (var i = 0; i < items.length; i++) {
                    var other = items[i];
                    if (other === li) continue;
                    var r = other.getBoundingClientRect(), mid = r.top + r.height / 2;
                    var before = items.indexOf(li) < i;
                    if (before && e.clientY > mid) {
                        list.insertBefore(li, other.nextSibling);
                        break;
                    }
                    if (!before && e.clientY < mid) {
                        list.insertBefore(li, other);
                        break;
                    }
                }
                li.style.transform = '';
                var own = li.getBoundingClientRect();
                li.style.transform = 'translateY(' + (e.clientY - drag.grabY - own.top) + 'px)';
            });
            function end() {
                if (!drag) return;
                drag = null;
                li.classList.remove('qz-dragging');
                li.style.transform = '';
            }
            li.addEventListener('pointerup', end);
            li.addEventListener('pointercancel', end);
        }

        function wordUI(q, box) {
            var picked = [];
            var answerRow = h('div', {cls: 'qz-tiles qz-tiles-answer', 'aria-label': 'Ваше слово'});
            var pool = h('div', {cls: 'qz-tiles qz-tiles-pool'});
            var btn = submitButton('Ответить', function () {
                return picked.length ? picked.map(function (i) { return q.letters[i]; }).join('') : null;
            });
            var back = h('button', {type: 'button', cls: 'qz-btn qz-btn-lg', 'aria-label': 'Стереть букву',
                onclick: function () {
                    if (picked.length) {
                        picked.pop();
                        draw();
                    }
                }}, h('i', {cls: 'fa fa-long-arrow-left'}), ' Стереть');
            function draw() {
                answerRow.innerHTML = '';
                pool.innerHTML = '';
                picked.forEach(function (idx, pos) {
                    answerRow.appendChild(h('button', {type: 'button', cls: 'qz-tile qz-tile-on', text: q.letters[idx],
                        onclick: function () {
                            picked.splice(pos, 1);
                            draw();
                        }}));
                });
                for (var n = picked.length; n < q.letters.length; n++) answerRow.appendChild(h('span', {cls: 'qz-tile qz-tile-slot'}));
                q.letters.forEach(function (ch, idx) {
                    var used = picked.indexOf(idx) >= 0;
                    pool.appendChild(h('button', {type: 'button', cls: 'qz-tile' + (used ? ' qz-tile-used' : ''), text: ch,
                        disabled: used, onclick: function () {
                            if (box.classList.contains('qz-locked')) return;
                            sound.sfx('tap');
                            picked.push(idx);
                            draw();
                        }}));
                });
                btn.disabled = !picked.length;
                back.disabled = !picked.length;
            }
            draw();
            box.appendChild(answerRow);
            box.appendChild(pool);
            box.appendChild(h('div', {cls: 'qz-row'}, back, btn));
        }

        function textUI(q, box) {
            var max = q.type === 'cloud' ? 30 : q.type === 'open' ? 300 : 100;
            var field = q.type === 'open' ?
                h('textarea', {cls: 'qz-field', rows: '3', maxlength: String(max), placeholder: 'Ваш ответ'}) :
                h('input', {cls: 'qz-field', type: 'text', maxlength: String(max), autocomplete: 'off', autocapitalize: 'off',
                    spellcheck: 'false', placeholder: q.type === 'cloud' ? 'Одно-два слова' : 'Ваш ответ'});
            var btn = submitButton('Ответить', function () {
                var v = field.value.trim();
                return v ? v : null;
            });
            field.addEventListener('input', function () { btn.disabled = !field.value.trim(); });
            field.addEventListener('keydown', function (e) {
                if (e.key === 'Enter' && !e.shiftKey && field.value.trim()) {
                    e.preventDefault();
                    btn.click();
                }
            });
            box.appendChild(field);
            box.appendChild(btn);
        }

        function sliderUI(q, box) {
            var s = q.slider || {min: 0, max: 100, step: 1, unit: ''};
            var step = Number(s.step) || 1, lo = Number(s.min), hi = Number(s.max);
            var start = lo + Math.round((hi - lo) / 2 / step) * step;
            var decimals = (String(step).split('.')[1] || '').length;
            var out = h('output', {cls: 'qz-slider-value'});
            var range = h('input', {type: 'range', cls: 'qz-range', min: String(lo), max: String(hi), step: String(step),
                value: String(start), 'aria-label': 'Ответ'});
            function showValue() { out.textContent = Number(range.value).toFixed(decimals) + (s.unit ? ' ' + s.unit : ''); }
            range.addEventListener('input', showValue);
            showValue();
            var btn = submitButton('Ответить', function () { return Number(range.value); });
            btn.disabled = false;
            box.appendChild(out);
            box.appendChild(range);
            box.appendChild(h('div', {cls: 'qz-range-ends'}, h('span', {text: String(lo)}), h('span', {text: String(hi)})));
            box.appendChild(btn);
        }

        function pinUI(q, box) {
            var spot = null;
            var marker = h('span', {cls: 'qz-pin-marker', hidden: true});
            var img = h('img', {src: q.image, alt: '', draggable: 'false'});
            var wrap = h('div', {cls: 'qz-pin-wrap qz-pin-input'}, img, marker);
            var btn = submitButton('Ответить', function () { return spot; });
            wrap.addEventListener('click', function (e) {
                if (box.classList.contains('qz-locked')) return;
                var r = img.getBoundingClientRect();
                if (!r.width || !r.height) return;
                spot = {x: Math.round(Math.max(0, Math.min(100, (e.clientX - r.left) / r.width * 100)) * 10) / 10,
                    y: Math.round(Math.max(0, Math.min(100, (e.clientY - r.top) / r.height * 100)) * 10) / 10};
                marker.style.left = spot.x + '%';
                marker.style.top = spot.y + '%';
                marker.hidden = false;
                btn.disabled = false;
                sound.sfx('tap');
            });
            box.appendChild(h('p', {cls: 'qz-hint', text: 'Коснитесь картинки, чтобы поставить точку'}));
            box.appendChild(wrap);
            box.appendChild(btn);
        }

        function showAnswered() {
            sound.urgent(false);
            show(h('div', {cls: 'qz-center qz-answered qz-enter'},
                h('div', {cls: 'qz-me-badge qz-pop'}, h('i', {cls: 'fa fa-paper-plane'})),
                h('h2', {text: 'Ответ принят'}),
                h('div', {cls: 'qz-wait'}, h('i'), h('i'), h('i')),
                h('p', {cls: 'qz-wait-text', text: MODE === 'solo' ? 'Проверяем…' : 'Ждём остальных игроков'})));
        }

        // ---------------- results

        function verdict(me) {
            if (!me || !me.answered) return {cls: 'qz-v-none', title: 'Нет ответа', icon: 'fa-clock-o'};
            if (!me.scored) return {cls: 'qz-v-info', title: 'Ответ принят', icon: 'fa-check'};
            if (me.correct) return {cls: 'qz-v-ok', title: 'Верно!', icon: 'fa-check'};
            if (me.points > 0) return {cls: 'qz-v-part', title: 'Частично', icon: 'fa-adjust'};
            return {cls: 'qz-v-bad', title: 'Неверно', icon: 'fa-times'};
        }

        function showReveal() {
            var st = game.st, q = P.q, res = P.res, me = res.me, rv = res.reveal;
            sound.music(null);
            sound.urgent(false);
            var v = verdict(me);
            var pts = h('b', {cls: 'qz-points', text: '0'});
            var head = h('div', {cls: 'qz-verdict ' + v.cls + ' qz-pop'},
                h('i', {cls: 'fa ' + v.icon + ' qz-verdict-icon'}),
                h('h2', {text: v.title}),
                me && me.scored && me.points > 0 ? h('div', {cls: 'qz-points-row'}, '+', pts) : null,
                me && me.scored && me.correct && me.streak >= 2 ? h('span', {cls: 'qz-streak qz-streak-big', text: '🔥 Серия ' + me.streak}) : null,
                me && me.rank ? h('p', {cls: 'qz-place-line', text: place(me.rank) + ' место из ' + me.total}) : null);
            var mine = P.mine !== null ? P.mine : (me ? me.value : null);
            var body = h('div', {cls: 'qz-reveal-body'},
                q.text ? h('div', {cls: 'qz-q-mini', html: q.text}) : null,
                typeof mine === 'string' ? h('p', {cls: 'qz-key-text'}, h('span', {cls: 'qz-muted', text: 'Ваш ответ: '}),
                    h('span', {text: mine})) : null,
                revealView(q, rv, {mine: mine}),
                explanation(rv));
            var view = h('div', {cls: 'qz-reveal qz-enter'}, head, body);
            if (MODE === 'solo') {
                var last = st.i + 1 >= st.n;
                view.appendChild(h('div', {cls: 'qz-sticky-actions'}, h('button', {type: 'button',
                    cls: 'qz-btn qz-btn-primary qz-btn-xl', text: last ? 'Итоги' : 'Дальше',
                    onclick: function () { soloNext(this); }})));
            }
            show(view);
            typeset(body.querySelector('.qz-q-mini'));
            if (me && me.scored && me.points > 0) {
                countUp(pts, 0, me.points, 900);
                if (P.effectsFor !== st.i) setTimeout(function () { sound.sfx('count_up', 900); }, 250);
            }
            else pts.textContent = String(me ? me.points : 0);
            if (P.effectsFor !== st.i) {
                P.effectsFor = st.i;
                if (me && me.answered && me.scored) {
                    if (me.correct || me.points > 0) {
                        sound.sfx('correct');
                        sound.vibrate([40, 60, 40]);
                        if (me.correct && me.streak >= 2) setTimeout(function () { sound.sfx('streak'); }, 500);
                    } else {
                        sound.sfx('wrong');
                        sound.vibrate(220);
                    }
                }
            }
        }

        function showBoard() {
            var res = P.res, me = res.me, lb = res.leaderboard || {top: [], total: 0};
            sound.music(null);
            var view = h('div', {cls: 'qz-board-view qz-enter'},
                me && me.rank ? h('div', {cls: 'qz-my-place qz-pop'},
                    h('span', {cls: 'qz-muted', text: 'Ваше место'}),
                    h('b', {text: String(me.rank)}),
                    h('span', {text: 'из ' + me.total + ' · ' + me.score + ' ' + plural(me.score, 'очко', 'очка', 'очков')})) : null,
                h('h3', {cls: 'qz-h3', text: 'Лидеры'}),
                leaderRows(lb.top, C.player, 5),
                h('div', {cls: 'qz-wait qz-wait-small'}, h('i'), h('i'), h('i')));
            show(view);
        }

        function showFinal() {
            var fin = P.fin, me = fin.me;
            sound.music(null);
            sound.urgent(false);
            var view = h('div', {cls: 'qz-final qz-enter'},
                h('h2', {cls: 'qz-final-title', text: 'Итоги'}),
                podium(fin.top, C.player),
                me ? h('div', {cls: 'qz-my-place'},
                    h('span', {cls: 'qz-muted', text: me.nickname + ' · ваше место'}),
                    h('b', {text: me.rank ? String(me.rank) : '—'}),
                    h('span', {text: me.score + ' ' + plural(me.score, 'очко', 'очка', 'очков') + ' · верно ' + me.correct +
                            ' из ' + fin.questions})) : null);
            if (fin.mistakes && fin.mistakes.length) {
                view.appendChild(h('h3', {cls: 'qz-h3', text: 'Работа над ошибками'}));
                var list = h('ol', {cls: 'qz-mistakes'}, fin.mistakes.map(function (m) {
                    return h('li', {},
                        h('span', {cls: 'qz-mistake-n', text: m.n}),
                        h('div', {},
                            h('p', {cls: 'qz-mistake-q', text: (m.text || 'Вопрос ' + m.n).replace(/\*\*|__|`/g, '')}),
                            h('p', {}, h('span', {cls: 'qz-muted', text: 'Ваш ответ: '}),
                                m.given === null || m.given === undefined ? h('i', {text: 'нет ответа'}) : h('s', {text: m.given})),
                            h('p', {}, h('span', {cls: 'qz-muted', text: 'Правильно: '}), h('b', {text: m.correct})),
                            m.explanation ? h('p', {cls: 'qz-muted qz-small', text: m.explanation.replace(/\*\*|__|`/g, '')}) : null));
                }));
                view.appendChild(list);
                setTimeout(function () { typeset(list); }, 0);
            } else if (me) {
                view.appendChild(h('p', {cls: 'qz-summary', text: 'Ни одной ошибки!'}));
            }
            view.appendChild(h('div', {cls: 'qz-row qz-row-center'},
                h('a', {cls: 'qz-btn qz-btn-primary qz-btn-lg', href: U.quiz, text: 'К викторине'}),
                h('a', {cls: 'qz-btn qz-btn-lg', href: U.join, text: 'Другая игра'})));
            show(view);
            if (me && me.rank && me.rank <= 3) {
                sound.sfx('finale');
                setTimeout(function () { sound.music('final'); }, 5200);
                sound.vibrate([60, 60, 60, 60, 200]);
                setTimeout(function () { confetti(5000); beatFlash(1); }, 3300);
            } else {
                sound.sfx('finale');
            }
        }

        poller.start();
    }

    // ============================================================ host: projector screen and phone remote

    function startHost() {
        var H = {v: 0, since: 0, players: 0, answered: 0, q: null, key: null, rv: null, lb: null, fin: null,
            loadingF: false, view: '', names: [], acting: false, effectsFor: '', ui: null, boardTimer: null};
        var poller = Poller(function () {
            return U.host_state + '?v=' + H.v + '&since=' + H.since;
        }, onData, function () {
            show(h('div', {cls: 'qz-center qz-msg'}, h('h2', {text: 'Игра не найдена'}),
                h('a', {cls: 'qz-btn', href: U.quiz, text: 'К викторине'})));
        }, 1000);
        var controls = byId('qz-controls');
        var corner = byId('qz-corner');
        keepAwake();
        updateSoundButtons();

        function onData(d) {
            if (d.error) return;
            H.players = d.players || 0;
            H.answered = d.answered || 0;
            var count = document.querySelector('#qz-count b');
            if (count) count.textContent = String(H.players);
            if (d.joined && d.joined.length) addNames(d.joined);
            if (!d.same) {
                H.v = d.v;
                if (d.question) H.q = d.question;
                if (d.key) H.key = d.key;
                if (d.reveal) H.rv = d.reveal;
                if (d.leaderboard) H.lb = d.leaderboard;
                game.st = d;
                setPaused(!!d.paused);
                setQnum(d);
                if (d.ph === 'finished' && !H.fin) loadFinal();
                render();
            } else if (game.st) {
                game.st.players = d.players;
            }
            updateCounters();
            updateControls();
        }

        function loadFinal() {
            if (H.loadingF) return;
            H.loadingF = true;
            request('GET', U.final).then(function (r) {
                H.loadingF = false;
                if (r.status === 200) {
                    H.fin = r.data;
                    render();
                } else setTimeout(loadFinal, 1500);
            }, function () {
                H.loadingF = false;
                setTimeout(loadFinal, 1500);
            });
        }

        function updateCounters() {
            if (ROLE === 'screen' && game.st && game.st.ph === 'question' && H.answered > (H.shownAnswered || 0)) {
                var more = Math.min(4, H.answered - (H.shownAnswered || 0));
                for (var k = 0; k < more; k++) setTimeout(function () { sound.sfx('answered'); }, k * 90);
            }
            H.shownAnswered = game.st && game.st.ph === 'question' ? H.answered : 0;
            var els = document.querySelectorAll('.qz-answered-n');
            for (var i = 0; i < els.length; i++) els[i].textContent = String(H.answered);
            els = document.querySelectorAll('.qz-players-n');
            for (i = 0; i < els.length; i++) els[i].textContent = String(H.players);
            var label = document.querySelector('.qz-lobby-count small');
            if (label) label.textContent = plural(H.players, 'игрок', 'игрока', 'игроков');
        }

        function updateControls() {
            var st = game.st;
            if (!controls || !st) return;
            var next = controls.querySelector('[data-act="next"]');
            var pause = controls.querySelector('[data-act="pause"]');
            var skip = controls.querySelector('[data-act="skip"]');
            var end = controls.querySelector('[data-act="end"]');
            var label = {lobby: 'Начать', question: 'Показать ответ', reveal: 'Таблица',
                leaderboard: st.i + 1 >= st.n ? 'Итоги' : 'Следующий вопрос', finished: 'Готово'}[st.ph] || 'Далее';
            next.querySelector('span').textContent = label;
            next.disabled = st.ph === 'finished' || (st.ph === 'lobby' && !H.players);
            pause.disabled = st.ph === 'lobby' || st.ph === 'finished';
            pause.querySelector('span').textContent = st.paused ? 'Продолжить' : 'Пауза';
            pause.querySelector('i').className = st.paused ? 'fa fa-play' : 'fa fa-pause';
            skip.disabled = st.ph !== 'question';
            end.disabled = st.ph === 'finished';
            controls.classList.toggle('qz-controls-done', st.ph === 'finished');
        }

        function act(name, extra) {
            sound.unlock();
            if (name === 'sound') {
                sound.toggle();
                return;
            }
            if (name === 'fullscreen') {
                toggleFullscreen();
                return;
            }
            if (name === 'end' && !window.confirm('Завершить игру для всех?')) return;
            var st = game.st;
            if (!st) return;
            if (name === 'next' && st.ph === 'lobby') name = 'start';
            if (name === 'pause' && st.paused) name = 'resume';
            if (H.acting) return;
            H.acting = true;
            var body = {action: name};
            if (extra) for (var k in extra) if (extra.hasOwnProperty(k)) body[k] = extra[k];
            request('POST', U.host_action, body, true).then(function (r) {
                H.acting = false;
                if (r.status !== 200) toast(r.data.error || 'Не получилось');
                poller.now();
            }, function () {
                H.acting = false;
                toast('Нет связи');
            });
        }

        function toggleFullscreen() {
            var d = document;
            if (d.fullscreenElement || d.webkitFullscreenElement) {
                (d.exitFullscreen || d.webkitExitFullscreen).call(d);
            } else {
                var el = d.documentElement;
                var fn = el.requestFullscreen || el.webkitRequestFullscreen;
                if (fn) {
                    var p = fn.call(el);
                    if (p && p.catch) p.catch(function () {});
                }
            }
        }

        if (controls) {
            controls.addEventListener('click', function (e) {
                var b = e.target.closest('[data-act]');
                if (b && !b.disabled) act(b.getAttribute('data-act'));
            });
        }

        document.addEventListener('keydown', function (e) {
            if (e.target.closest && e.target.closest('input, textarea, select')) return;
            if (e.ctrlKey || e.metaKey || e.altKey) return;
            var key = e.key;
            if (key === ' ' || key === 'ArrowRight' || key === 'Enter') {
                e.preventDefault();
                var st = game.st;
                if (st && st.ph !== 'finished' && !(st.ph === 'lobby' && !H.players)) act('next');
            } else if (key === 'p' || key === 'P' || key === 'з' || key === 'З') {
                if (game.st && game.st.ph !== 'lobby' && game.st.ph !== 'finished') act('pause');
            } else if (key === 'f' || key === 'F' || key === 'а' || key === 'А') {
                if (ROLE === 'screen') act('fullscreen');
            } else if (key === 'm' || key === 'M' || key === 'ь' || key === 'Ь') {
                act('sound');
            }
        });

        // ---------------- lobby names

        function addNames(rows) {
            var fresh = [];
            rows.forEach(function (row) {
                H.since = Math.max(H.since, row.id);
                for (var i = 0; i < H.names.length; i++) if (H.names[i].id === row.id) return;
                H.names.push(row);
                fresh.push(row);
            });
            var box = byId('qz-names');
            if (box && fresh.length) {
                fresh.slice(-150).forEach(function (row) { box.appendChild(nameChip(row, true)); });
                if (ROLE === 'screen') sound.sfx('join');
                var empty = byId('qz-names-empty');
                if (empty) empty.hidden = true;
            }
        }

        function nameChip(row, pop) {
            return h('button', {type: 'button', cls: 'qz-name' + (pop ? ' qz-pop' : ''), title: 'Удалить игрока',
                'data-id': String(row.id), text: row.nickname, onclick: function () {
                    var chip = this;
                    if (!window.confirm('Удалить игрока «' + row.nickname + '»?')) return;
                    request('POST', U.host_action, {action: 'kick', player: String(row.id)}, true).then(function (r) {
                        if (r.status === 200) {
                            chip.remove();
                            H.names = H.names.filter(function (n) { return n.id !== row.id; });
                            poller.now();
                        } else toast(r.data.error || 'Не получилось');
                    });
                }});
        }

        // ---------------- views

        function render() {
            var st = game.st;
            var key = st.ph + ':' + st.i;
            if (st.ph === 'finished') key += H.fin ? ':f' : ':w';
            if (corner) corner.hidden = st.ph === 'lobby' || st.ph === 'finished';
            if (key === H.view) return;
            H.view = key;
            H.ui = null;
            clearTimeout(H.boardTimer);
            if (st.ph !== 'question') sound.urgent(false);
            if (st.ph === 'lobby') return ROLE === 'screen' ? screenLobby() : remoteLobby();
            if (st.ph === 'question') return ROLE === 'screen' ? screenQuestion() : remoteQuestion();
            if (st.ph === 'reveal') return ROLE === 'screen' ? screenReveal() : remoteReveal();
            if (st.ph === 'leaderboard') return ROLE === 'screen' ? screenBoard() : remoteBoard();
            if (st.ph === 'finished') return H.fin ? (ROLE === 'screen' ? screenFinal() : remoteFinal()) : show(wait('Подводим итоги…'));
        }

        function namesBox() {
            var box = h('div', {id: 'qz-names', cls: 'qz-names'});
            H.names.forEach(function (row) { box.appendChild(nameChip(row, false)); });
            return box;
        }

        function startButton() {
            return h('button', {type: 'button', cls: 'qz-btn qz-btn-primary qz-btn-xl qz-start', onclick: function () { act('start'); }},
                h('i', {cls: 'fa fa-play'}), ' Начать');
        }

        function screenLobby() {
            sound.music('lobby');
            var url = (C.joinAbsolute || '').replace(/^https?:\/\//, '').replace(/\/$/, '');
            show(h('div', {cls: 'qz-lobby qz-enter'},
                h('div', {cls: 'qz-lobby-join'},
                    h('div', {cls: 'qz-lobby-steps'},
                        h('p', {}, 'Откройте ', h('b', {cls: 'qz-lobby-url', text: url})),
                        h('p', {text: 'и введите PIN'}),
                        h('div', {cls: 'qz-lobby-pin', text: spacedPin(C.pin)}),
                        h('p', {cls: 'qz-muted', text: 'или наведите камеру на QR-код'})),
                    h('img', {cls: 'qz-lobby-qr', src: U.qr, alt: 'QR-код для входа'})),
                h('div', {cls: 'qz-lobby-players'},
                    h('div', {cls: 'qz-lobby-top'},
                        h('div', {cls: 'qz-lobby-count'}, h('b', {cls: 'qz-players-n', text: String(H.players)}),
                            h('small', {text: plural(H.players, 'игрок', 'игрока', 'игроков')})),
                        h('span', {cls: 'qz-spacer'}),
                        startButton()),
                    h('p', {id: 'qz-names-empty', cls: 'qz-muted qz-names-empty', hidden: H.names.length > 0, text: 'Ждём игроков…'}),
                    namesBox(),
                    h('p', {cls: 'qz-muted qz-small', text: 'Нажмите на имя, чтобы удалить игрока.'}))));
        }

        function remoteLobby() {
            show(h('div', {cls: 'qz-remote qz-enter'},
                h('div', {cls: 'qz-remote-pin'}, 'PIN ', h('b', {text: spacedPin(C.pin)})),
                h('img', {cls: 'qz-remote-qr', src: U.qr, alt: 'QR-код для входа'}),
                h('p', {cls: 'qz-muted qz-remote-url', text: (C.joinAbsolute || '').replace(/^https?:\/\//, '') + '?pin=' + C.pin}),
                h('div', {cls: 'qz-lobby-count'}, h('b', {cls: 'qz-players-n', text: String(H.players)}),
                    h('small', {text: plural(H.players, 'игрок', 'игрока', 'игроков')})),
                h('p', {id: 'qz-names-empty', cls: 'qz-muted', hidden: H.names.length > 0, text: 'Ждём игроков…'}),
                namesBox()));
        }

        function keyText(q, key) {
            if (!q || !key) return '';
            var t = q.type;
            if (t === 'poll' || t === 'cloud' || t === 'open') return 'Нет правильного ответа';
            if (t === 'order') return (key.correct || []).map(function (id) { return optionLabel(q, id); }).join(' → ');
            if (t === 'word') return String(key.word || '').toUpperCase();
            if (t === 'text' || (t === 'code' && q.input)) return (key.answers || []).join(' / ');
            if (t === 'slider') return key.answer + (q.slider && q.slider.unit ? ' ' + q.slider.unit : '');
            if (t === 'pin') return 'Точка (' + key.x + '%; ' + key.y + '%), радиус ' + key.r + '%';
            return (key.correct || []).map(function (id) { return optionLabel(q, id); }).join(', ');
        }

        function questionBody(q) {
            var t = q.type;
            if (isChoice(q)) {
                var grid = h('div', {cls: 'qz-opts qz-opts-show' + (longOptions(q) ? ' qz-opts-long' : '')});
                q.options.forEach(function (o, i) {
                    grid.appendChild(h('div', {cls: 'qz-opt qz-c' + i}, optionContent(q, o, i)));
                });
                return grid;
            }
            if (t === 'order') {
                return h('ol', {cls: 'qz-order qz-order-show'}, q.options.map(function (o, i) {
                    return h('li', {cls: 'qz-order-item qz-c' + i}, h('span', {cls: 'qz-opt-body'},
                        o.image ? h('img', {src: o.image, alt: '', cls: 'qz-opt-img'}) : null, h('span', {cls: 'qz-opt-text', text: o.text})));
                }));
            }
            if (t === 'word') {
                return h('div', {cls: 'qz-tiles qz-tiles-show'}, (q.letters || []).map(function (ch) {
                    return h('span', {cls: 'qz-tile', text: ch});
                }));
            }
            if (t === 'pin') return h('div', {cls: 'qz-pin-wrap'}, h('img', {src: q.image, alt: ''}));
            if (t === 'slider') {
                var s = q.slider || {};
                return h('p', {cls: 'qz-hint-big', text: 'Выберите число от ' + s.min + ' до ' + s.max + (s.unit ? ' ' + s.unit : '')});
            }
            var hints = {cloud: 'Напишите слово на телефоне', open: 'Напишите ответ на телефоне'};
            return h('p', {cls: 'qz-hint-big', text: hints[t] || 'Введите ответ на телефоне'});
        }

        function screenQuestion() {
            var q = H.q;
            sound.music(null);
            var ringBox = h('div', {cls: 'qz-ring-wrap qz-ring-big'});
            var view = h('div', {cls: 'qz-host-q qz-enter'},
                h('div', {cls: 'qz-host-q-main'}, questionHead(q, true), questionBody(q)),
                h('aside', {cls: 'qz-host-side'}, ringBox,
                    h('div', {cls: 'qz-answered-box'}, h('b', {cls: 'qz-answered-n', text: String(H.answered)}),
                        h('span', {}, 'из ', h('span', {cls: 'qz-players-n', text: String(H.players)})),
                        h('small', {text: 'ответили'}))),
                countdownEl());
            H.ui = {view: view, ring: null, opened: false, timeOver: false};
            show(view);
            H.ui.ring = makeRing(ringBox);
            hostTick(timing());
        }

        function remoteQuestion() {
            var q = H.q;
            var timer = h('b', {cls: 'qz-remote-timer'});
            var view = h('div', {cls: 'qz-remote qz-enter'},
                h('div', {cls: 'qz-remote-head'}, h('span', {cls: 'qz-q-type', text: q.type_name}), timer),
                q.text ? h('div', {cls: 'qz-q-text', html: q.text}) : null,
                q.code ? h('pre', {cls: 'qz-code'}, h('code', {text: q.code})) : null,
                h('div', {cls: 'qz-remote-key'}, h('span', {cls: 'qz-muted', text: 'Ответ: '}), h('b', {text: keyText(q, H.key)})),
                h('div', {cls: 'qz-answered-box qz-answered-inline'}, 'Ответили ', h('b', {cls: 'qz-answered-n', text: String(H.answered)}),
                    ' из ', h('b', {cls: 'qz-players-n', text: String(H.players)})),
                countdownEl());
            H.ui = {view: view, timer: timer, opened: false};
            show(view);
            typeset(view.querySelector('.qz-q-text'));
            hostTick(timing());
        }

        function hostTick(t) {
            if (!H.ui || !game.st || game.st.ph !== 'question') return;
            var counting = runCountdown(H.ui.view, t, ROLE === 'screen');
            if (H.ui.ring && t) H.ui.ring.set(counting ? 1 : t.left / t.total, Math.ceil(counting ? t.total : t.left));
            if (H.ui.timer && t) H.ui.timer.textContent = counting ? '…' : String(Math.ceil(t.left));
            if (!t) return;
            if (!counting && !H.ui.opened) {
                H.ui.opened = true;
                sound.music('question', game.st.i);
            }
            if (H.ui.opened && !game.st.paused) {
                sound.urgent(t.left <= 5 && t.left > 0);
                if (ROLE === 'screen') clockSound(H.ui, t);
                if (t.left <= 0 && !H.ui.timeOver) {
                    H.ui.timeOver = true;
                    sound.urgent(false);
                    sound.music(null);
                    setTimeout(function () { poller.now(); }, 600);
                }
            }
        }
        tickHandlers.push(function (t) { if (IS_HOST) hostTick(t); });

        function revealEffects() {
            var tag = 'r' + game.st.i;
            if (H.effectsFor === tag) return;
            H.effectsFor = tag;
            sound.music(null);
            if (ROLE === 'screen') sound.sfx('reveal');
        }

        function screenReveal() {
            var q = H.q, rv = H.rv;
            if (!q || !rv) return show(wait());
            revealEffects();
            var view = h('div', {cls: 'qz-host-reveal qz-enter'},
                h('div', {cls: 'qz-host-reveal-q'}, h('span', {cls: 'qz-q-type', text: q.type_name}),
                    q.text ? h('div', {cls: 'qz-q-text', html: q.text}) : null),
                revealView(q, rv, {hideable: true}),
                revealSummary(rv),
                explanation(rv));
            show(view);
            typeset(view.querySelector('.qz-q-text'));
        }

        function remoteReveal() {
            var q = H.q, rv = H.rv;
            if (!q || !rv) return show(wait());
            revealEffects();
            show(h('div', {cls: 'qz-remote qz-enter'},
                h('div', {cls: 'qz-remote-key'}, h('span', {cls: 'qz-muted', text: 'Ответ: '}), h('b', {text: keyText(q, H.key)})),
                revealSummary(rv),
                rv.type === 'open' ? openView(rv.texts || [], false) : null,
                h('h3', {cls: 'qz-h3', text: 'Лидеры'}),
                leaderRows((H.lb || {top: []}).top, null, 5)));
        }

        function screenBoard() {
            var lb = H.lb || {top: [], total: 0};
            var top = lb.top.slice(0, 5);
            // Start in the previous order with the previous scores, then move to the new places.
            var before = top.slice().sort(function (a, b) {
                return (a.prev || 9999) - (b.prev || 9999) || a.rank - b.rank;
            });
            var list = h('ol', {cls: 'qz-board qz-board-big'});
            before.forEach(function (row) {
                list.appendChild(h('li', {cls: 'qz-board-row', 'data-key': String(row.id)},
                    h('span', {cls: 'qz-board-place', text: String(row.prev || '')}),
                    h('span', {cls: 'qz-board-nick', text: row.nick}),
                    row.streak >= 2 ? h('span', {cls: 'qz-streak', text: '🔥 ' + row.streak}) : null,
                    row.delta ? h('span', {cls: 'qz-delta', text: '+' + row.delta}) : null,
                    h('b', {cls: 'qz-board-score', text: String(row.score - row.delta)})));
            });
            show(h('div', {cls: 'qz-host-board qz-enter'}, h('h2', {cls: 'qz-board-title', text: 'Лидеры'}), list,
                lb.total > 5 ? h('p', {cls: 'qz-muted', text: 'Всего игроков: ' + lb.total}) : null));
            sound.music('board');
            H.boardTimer = setTimeout(function () {
                beatFlash(1);
                sound.sfx('count_up', 1200);
                if (top.some(function (row) { return row.prev && row.rank < row.prev; })) setTimeout(function () { sound.sfx('rise'); }, 60);
                flip(list, function () {
                    top.forEach(function (row) {
                        var li = list.querySelector('[data-key="' + row.id + '"]');
                        if (li) list.appendChild(li);
                    });
                });
                top.forEach(function (row) {
                    var li = list.querySelector('[data-key="' + row.id + '"]');
                    if (!li) return;
                    li.querySelector('.qz-board-place').textContent = String(row.rank);
                    if (row.prev && row.rank < row.prev) li.classList.add('qz-up');
                    countUp(li.querySelector('.qz-board-score'), row.score - row.delta, row.score, 1200);
                });
                H.boardTimer = setTimeout(function () { sound.music(null); }, 2000);
            }, 900);
        }

        function remoteBoard() {
            var lb = H.lb || {top: [], total: 0};
            show(h('div', {cls: 'qz-remote qz-enter'}, h('h3', {cls: 'qz-h3', text: 'Лидеры'}), leaderRows(lb.top, null, 10)));
        }

        function finalLinks() {
            return h('div', {cls: 'qz-row qz-row-center qz-final-links'},
                h('a', {cls: 'qz-btn qz-btn-primary qz-btn-lg', href: U.report}, h('i', {cls: 'fa fa-table'}), ' Отчёт'),
                h('a', {cls: 'qz-btn qz-btn-lg', href: U.xlsx}, h('i', {cls: 'fa fa-file-excel-o'}), ' Excel'),
                h('a', {cls: 'qz-btn qz-btn-lg', href: U.quiz, text: 'К викторине'}));
        }

        function screenFinal() {
            var fin = H.fin;
            sound.music(null);
            show(h('div', {cls: 'qz-final qz-final-host qz-enter'},
                h('h2', {cls: 'qz-final-title', text: C.title}),
                podium(fin.top, null),
                fin.top.length > 3 ? leaderRows(fin.top.slice(3, 10).map(function (r) {
                    return {id: r.id, nick: r.nickname, score: r.score, rank: r.rank};
                }), null, 7) : null,
                h('p', {cls: 'qz-muted', text: 'Игроков: ' + fin.total + ' · вопросов: ' + fin.questions}),
                finalLinks()));
            if (H.effectsFor !== 'fin') {
                H.effectsFor = 'fin';
                sound.sfx('finale');
                setTimeout(function () { sound.music('final'); }, 5200);
                setTimeout(function () { confetti(6000); beatFlash(1); }, 3300);
            }
        }

        function remoteFinal() {
            var fin = H.fin;
            show(h('div', {cls: 'qz-remote qz-enter'}, h('h3', {cls: 'qz-h3', text: 'Итоги'}),
                leaderRows(fin.top.map(function (r) { return {id: r.id, nick: r.nickname, score: r.score, rank: r.rank}; }), null, 10),
                finalLinks()));
        }

        poller.start();
    }

    // ------------------------------------------------------------ go

    function boot() {
        stage.classList.add('qz-ready');
        if (ROLE === 'screen' || (!IS_HOST && (MODE === 'auto' || MODE === 'solo'))) beatGlow();
        if (IS_HOST) startHost();
        else startPlayer();
    }

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
    else boot();
})();
