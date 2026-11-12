/* Touch-typing trainer: lessons by keyboard zones (like Stamina), timed speed tests, code. */
document.addEventListener('DOMContentLoaded', function () {
    'use strict';

    var C = window.TYPING;          // config from the page: strings, urls, csrf, signed in, done lessons
    var S = C.strings;
    var $ = function (s) { return document.querySelector(s); };

    /* ---------------- keyboards ---------------- */

    // Physical keys by row, written as they are on the English layout.
    var ROWS = [
        ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '='],
        ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\\'],
        ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\''],
        ['z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/']
    ];
    var FINGER = {   // lp lr lm li | ri rm rr rp
        '`': 'lp', '1': 'lp', '2': 'lr', '3': 'lm', '4': 'li', '5': 'li', '6': 'ri', '7': 'ri', '8': 'rm', '9': 'rr',
        '0': 'rp', '-': 'rp', '=': 'rp', q: 'lp', w: 'lr', e: 'lm', r: 'li', t: 'li', y: 'ri', u: 'ri', i: 'rm',
        o: 'rr', p: 'rp', '[': 'rp', ']': 'rp', '\\': 'rp', a: 'lp', s: 'lr', d: 'lm', f: 'li', g: 'li', h: 'ri',
        j: 'ri', k: 'rm', l: 'rr', ';': 'rp', '\'': 'rp', z: 'lp', x: 'lr', c: 'lm', v: 'li', b: 'li', n: 'ri',
        m: 'ri', ',': 'rm', '.': 'rr', '/': 'rp'
    };
    var SHIFT_EN = {
        '`': '~', '1': '!', '2': '@', '3': '#', '4': '$', '5': '%', '6': '^', '7': '&', '8': '*', '9': '(', '0': ')',
        '-': '_', '=': '+', '[': '{', ']': '}', '\\': '|', ';': ':', '\'': '"', ',': '<', '.': '>', '/': '?'
    };
    var RU = {
        '`': 'ё', q: 'й', w: 'ц', e: 'у', r: 'к', t: 'е', y: 'н', u: 'г', i: 'ш', o: 'щ', p: 'з', '[': 'х', ']': 'ъ',
        a: 'ф', s: 'ы', d: 'в', f: 'а', g: 'п', h: 'р', j: 'о', k: 'л', l: 'д', ';': 'ж', '\'': 'э',
        z: 'я', x: 'ч', c: 'с', v: 'м', b: 'и', n: 'т', m: 'ь', ',': 'б', '.': 'ю', '/': '.'
    };
    var SHIFT_RU = {'1': '!', '2': '"', '3': '№', '4': ';', '5': '%', '6': ':', '7': '?', '8': '*', '9': '(',
                    '0': ')', '-': '_', '=': '+', '\\': '/', '/': ','};

    // charMap[char] = {key, shift}: which physical key types this character on the chosen layout.
    function buildLayout(name) {
        var map = {};
        ROWS.forEach(function (row) {
            row.forEach(function (key) {
                var plain = name === 'en' ? key : (RU[key] || key);
                var shifted;
                if (name === 'en') shifted = SHIFT_EN[key] || key.toUpperCase();
                else shifted = SHIFT_RU[key] || (RU[key] ? RU[key].toUpperCase() : key);
                if (!(plain in map)) map[plain] = {key: key, shift: false};
                if (shifted !== plain && !(shifted in map)) map[shifted] = {key: key, shift: true};
            });
        });
        map[' '] = {key: ' ', shift: false};
        map['\n'] = {key: 'enter', shift: false};
        return map;
    }

    function keyLabel(layout, key) {
        if (layout === 'en') return key.toUpperCase();
        return (RU[key] || key).toUpperCase();
    }

    var keyboardEl = $('#ty-keyboard');
    var keyEls = {};

    function drawKeyboard(layout) {
        keyboardEl.innerHTML = '';
        keyEls = {};
        ROWS.forEach(function (row, r) {
            var line = document.createElement('div');
            line.className = 'ty-row ty-row-' + r;
            if (r === 3) line.appendChild(special('shiftl', 'Shift', 'ty-wide2', 'lp'));
            if (r === 2) line.appendChild(special('caps', 'Caps', 'ty-wide15', 'lp'));
            if (r === 1) line.appendChild(special('tab', 'Tab', 'ty-wide15', 'lp'));
            row.forEach(function (key) {
                var el = document.createElement('div');
                el.className = 'ty-key ty-f-' + FINGER[key] + (key === 'f' || key === 'j' ? ' ty-home' : '');
                el.textContent = keyLabel(layout, key);
                line.appendChild(el);
                keyEls[key] = el;
            });
            if (r === 0) line.appendChild(special('backspace', '⌫', 'ty-wide2', 'rp'));
            if (r === 2) line.appendChild(special('enter', 'Enter', 'ty-wide2', 'rp'));
            if (r === 3) line.appendChild(special('shiftr', 'Shift', 'ty-wide25', 'rp'));
            keyboardEl.appendChild(line);
        });
        var last = document.createElement('div');
        last.className = 'ty-row';
        last.appendChild(special(' ', '', 'ty-space', 'th'));
        keyboardEl.appendChild(last);
    }

    function special(id, label, cls, finger) {
        var el = document.createElement('div');
        el.className = 'ty-key ' + cls + ' ty-f-' + finger;
        el.textContent = label;
        keyEls[id] = el;
        return el;
    }

    var FINGER_NAME = {lp: S.lp, lr: S.lr, lm: S.lm, li: S.li, ri: S.ri, rm: S.rm, rr: S.rr, rp: S.rp, th: S.thumb};

    function highlight(ch) {
        Object.keys(keyEls).forEach(function (k) { keyEls[k].classList.remove('ty-next', 'ty-next-shift'); });
        var info = state.charMap[ch];
        var hint = '';
        if (info) {
            var el = keyEls[info.key];
            if (el) el.classList.add('ty-next');
            var finger = info.key === ' ' ? 'th' : info.key === 'enter' ? 'rp' : FINGER[info.key];
            if (info.shift) {
                // Shift is pressed with the other hand.
                var left = finger && finger[0] === 'l';
                var shiftKey = keyEls[left ? 'shiftr' : 'shiftl'];
                if (shiftKey) shiftKey.classList.add('ty-next-shift');
                hint = FINGER_NAME[finger] + ' + Shift';
            } else {
                hint = FINGER_NAME[finger] || '';
            }
        }
        $('#ty-finger').textContent = hint;
    }

    function press(ch, ok) {
        var info = state.charMap[ch];
        var el = info && keyEls[info.key];
        if (!el) return;
        el.classList.add(ok ? 'ty-hit' : 'ty-miss');
        setTimeout(function () { el.classList.remove('ty-hit', 'ty-miss'); }, 140);
    }

    /* ---------------- sounds (generated, no files) ---------------- */

    var audio = null;
    var soundOn = load('typing-sound', '1') === '1';
    function tone(freq, length, type, gain) {
        if (!soundOn) return;
        try {
            audio = audio || new (window.AudioContext || window.webkitAudioContext)();
            var osc = audio.createOscillator();
            var vol = audio.createGain();
            osc.type = type;
            osc.frequency.value = freq;
            vol.gain.setValueAtTime(gain, audio.currentTime);
            vol.gain.exponentialRampToValueAtTime(0.0001, audio.currentTime + length);
            osc.connect(vol);
            vol.connect(audio.destination);
            osc.start();
            osc.stop(audio.currentTime + length);
        } catch (e) { /* no audio */ }
    }
    var sound = {
        key: function () { tone(1800 + Math.random() * 300, 0.035, 'square', 0.04); },
        error: function () { tone(170, 0.18, 'sawtooth', 0.09); },
        done: function () { tone(660, 0.12, 'sine', 0.12); setTimeout(function () { tone(990, 0.2, 'sine', 0.12); }, 120); }
    };

    function load(k, d) { try { var v = localStorage.getItem(k); return v === null ? d : v; } catch (e) { return d; } }
    function store(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* ignore */ } }

    /* ---------------- exercises ---------------- */

    // Lessons add keys a few at a time, home row first, as in Stamina and similar trainers.
    // The numbers are stored with results: new lessons are only added at the end.
    var LESSONS = ['fj', 'dk', 'sl', 'a;', 'gh', 'ru', 'ei', 'wo', 'qp', 'ty', 'vm', 'c,', 'x.', 'z/', 'bn', '\'[]', '`',
                   'SHIFT', '1234567890', 'WORDS', 'PUNCT', 'SYMBOLS', 'PHRASES', 'TEXT'];
    var SPECIAL = {SHIFT: 'capitals', '1234567890': 'digits', WORDS: 'allLetters', PUNCT: 'punctuation',
                   SYMBOLS: 'symbols', PHRASES: 'phrases', TEXT: 'longText'};
    var STARS = [60, 100, 150];   // chars/min for one, two and three stars (accuracy 93% and more)
    var PASS_CPM = STARS[0];
    var PASS_ACC = 93;

    function lessonTitle(i, layout) {
        var keys = LESSONS[i];
        if (SPECIAL[keys]) return S[SPECIAL[keys]];
        return keys.split('').map(function (k) { return keyLabel(layout, k); }).join(' ');
    }

    function stars(cpm) {
        var n = 0;
        STARS.forEach(function (t) { if (cpm >= t) n++; });
        return n;
    }

    function letter(layout, key) { return layout === 'en' ? key : (RU[key] || key); }

    function pick(list) { return list[Math.floor(Math.random() * list.length)]; }

    function words(lang) {
        var seen = {};
        return window.TYPING_WORDS[lang].filter(function (w) {
            if (!w || seen[w]) return false;
            seen[w] = true;
            return true;
        });
    }

    function capital(w) { return w.charAt(0).toUpperCase() + w.slice(1); }

    function phrasesText(lang, length) {
        var list = window.TYPING_PHRASES[lang].slice();
        for (var i = list.length - 1; i > 0; i--) {   // shuffled, so no phrase repeats
            var j = Math.floor(Math.random() * (i + 1));
            var t = list[i]; list[i] = list[j]; list[j] = t;
        }
        var out = [];
        var size = 0;
        while (size < length && out.length < list.length) {
            var p = list[out.length];
            out.push(p);
            size += p.length + 1;
        }
        return out.join(' ');
    }

    function punctuationText(lang) {
        // Real words in short sentences: commas, full stops, questions, exclamations, colons, dashes.
        var list = words(lang);
        var out = [];
        var size = 0;
        while (size < 160) {
            var n = 3 + Math.floor(Math.random() * 4);
            var sentence = [];
            for (var i = 0; i < n; i++) {
                var w = pick(list);
                if (i === 1 && Math.random() < 0.4) w += ',';
                if (i === 2 && Math.random() < 0.15) w += ' -';
                if (i === 2 && Math.random() < 0.1) w += ':';
                sentence.push(w);
            }
            var s = capital(sentence.join(' ').replace(/[,:-]+$/, '')) + pick(['.', '.', '.', '?', '!']);
            out.push(s);
            size += s.length + 1;
        }
        return out.join(' ');
    }

    function symbolsText(layout) {
        var tokens = layout === 'en' ? [
            '(a + b)', 'a[i]', 'x == y', 'a != b', 'i++', '{ }', 'f(x);', '"text"', '\'c\'', 'a < b', 'b > c',
            'x <= 10', 'y >= 0', 'a && b', 'a || b', 's += 1;', '50%', '#include', 'user@mail', 'a * b', 'n / 2',
            'arr[0]', 'm[k] = v;', '<p>', '$x', 'a - b', 'k % 2', '!ok', 'x = y + 1;', '(1, 2)', 'a ^ b', '~x'
        ] : [
            '(а + б)', 'а = б', '50%', '№7', '"да"', 'да?', 'нет!', 'а: б', 'а; б', '2 * 3', '1 + 1 = 2',
            'х - у', '_', '(5)', '10%', '№12', '"Ош"', 'как?', 'ура!', 'итог: 5', 'а/б', '(1; 2)', 'а * б = в'
        ];
        var out = [];
        var size = 0;
        while (size < 150) {
            var t = pick(tokens);
            out.push(t);
            size += t.length + 1;
        }
        return out.join(' ');
    }

    function lessonText(index, layout, lang) {
        var kind = LESSONS[index];
        if (kind === 'PHRASES') return phrasesText(lang, 170);
        if (kind === 'TEXT') return phrasesText(lang, 380);
        if (kind === 'PUNCT') return punctuationText(lang);
        if (kind === 'SYMBOLS') return symbolsText(layout);
        if (kind === 'WORDS') return testText(lang).slice(0, 170).replace(/ \S*$/, '');
        lang = layout === 'en' ? 'en' : 'ru';
        var allowed = {};
        var fresh = {};
        for (var i = 0; i <= index; i++) {
            if (SPECIAL[LESSONS[i]]) continue;
            LESSONS[i].split('').forEach(function (k) {
                var ch = letter(layout, k);
                allowed[ch] = true;
                if (i === index) fresh[ch] = true;
            });
        }
        var latest = Object.keys(fresh).length ? fresh : allowed;
        var dict = words(lang).filter(function (w) {
            return w.split('').every(function (ch) { return allowed[ch]; });
        });
        var withNew = dict.filter(function (w) { return w.split('').some(function (ch) { return latest[ch]; }); });
        var letters = Object.keys(allowed);
        var newLetters = Object.keys(latest);
        var out = [];
        var length = 0;
        while (length < 150) {
            var w;
            if (withNew.length >= 4 && Math.random() < 0.6) w = pick(withNew);
            else if (dict.length >= 8 && Math.random() < 0.5) w = pick(dict);
            else {
                // Made-up syllables from the keys learnt so far, with the new keys more often.
                var n = 2 + Math.floor(Math.random() * 4);
                w = '';
                for (var j = 0; j < n; j++) w += Math.random() < 0.5 ? pick(newLetters) : pick(letters);
            }
            if (LESSONS[index] === 'SHIFT') w = w.charAt(0).toUpperCase() + w.slice(1);
            if (LESSONS[index] === '1234567890' && Math.random() < 0.5) w = String(Math.floor(Math.random() * 1000));
            out.push(w);
            length += w.length + 1;
        }
        return out.join(' ');
    }

    function testText(lang) {
        var list = words(lang);
        var out = [];
        for (var i = 0; i < 160; i++) out.push(pick(list));
        return out.join(' ');
    }

    /* ---------------- the exercise ---------------- */

    var state = {};
    var textEl = $('#ty-text');
    var input = $('#ty-input');
    var timer = null;

    function settings() {
        return {
            mode: load('typing-mode', 'lesson'),
            layout: load('typing-layout', C.defaultLayout),
            lesson: parseInt(load('typing-lesson-' + load('typing-layout', C.defaultLayout), '0'), 10) || 0,
            duration: parseInt(load('typing-duration', '60'), 10),
            codeLang: load('typing-code-lang', ''),
            codeLevel: parseInt(load('typing-code-level', '0'), 10) || 0
        };
    }

    var lastSnippet = null;
    function pickSnippet(lang, level) {
        var list = window.TYPING_CODE.filter(function (c) {
            return (!lang || c.lang === lang) && (!level || c.level === level);
        });
        if (!list.length) list = window.TYPING_CODE;
        var snippet = pick(list);
        if (snippet === lastSnippet && list.length > 1) snippet = pick(list);
        lastSnippet = snippet;
        return snippet;
    }

    // The server gives a ticket when the exercise starts; a result is only saved with it.
    function requestTicket(run) {
        if (!C.signedIn) return;
        fetch(C.startUrl, {method: 'POST', credentials: 'same-origin', headers: {'X-CSRFToken': C.csrf}})
            .then(function (r) { return r.json(); })
            .then(function (res) { if (res.ok) run.token = res.token; })
            .catch(function () { /* the result just is not saved */ });
    }

    function start() {
        var s = settings();
        var keyboardLayout = s.layout === 'en' ? 'en' : 'ru';
        clearInterval(timer);
        state = {
            mode: s.mode, layout: s.layout, lesson: s.lesson, duration: s.duration,
            charMap: buildLayout(keyboardLayout), pos: 0, errors: 0, errorAt: {},
            started: null, finished: false, code: null, keys: [], lastKey: 0, token: null, pasted: false
        };
        requestTicket(state);
        if (s.mode === 'lesson') state.text = lessonText(s.lesson, keyboardLayout, s.layout);
        else if (s.mode === 'test') state.text = testText(s.layout);
        else {
            var snippet = pickSnippet(s.codeLang, s.codeLevel);
            state.code = snippet.lang;
            state.text = snippet.text;
            state.charMap = buildLayout('en');
            keyboardLayout = 'en';
        }
        drawKeyboard(keyboardLayout);
        renderText();
        updateStats();
        $('#ty-result').hidden = true;
        $('#ty-board').hidden = false;
        $('#ty-caption').textContent = s.mode === 'lesson' ? S.lesson + ' ' + (s.lesson + 1) + ': ' + lessonTitle(s.lesson, keyboardLayout)
            : s.mode === 'test' ? S.test + ' · ' + s.duration + ' ' + S.sec
            : S.code + ' · ' + state.code;
        skipIndent();
        highlight(state.text[state.pos]);
        focus();
    }

    function focus() { input.focus({preventScroll: true}); }

    function renderText() {
        // Spans are built once; typing only changes classes.
        textEl.innerHTML = '';
        var frag = document.createDocumentFragment();
        for (var i = 0; i < state.text.length; i++) {
            var ch = state.text[i];
            var span = document.createElement('span');
            span.className = 'ty-ch';
            if (ch === '\n') { span.textContent = '↵'; span.classList.add('ty-nl'); }
            else span.textContent = ch;
            frag.appendChild(span);
            if (ch === '\n') frag.appendChild(document.createElement('br'));
        }
        textEl.appendChild(frag);
        state.spans = textEl.querySelectorAll('.ty-ch');
        mark();
    }

    function mark() {
        var spans = state.spans;
        var prev = textEl.querySelector('.ty-cur');
        if (prev) prev.classList.remove('ty-cur');
        if (state.pos < spans.length) {
            spans[state.pos].classList.add('ty-cur');
            // Keep the current line in view.
            var top = spans[state.pos].offsetTop - textEl.offsetTop;
            if (top > textEl.clientHeight - 60 || top < textEl.scrollTop) textEl.scrollTop = Math.max(0, top - 40);
        }
    }

    function skipIndent() {
        // In code the spaces at the start of a line are typed for you, like in an editor.
        if (state.mode !== 'code') return;
        while (state.pos < state.text.length && state.text[state.pos] === ' ' &&
               (state.pos === 0 || state.text[state.pos - 1] === '\n' || state.spans[state.pos - 1].classList.contains('ty-auto'))) {
            state.spans[state.pos].classList.add('ty-done', 'ty-auto');
            state.pos++;
        }
    }

    function elapsed() { return state.started ? (Date.now() - state.started) / 1000 : 0; }

    function typedChars() {
        var n = 0;
        for (var i = 0; i < state.pos; i++) if (!state.spans[i].classList.contains('ty-auto')) n++;
        return n;
    }

    function updateStats() {
        var t = elapsed();
        var chars = state.pos ? typedChars() : 0;
        var cpm = t > 1 ? Math.round(chars * 60 / t) : 0;
        var acc = chars + state.errors ? Math.round(1000 * chars / (chars + state.errors)) / 10 : 100;
        $('#ty-cpm').textContent = cpm;
        $('#ty-wpm').textContent = Math.round(cpm / 5);
        $('#ty-acc').textContent = acc + '%';
        $('#ty-err').textContent = state.errors;
        if (state.mode === 'test') {
            var left = Math.max(0, state.duration - t);
            $('#ty-time').textContent = Math.ceil(left) + ' ' + S.sec;
        } else {
            $('#ty-time').textContent = Math.floor(t) + ' ' + S.sec;
        }
    }

    function wrongLayout(ch) {
        var cyr = /[а-яёңөү]/i.test(ch);
        var lat = /[a-z]/i.test(ch);
        var expectCyr = state.layout !== 'en' && state.mode !== 'code';
        if (cyr && !expectCyr) return S.switchEn;
        if (lat && expectCyr) return S.switchRu;
        return '';
    }

    function type(ch) {
        if (state.finished || state.pos >= state.text.length) return;
        if (!state.started) {
            state.started = Date.now();
            timer = setInterval(function () {
                updateStats();
                if (state.mode === 'test' && elapsed() >= state.duration) finish();
            }, 200);
        }
        var expected = state.text[state.pos];
        var span = state.spans[state.pos];
        if (ch === expected) {
            var now = Date.now();
            state.keys.push(state.keys.length ? now - state.lastKey : 0);
            state.lastKey = now;
            span.classList.add('ty-done');
            if (state.errorAt[state.pos]) span.classList.add('ty-was-wrong');
            span.classList.remove('ty-wrong');
            state.pos++;
            press(ch, true);
            sound.key();
            $('#ty-hint').textContent = '';
            if (expected === '\n') skipIndent();
            if (state.mode === 'test' && state.text.length - state.pos < 60) appendWords();
            if (state.pos >= state.text.length) { finish(); return; }
            mark();
            highlight(state.text[state.pos]);
        } else {
            // A mistake is counted once per character; the cursor waits for the right key.
            if (!state.errorAt[state.pos]) { state.errorAt[state.pos] = true; state.errors++; }
            span.classList.add('ty-wrong');
            press(ch, false);
            sound.error();
            $('#ty-hint').textContent = wrongLayout(ch);
        }
        updateStats();
    }

    function appendWords() {
        var more = ' ' + testText(state.layout);
        var start = state.text.length;
        state.text += more;
        var frag = document.createDocumentFragment();
        for (var i = 0; i < more.length; i++) {
            var span = document.createElement('span');
            span.className = 'ty-ch';
            span.textContent = more[i];
            frag.appendChild(span);
        }
        textEl.appendChild(frag);
        state.spans = textEl.querySelectorAll('.ty-ch');
        return start;
    }

    function finish() {
        if (state.finished) return;
        state.finished = true;
        clearInterval(timer);
        var t = state.mode === 'test' ? Math.min(elapsed(), state.duration) : elapsed();
        var chars = typedChars();
        var cpm = t > 0 ? Math.round(chars * 60 / t) : 0;
        var acc = chars + state.errors ? Math.round(1000 * chars / (chars + state.errors)) / 10 : 100;
        sound.done();
        highlight(null);
        $('#ty-board').hidden = true;
        var box = $('#ty-result');
        box.hidden = false;
        $('#ty-r-cpm').textContent = cpm;
        $('#ty-r-wpm').textContent = Math.round(cpm / 5);
        $('#ty-r-acc').textContent = acc + '%';
        $('#ty-r-err').textContent = state.errors;
        $('#ty-r-time').textContent = t.toFixed(1) + ' ' + S.sec;
        var passed = state.mode !== 'lesson' || (acc >= PASS_ACC && cpm >= PASS_CPM);
        var note = '';
        if (state.mode === 'lesson') {
            note = passed ? S.lessonPassed + ' ' + '★★★'.slice(0, stars(cpm)) + '☆☆☆'.slice(stars(cpm)) : S.lessonAgain;
            if (passed && stars(cpm) < 3) note += ' ' + S.nextStar.replace('{cpm}', STARS[stars(cpm)]);
        }
        if (state.pasted) note += ' ' + S.noPaste;
        $('#ty-r-note').textContent = note;
        $('#ty-next').hidden = !(state.mode === 'lesson' && passed && state.lesson < LESSONS.length - 1);
        $('#ty-r-record').hidden = true;
        $('#ty-r-level').hidden = true;
        if (state.mode === 'lesson' && passed) {
            markDone(state.layout, state.lesson, cpm);
        }
        if (C.signedIn && chars > 0 && t >= 5) save(state, t, chars);
        else if (!C.signedIn) $('#ty-r-note').textContent += ' ' + S.signIn;
    }

    function save(run, seconds, chars) {
        if (!run.token) return;
        fetch(C.saveUrl, {
            method: 'POST', credentials: 'same-origin',
            headers: {'Content-Type': 'application/json', 'X-CSRFToken': C.csrf},
            body: JSON.stringify({mode: run.mode, layout: run.layout, seconds: seconds, chars: chars,
                                  errors: run.errors, lesson: run.mode === 'lesson' ? run.lesson : null,
                                  token: run.token, keys: run.keys})
        }).then(function (r) { return r.json(); }).then(function (res) {
            if (run !== state) return;
            if (res.ok) {
                if (res.record && run.mode !== 'lesson') $('#ty-r-record').hidden = false;
                if (res.level) showLevel(res.level, res.level_up);
            } else if (res.error === 'typed' || res.error === 'speed') {
                $('#ty-r-note').textContent = S.notCounted;
            }
        }).catch(function () { /* the result just is not saved */ });
    }

    /* ---------------- level ---------------- */

    function showLevel(info, up) {
        var box = $('#ty-level');
        if (!box || !info) return;
        box.hidden = false;
        $('#ty-level-num').textContent = info.level;
        $('#ty-level-bar').style.width = info.percent + '%';
        box.title = S.levelTitle.replace('{xp}', info.xp).replace('{next}', info.next);
        if (up) {
            var b = $('#ty-r-level');
            b.hidden = false;
            b.textContent = S.levelUp.replace('{level}', info.level);
        }
    }
    showLevel(C.level, false);

    /* ---------------- lessons list ---------------- */

    // Best speed in every passed lesson: from the server, and from this browser for guests.
    var done = {};
    function keep(k, cpm) { if (!(done[k] >= cpm)) done[k] = cpm; }
    try { JSON.parse(load('typing-done', '[]')).forEach(function (k) { keep(k, PASS_CPM); }); } catch (e) { /* ignore */ }
    try {
        var local = JSON.parse(load('typing-best', '{}'));
        Object.keys(local).forEach(function (k) { keep(k, local[k]); });
    } catch (e) { /* ignore */ }
    Object.keys(C.lessonsBest || {}).forEach(function (k) { if (C.lessonsBest[k] >= PASS_CPM) keep(k, C.lessonsBest[k]); });

    function markDone(layout, i, cpm) {
        keep(layout + ':' + i, cpm);
        store('typing-best', JSON.stringify(done));
        drawLessons();
    }

    function drawLessons() {
        var s = settings();
        var list = $('#ty-lessons');
        list.innerHTML = '';
        var kb = s.layout === 'en' ? 'en' : 'ru';
        LESSONS.forEach(function (keys, i) {
            var b = document.createElement('button');
            b.type = 'button';
            b.className = 'ty-lesson' + (i === s.lesson && s.mode === 'lesson' ? ' ty-active' : '') +
                (done[s.layout + ':' + i] ? ' ty-passed' : '');
            b.innerHTML = '<span class="ty-num"></span><span class="ty-keys"></span><span class="ty-stars"></span>';
            b.querySelector('.ty-num').textContent = i + 1;
            b.querySelector('.ty-keys').textContent = lessonTitle(i, kb);
            var n = done[s.layout + ':' + i] ? stars(done[s.layout + ':' + i]) : 0;
            b.querySelector('.ty-stars').textContent = n ? '★★★'.slice(0, n) : '';
            if (SPECIAL[keys]) b.classList.add('ty-lesson-wide');
            b.addEventListener('click', function () {
                store('typing-mode', 'lesson');
                store('typing-lesson-' + s.layout, String(i));
                syncControls();
                start();
            });
            list.appendChild(b);
        });
    }

    /* ---------------- controls ---------------- */

    function syncControls() {
        var s = settings();
        document.querySelectorAll('.ty-mode').forEach(function (b) {
            b.classList.toggle('ty-active', b.dataset.mode === s.mode);
        });
        $('#ty-layout').value = s.layout;
        $('#ty-duration').value = String(s.duration);
        $('#ty-duration').hidden = s.mode !== 'test';
        $('#ty-lessons-box').hidden = s.mode !== 'lesson';
        $('#ty-sound i').className = 'fa ' + (soundOn ? 'fa-volume-up' : 'fa-volume-off');
        $('#ty-layout').hidden = s.mode === 'code';
        $('#ty-code-lang').hidden = $('#ty-code-level').hidden = s.mode !== 'code';
        $('#ty-code-lang').value = s.codeLang;
        $('#ty-code-level').value = String(s.codeLevel);
        drawLessons();
    }

    document.querySelectorAll('.ty-mode').forEach(function (b) {
        b.addEventListener('click', function () { store('typing-mode', b.dataset.mode); syncControls(); start(); });
    });
    $('#ty-layout').addEventListener('change', function () { store('typing-layout', this.value); syncControls(); start(); });
    $('#ty-duration').addEventListener('change', function () { store('typing-duration', this.value); start(); });
    (function () {
        var langs = [];
        window.TYPING_CODE.forEach(function (c) { if (langs.indexOf(c.lang) < 0) langs.push(c.lang); });
        var select = $('#ty-code-lang');
        langs.forEach(function (l) {
            var o = document.createElement('option');
            o.value = o.textContent = l;
            select.appendChild(o);
        });
    })();
    $('#ty-code-lang').addEventListener('change', function () { store('typing-code-lang', this.value); start(); });
    $('#ty-code-level').addEventListener('change', function () { store('typing-code-level', this.value); start(); });
    $('#ty-sound').addEventListener('click', function () {
        soundOn = !soundOn;
        store('typing-sound', soundOn ? '1' : '0');
        syncControls();
        focus();
    });
    $('#ty-kbd-toggle').addEventListener('click', function () {
        var hidden = keyboardEl.classList.toggle('ty-hidden');
        store('typing-keyboard', hidden ? '0' : '1');
        focus();
    });
    if (load('typing-keyboard', '1') === '0') keyboardEl.classList.add('ty-hidden');
    $('#ty-restart').addEventListener('click', start);
    $('#ty-again').addEventListener('click', start);
    $('#ty-next').addEventListener('click', function () {
        var s = settings();
        store('typing-lesson-' + s.layout, String(Math.min(s.lesson + 1, LESSONS.length - 1)));
        syncControls();
        start();
    });

    /* ---------------- input ---------------- */

    // A hidden text field takes the keys: it works with every layout, IME and phone keyboard.
    // Only real key presses count: pasted, dropped or script-made text is thrown away.
    function cheat() {
        state.pasted = true;
        $('#ty-hint').textContent = S.noPaste;
    }
    input.addEventListener('keydown', function (e) {
        if (!e.isTrusted) { e.preventDefault(); return; }
        if ((e.ctrlKey || e.metaKey) && /^[vVмМ]$/.test(e.key)) {
            e.preventDefault();
            cheat();
            return;
        }
        if (e.key === 'Enter') { e.preventDefault(); type('\n'); }
        else if (e.key === 'Tab') { e.preventDefault(); }
        else if (e.key === 'Escape') { e.preventDefault(); start(); }
    });
    input.addEventListener('beforeinput', function (e) {
        var kind = e.inputType || '';
        if (!e.isTrusted || /^insertFrom|^insertReplacement|^insertLink/.test(kind)) {
            e.preventDefault();
            cheat();
        }
    });
    input.addEventListener('input', function (e) {
        var value = input.value;
        input.value = '';
        if (!e.isTrusted) return;
        var kind = e.inputType || 'insertText';
        if (kind !== 'insertText' && kind !== 'insertCompositionText') {
            if (/^insertFrom|^insertReplacement/.test(kind)) cheat();
            return;
        }
        // One key gives one character; a longer piece at once is a paste or a phone suggestion.
        if (value.length > 2) { cheat(); return; }
        for (var i = 0; i < value.length; i++) type(value[i]);
    });
    ['paste', 'drop', 'cut'].forEach(function (name) {
        input.addEventListener(name, function (e) { e.preventDefault(); cheat(); });
    });
    $('#ty-area').addEventListener('dragover', function (e) { e.preventDefault(); });
    $('#ty-area').addEventListener('drop', function (e) { e.preventDefault(); cheat(); });
    textEl.addEventListener('copy', function (e) { e.preventDefault(); });
    textEl.addEventListener('dragstart', function (e) { e.preventDefault(); });
    $('#ty-area').addEventListener('click', focus);
    input.addEventListener('blur', function () { $('#ty-area').classList.add('ty-unfocused'); });
    input.addEventListener('focus', function () { $('#ty-area').classList.remove('ty-unfocused'); });

    syncControls();
    start();
});
