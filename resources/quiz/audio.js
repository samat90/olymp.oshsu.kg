/* Quiz sounds and music. Everything is synthesized with the Web Audio API: no audio files.
 * window.QuizAudio: unlock, setMuted, isMuted, setVolume, getVolume, music, urgent, sfx, vibrate. */
(function () {
    'use strict';

    var AC = window.AudioContext || window.webkitAudioContext;
    var ctx = null, bus = {}, noise = null, unlocked = false;
    var muted = false, volume = 0.8;
    var want = {name: null, quiet: false}, current = null, playing = [], timer = null, isUrgent = false;
    var LOOKAHEAD = 0.12, TICK_MS = 25;

    try {
        muted = localStorage.getItem('qz-muted') === '1';
        var stored = parseFloat(localStorage.getItem('qz-volume'));
        if (stored >= 0 && stored <= 1) volume = stored;
    } catch (e) { /* storage blocked */ }

    function save(key, value) { try { localStorage.setItem(key, value); } catch (e) { /* ignore */ } }
    function noop() {}

    /* ---------------- notes ---------------- */

    var SEMI = {C: 0, D: 2, E: 4, F: 5, G: 7, A: 9, B: 11}, freqCache = {};
    function hz(name) {
        if (freqCache[name]) return freqCache[name];
        var m = /^([A-G])([#b]?)(-?\d)$/.exec(name);
        var midi = 12 * (+m[3] + 1) + SEMI[m[1]] + (m[2] === '#' ? 1 : m[2] === 'b' ? -1 : 0);
        return (freqCache[name] = 440 * Math.pow(2, (midi - 69) / 12));
    }
    // "D4 - A4 | G4 ..." -> ['D4', null, 'A4', 'G4', ...]; '-' is a rest, '|' only helps reading.
    function seq(text) {
        return text.split(/\s+/).filter(function (s) { return s && s !== '|'; })
            .map(function (s) { return s === '-' ? null : s; });
    }

    /* ---------------- engine ---------------- */

    function init() {
        if (ctx || !AC) return ctx;
        try {
            ctx = new AC();
            var comp = ctx.createDynamicsCompressor();
            comp.threshold.value = -16;
            comp.knee.value = 12;
            comp.ratio.value = 4;
            comp.attack.value = 0.004;
            comp.release.value = 0.2;
            bus.master = ctx.createGain();
            comp.connect(bus.master);
            bus.master.connect(ctx.destination);
            bus.music = ctx.createGain();
            bus.music.gain.value = 0.55;
            bus.music.connect(comp);
            bus.sfx = ctx.createGain();
            bus.sfx.gain.value = 0.9;
            bus.sfx.connect(comp);
            noise = ctx.createBuffer(1, ctx.sampleRate, ctx.sampleRate);
            var d = noise.getChannelData(0);
            for (var i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;
            applyVolume();
        } catch (e) {
            ctx = null;
        }
        return ctx;
    }

    function applyVolume() {
        if (!ctx) return;
        bus.master.gain.setTargetAtTime(muted ? 0 : volume, ctx.currentTime, 0.03);
    }

    function env(g, t, attack, peak, decay) {
        g.gain.setValueAtTime(0.0001, t);
        g.gain.linearRampToValueAtTime(peak, t + attack);
        g.gain.exponentialRampToValueAtTime(0.0001, t + attack + decay);
    }

    function filter(type, freq, q, out) {
        var f = ctx.createBiquadFilter();
        f.type = type;
        f.frequency.value = freq;
        f.Q.value = q || 0.7;
        if (out) f.connect(out);
        return f;
    }

    // One oscillator note, optional pitch glide to f2.
    function tone(type, f, t, dur, vol, out, f2, attack) {
        var o = ctx.createOscillator(), g = ctx.createGain();
        o.type = type;
        o.frequency.setValueAtTime(f, t);
        if (f2) o.frequency.exponentialRampToValueAtTime(f2, t + dur);
        env(g, t, attack || 0.005, vol, dur);
        o.connect(g);
        g.connect(out);
        o.start(t);
        o.stop(t + (attack || 0.005) + dur + 0.05);
        return o;
    }

    // Filtered noise burst; returns the filter so callers can sweep it.
    function hiss(t, dur, vol, out, type, freq, q) {
        var s = ctx.createBufferSource(), g = ctx.createGain(), f = filter(type, freq, q, g);
        s.buffer = noise;
        env(g, t, 0.002, vol, dur);
        s.connect(f);
        g.connect(out);
        s.start(t, Math.random() * 0.4);
        s.stop(t + dur + 0.05);
        return f;
    }

    function kick(t, vol, out) {
        var o = ctx.createOscillator(), g = ctx.createGain();
        o.frequency.setValueAtTime(140, t);
        o.frequency.exponentialRampToValueAtTime(44, t + 0.12);
        env(g, t, 0.002, vol, 0.3);
        o.connect(g);
        g.connect(out);
        o.start(t);
        o.stop(t + 0.35);
    }
    function hat(t, vol, out, open) { hiss(t, open ? 0.16 : 0.035, vol, out, 'highpass', 7500); }
    function snare(t, vol, out) {
        hiss(t, 0.11, vol, out, 'bandpass', 1900, 0.8);
        tone('triangle', 210, t, 0.06, vol * 0.5, out, 150);
    }

    // Karplus-Strong string: a burst of noise fed through a decaying averaging delay line.
    var ksCache = {};
    function ksBuffer(f) {
        var sr = ctx.sampleRate, n = Math.max(2, Math.floor(sr / f - 0.5));
        if (!ksCache[n]) {
            var len = Math.floor(sr * 1.4), buf = ctx.createBuffer(1, len, sr), d = buf.getChannelData(0), i, prev = 0;
            for (i = 0; i < n; i++) { var r = Math.random() * 2 - 1; d[i] = (r + prev) * 0.5; prev = r; }
            d[n] = d[0] * 0.996;
            for (i = n + 1; i < len; i++) d[i] = 0.498 * (d[i - n] + d[i - n - 1]);
            var fade = Math.floor(sr * 0.06);
            for (i = 0; i < fade; i++) d[len - 1 - i] *= i / fade;
            ksCache[n] = {buf: buf, n: n};
        }
        return {buf: ksCache[n].buf, rate: f * (n + 0.5) / sr};
    }

    // Plucked komuz-like note: two slightly detuned strings, warm low-pass, small body resonance.
    function pluck(f, t, vol, out, damp) {
        var b = ksBuffer(f), g = ctx.createGain(), body = filter('peaking', 260, 1.2, g), lp = filter('lowpass', 3000, 0.5, body);
        body.gain.value = 4;
        g.gain.value = vol;
        g.connect(out);
        for (var k = 0; k < 2; k++) {
            var s = ctx.createBufferSource();
            s.buffer = b.buf;
            s.playbackRate.value = b.rate * (k ? 1.0035 : 1);
            if (k) {
                var h = ctx.createGain();
                h.gain.value = 0.45;
                s.connect(h);
                h.connect(lp);
            } else {
                s.connect(lp);
            }
            s.start(t + k * 0.007);
        }
        if (damp) {
            g.gain.setValueAtTime(vol, t + damp);
            g.gain.exponentialRampToValueAtTime(0.0001, t + damp + 0.08);
        }
    }

    // Soft sustained drone / pad.
    function pad(f, t, dur, vol, out) {
        var g = ctx.createGain(), lp = filter('lowpass', 420, 0.6, g);
        g.gain.setValueAtTime(0.0001, t);
        g.gain.linearRampToValueAtTime(vol, t + 0.9);
        g.gain.setValueAtTime(vol, t + dur - 0.9);
        g.gain.linearRampToValueAtTime(0.0001, t + dur);
        g.connect(out);
        [-6, 6].forEach(function (cents) {
            var o = ctx.createOscillator();
            o.type = 'sawtooth';
            o.frequency.value = f;
            o.detune.value = cents;
            o.connect(lp);
            o.start(t);
            o.stop(t + dur + 0.05);
        });
    }

    function bass(f, t, dur, vol, out) {
        var g = ctx.createGain(), lp = filter('lowpass', 700, 2, g), o = ctx.createOscillator();
        lp.frequency.setValueAtTime(900, t);
        lp.frequency.exponentialRampToValueAtTime(220, t + dur);
        env(g, t, 0.005, vol, dur);
        g.connect(out);
        o.type = 'sawtooth';
        o.frequency.value = f;
        o.connect(lp);
        o.start(t);
        o.stop(t + dur + 0.05);
    }

    // Brass-like voice: detuned saws with an opening filter.
    function brass(f, t, dur, vol, out) {
        var g = ctx.createGain(), lp = filter('lowpass', 500, 1, g);
        lp.frequency.setValueAtTime(500, t);
        lp.frequency.linearRampToValueAtTime(2600, t + 0.06);
        lp.frequency.exponentialRampToValueAtTime(1200, t + dur);
        g.gain.setValueAtTime(0.0001, t);
        g.gain.linearRampToValueAtTime(vol, t + 0.03);
        g.gain.setValueAtTime(vol * 0.8, t + dur * 0.7);
        g.gain.exponentialRampToValueAtTime(0.0001, t + dur + 0.12);
        g.connect(out);
        [-7, 7].forEach(function (cents) {
            var o = ctx.createOscillator();
            o.type = 'sawtooth';
            o.frequency.value = f;
            o.detune.value = cents;
            o.connect(lp);
            o.start(t);
            o.stop(t + dur + 0.2);
        });
    }

    /* ---------------- music ---------------- */

    var LOBBY_A = seq('D4 - A4 - G4 A4 C5 A4 | G4 - F4 - D4 - - - | D4 - A4 - C5 D5 C5 A4 | G4 A4 G4 F4 G4 - - - |' +
        'A4 - C5 - D5 - C5 A4 | G4 - A4 G4 F4 - D4 - | F4 G4 A4 - G4 F4 D4 C4 | D4 - - - A3 - - -');
    var LOBBY_B = seq('F4 - F4 G4 A4 - G4 F4 | D4 - C4 - D4 - - - | A4 - A4 C5 D5 - E5 D5 | C5 - A4 - G4 - - - |' +
        'D5 - C5 A4 G4 - A4 C5 | A4 - G4 - F4 G4 A4 - | G4 F4 D4 - C4 D4 F4 G4 | D4 - - - - - - -');
    var LOBBY_ROOTS = ['D3', 'D3', 'C3', 'G2', 'F3', 'C3', 'G2', 'D3'];

    var Q_ROOTS = ['A2', 'F2', 'G2', 'E2'];
    var Q_CHORDS = [['A4', 'C5', 'E5'], ['F4', 'A4', 'C5'], ['G4', 'B4', 'D5'], ['E4', 'G#4', 'B4']];
    var Q_ARP = {2: 0, 5: 1, 7: 2, 10: 1, 13: 2, 15: 0};
    var Q_BASS = {0: 1, 3: 1, 6: 1, 8: 1, 10: 2, 14: 1};

    var TRACKS = {
        lobby: {
            bpm: 96, div: 2,
            play: function (c, t, sd, out) {
                var s = c % 128, mel = s < 64 ? LOBBY_A : LOBBY_B, i = s % 64, pos = i % 8, root = LOBBY_ROOTS[i >> 3];
                if (mel[i]) pluck(hz(mel[i]), t, 0.55, out);
                if (pos === 0 || pos === 3 || pos === 6) pluck(hz(root), t, pos ? 0.22 : 0.3, out, sd * 2.5);
                if (pos === 2 || pos === 5) pluck(hz(root) * 1.5, t, 0.15, out, sd * 1.5);
                if (i % 16 === 0) {
                    pad(hz('D2'), t, sd * 16 + 0.8, 0.05, out);
                    pad(hz('A2'), t, sd * 16 + 0.8, 0.035, out);
                }
            }
        },
        question: {
            bpm: 124, div: 4, urgent: 1.22,
            play: function (c, t, sd, out) {
                var bar = (c >> 4) % 4, pos = c % 16, chord = Q_CHORDS[bar];
                if (pos % 8 === 0 || (isUrgent && pos % 4 === 0) || (bar === 3 && pos === 11)) kick(t, 0.75, out);
                if (pos === 4 || pos === 12) snare(t, 0.32, out);
                if (pos % 2 === 0 || isUrgent) hat(t, pos % 4 === 2 ? 0.16 : 0.07, out, pos === 14 && bar === 3);
                if (Q_BASS[pos]) bass(hz(Q_ROOTS[bar]) * Q_BASS[pos], t, sd * 1.6, 0.32, out);
                if (Q_ARP[pos] !== undefined) pluck(hz(chord[Q_ARP[pos]]) * (pos === 15 ? 2 : 1), t, 0.3, out, sd * 2);
                if (isUrgent && pos % 2 === 0) tone('square', hz(pos % 4 ? 'E5' : 'E6'), t, 0.05, 0.04, out);
            }
        },
        board: {
            bpm: 100, div: 8,
            play: function (c, t, sd, out) {
                var ROLL = 40;
                if (c < ROLL) {
                    var k = c / ROLL;
                    snare(t, (0.05 + 0.4 * k * k) * (0.8 + Math.random() * 0.3), out);
                    if (c % 8 === 0) tone('sine', 90, t, 0.25, 0.25 + 0.3 * k, out, 60);
                } else if (c === ROLL) {
                    kick(t, 0.9, out);
                    hiss(t, 1.4, 0.3, out, 'highpass', 4500);
                    bass(hz('C2'), t, 0.8, 0.4, out);
                } else {
                    var p = (c - ROLL) % 32;
                    if (p === 0 || p === 20) kick(t, 0.35, out);
                    if (p % 8 === 4) hat(t, 0.05, out);
                    if (p === 16 || p === 24) tone('sine', p === 16 ? 160 : 120, t, 0.18, 0.14, out, 90);
                }
            }
        }
    };

    function stepDur(p) {
        return 60 / (p.def.bpm * (isUrgent && p.def.urgent ? p.def.urgent : 1)) / p.def.div;
    }

    // Lookahead scheduler: a coarse timer queues notes slightly ahead on the precise audio clock.
    function schedule() {
        if (!ctx) return;
        var now = ctx.currentTime;
        playing = playing.filter(function (p) {
            if (p.end && p.end <= now) {
                try { p.out.disconnect(); } catch (e) { /* ignore */ }
                return false;
            }
            return true;
        });
        playing.forEach(function (p) {
            if (p.next < now - 0.25) p.next = now + 0.03;   // back from a pause
            while (p.next < now + LOOKAHEAD && (!p.end || p.next < p.end)) {
                try { p.def.play(p.count, p.next, stepDur(p), p.out); } catch (e) { /* keep going */ }
                p.count += 1;
                p.next += stepDur(p);
            }
        });
        if (!playing.length && timer) {
            clearInterval(timer);
            timer = null;
        }
    }

    function fadeTo(param, value, seconds) {
        var now = ctx.currentTime;
        param.cancelScheduledValues(now);
        param.setValueAtTime(Math.max(param.value, 0.0001), now);
        param.linearRampToValueAtTime(Math.max(value, 0.0001), now + seconds);
    }

    function startMusic() {
        if (!ctx) return;
        var level = want.quiet ? 0.28 : 1;
        if (current && current.name === want.name) {
            fadeTo(current.out.gain, level, 0.4);
            return;
        }
        if (current) {
            fadeTo(current.out.gain, 0.0001, want.name ? 0.8 : 1.2);
            current.end = ctx.currentTime + (want.name ? 0.85 : 1.25);
            current = null;
        }
        isUrgent = false;
        if (!want.name || !TRACKS[want.name]) return;
        var out = ctx.createGain();
        out.gain.value = 0.0001;
        out.connect(bus.music);
        current = {name: want.name, def: TRACKS[want.name], out: out, count: 0, next: ctx.currentTime + 0.06, end: 0};
        fadeTo(out.gain, level, 0.6);
        playing.push(current);
        if (!timer) timer = setInterval(schedule, TICK_MS);
        schedule();
    }

    /* ---------------- effects ---------------- */

    var SFX = {
        tick: function (t, o) {
            tone('sine', 1250, t, 0.05, 0.3, o);
            hiss(t, 0.02, 0.12, o, 'bandpass', 3200, 2);
        },
        go: function (t, o) {
            ['G4', 'C5', 'E5'].forEach(function (n, i) { tone('triangle', hz(n), t + i * 0.06, 0.12, 0.25, o); });
            ['C5', 'E5', 'G5', 'C6'].forEach(function (n) { tone('triangle', hz(n), t + 0.18, 0.5, 0.14, o); });
            hiss(t, 0.35, 0.08, o, 'bandpass', 2500, 1).frequency.exponentialRampToValueAtTime(7000, t + 0.3);
        },
        join: function (t, o) {
            var notes = ['D5', 'F5', 'G5', 'A5', 'C6'];
            pluck(hz(notes[Math.floor(Math.random() * notes.length)]), t, 0.5, o);
        },
        answer: function (t, o) {
            tone('triangle', 660, t, 0.07, 0.25, o);
            tone('triangle', 990, t + 0.055, 0.12, 0.22, o);
        },
        correct: function (t, o) {
            tone('triangle', hz('G5'), t, 0.12, 0.32, o);
            tone('triangle', hz('D6'), t + 0.09, 0.32, 0.32, o);
            tone('sine', hz('D7'), t + 0.09, 0.25, 0.06, o);
        },
        wrong: function (t, o) {
            var lp = filter('lowpass', 900, 0.7, o);
            tone('triangle', hz('Bb3'), t, 0.16, 0.35, lp);
            tone('triangle', hz('F3'), t + 0.13, 0.35, 0.35, lp, hz('E3'));
        },
        reveal: function (t, o) {
            hiss(t, 0.45, 0.12, o, 'bandpass', 500, 1.5).frequency.exponentialRampToValueAtTime(5000, t + 0.4);
            ['D4', 'A4', 'D5', 'F5'].forEach(function (n, i) { pluck(hz(n), t + 0.32 + i * 0.03, 0.35, o); });
        },
        fanfare: function (t, o) {
            [['G4', 0], ['A4', 0.11], ['B4', 0.22]].forEach(function (x) { brass(hz(x[0]), t + x[1], 0.08, 0.16, o); });
            ['C4', 'E4', 'G4', 'C5'].forEach(function (n) { brass(hz(n), t + 0.34, 0.3, 0.12, o); });
            ['F4', 'A4', 'C5'].forEach(function (n) { brass(hz(n), t + 0.7, 0.14, 0.12, o); });
            ['C4', 'G4', 'C5', 'E5', 'G5'].forEach(function (n) { brass(hz(n), t + 0.88, 0.9, 0.11, o); });
            kick(t + 0.34, 0.5, o);
            kick(t + 0.88, 0.7, o);
            hiss(t + 0.88, 1.2, 0.12, o, 'highpass', 5000);
        },
        streak: function (t, o) {
            ['D5', 'F5', 'A5', 'C6', 'D6'].forEach(function (n, i) { pluck(hz(n), t + i * 0.045, 0.32, o); });
            tone('sine', hz('A6'), t + 0.22, 0.3, 0.05, o);
        },
        tap: function (t, o) { tone('sine', 540, t, 0.03, 0.18, o, 420); }
    };

    /* ---------------- unlock, visibility ---------------- */

    function unlock() {
        if (!AC) return;
        try {
            if (!init()) return;
            if (ctx.state !== 'running' && !document.hidden) {
                var p = ctx.resume();
                if (p && p.catch) p.catch(noop);
            }
            if (!unlocked) {
                unlocked = true;
                var s = ctx.createBufferSource();      // silent blip: needed by older iOS Safari
                s.buffer = ctx.createBuffer(1, 1, ctx.sampleRate);
                s.connect(ctx.destination);
                s.start(0);
                if (want.name) startMusic();
            }
        } catch (e) { /* no audio */ }
    }

    ['pointerdown', 'keydown', 'touchend'].forEach(function (type) {
        window.addEventListener(type, unlock, {capture: true, passive: true});
    });

    document.addEventListener('visibilitychange', function () {
        if (!ctx) return;
        try {
            var p = document.hidden ? ctx.suspend() : (unlocked ? ctx.resume() : null);
            if (p && p.catch) p.catch(noop);
        } catch (e) { /* ignore */ }
    });

    window.QuizAudio = {
        available: !!AC,
        unlock: unlock,
        isMuted: function () { return muted; },
        setMuted: function (on) {
            muted = !!on;
            save('qz-muted', muted ? '1' : '0');
            try { applyVolume(); } catch (e) { /* ignore */ }
        },
        getVolume: function () { return volume; },
        setVolume: function (v) {
            v = Math.max(0, Math.min(1, +v || 0));
            volume = v;
            save('qz-volume', String(v));
            try { applyVolume(); } catch (e) { /* ignore */ }
        },
        music: function (name, opts) {
            want = {name: name || null, quiet: !!(opts && opts.quiet)};
            try { if (ctx && unlocked) startMusic(); } catch (e) { /* ignore */ }
        },
        urgent: function (on) { isUrgent = !!on && !!current && current.name === 'question'; },
        sfx: function (name) {
            if (!ctx || !unlocked || muted || !SFX[name]) return;
            try { SFX[name](ctx.currentTime + 0.01, bus.sfx); } catch (e) { /* ignore */ }
        },
        vibrate: function (pattern) {
            if (muted || !navigator.vibrate) return false;
            try { return navigator.vibrate(pattern); } catch (e) { return false; }
        }
    };
})();
