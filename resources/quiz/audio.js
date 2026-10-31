/* Quiz sounds and music. Everything is synthesized with the Web Audio API: no audio files.
 * Instruments: drum kit (kick, snare, claps, hats, crash, toms, epic booms), synth and acoustic basses,
 * piano, electric piano, supersaw, chiptune, brass, strings, choir, organ, bells, guitar; a hall reverb.
 * Repertoire: public-domain melodies only (classical composers and traditional folk tunes, authors died
 * more than 70 years ago), in modern arrangements: epic, rock, EDM, disco, pop, lo-fi, 8-bit, swing, latin.
 * window.QuizAudio: unlock, setMuted, isMuted, setVolume, getVolume, music, urgent, sfx, vibrate, state,
 * beat (0..1 pulse of the current kick, for visuals), tracks (titles). */
(function () {
    'use strict';

    var AC = window.AudioContext || window.webkitAudioContext;
    var ctx = null, bus = {}, noise = null, unlocked = false, curve = null, pulseWave = null;
    var muted = false, volume = 0.8;
    var want = {name: null, quiet: false, variant: null}, current = null, playing = [], timer = null;
    var lastVariant = {}, beats = [], errors = 0;
    var LOOKAHEAD = 0.12, TICK_MS = 25;

    try {
        muted = localStorage.getItem('qz-muted') === '1';
        var stored = parseFloat(localStorage.getItem('qz-volume'));
        if (stored >= 0 && stored <= 1) volume = stored;
    } catch (e) { /* storage blocked */ }

    function save(key, value) { try { localStorage.setItem(key, value); } catch (e) { /* ignore */ } }
    function noop() {}

    /* ---------------- notes, chords, random ---------------- */

    function mhz(m) { return 440 * Math.pow(2, (m - 69) / 12); }

    function rng(seed) {
        return function () {
            seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0;
            return seed / 4294967296;
        };
    }
    function hash(n) {
        n = Math.imul(n ^ 0x9e3779b9, 0x85ebca6b);
        n ^= n >>> 13;
        n = Math.imul(n, 0xc2b2ae35);
        return ((n ^ (n >>> 16)) >>> 0) / 4294967296;
    }

    // Melody, one token per step: note name "c", "f#", "eb" in octave 4 (c = middle C); ' raises and
    // , lowers an octave; '-' holds the note, '.' is a rest. len = how many steps each note lasts.
    var SEMI = {c: 0, d: 2, e: 4, f: 5, g: 7, a: 9, b: 11};
    function parseMel(text) {
        var out = {note: [], fresh: [], len: []}, last = null;
        text.split(/[\s|]+/).forEach(function (s) {
            if (!s) return;
            var isNew = s !== '-' && s !== '.', j = 1;
            if (s === '.') last = null;
            else if (isNew) {
                last = 60 + SEMI[s.charAt(0)];
                if (s.charAt(1) === '#') { last += 1; j = 2; } else if (s.charAt(1) === 'b' && s.length > 1) { last -= 1; j = 2; }
                for (; j < s.length; j++) last += s.charAt(j) === "'" ? 12 : -12;
            }
            out.note.push(last);
            out.fresh.push(isNew && last !== null);
        });
        for (var i = out.note.length - 1; i >= 0; i--) {
            var k = i + 1, cont = k < out.note.length && !out.fresh[k] && out.note[k] !== null && out.note[i] !== null;
            out.len[i] = 1 + (cont ? out.len[k] : 0);
        }
        return out;
    }

    var QUAL = {'': [0, 4, 7], m: [0, 3, 7], '5': [0, 7], '7': [0, 4, 7, 10], m7: [0, 3, 7, 10], M7: [0, 4, 7, 11],
        dim: [0, 3, 6], sus: [0, 5, 7]};
    // "Bm", "F#7", "GM7", "C5" -> root (A2..G#3) and intervals.
    function chord(sym) {
        var m = /^([A-G])([#b]?)(m7|M7|m|5|7|dim|sus)?$/.exec(sym);
        if (!m) throw new Error('chord ' + sym);
        var r = 48 + SEMI[m[1].toLowerCase()] + (m[2] === '#' ? 1 : m[2] === 'b' ? -1 : 0);
        if (r > 56) r -= 12;
        return {r: r, iv: QUAL[m[3] || '']};
    }
    // Chord tones placed in [lo, lo + 12), sorted: a close voicing.
    function voice(cd, lo) {
        return cd.iv.map(function (i) {
            var n = cd.r + i;
            while (n < lo) n += 12;
            while (n >= lo + 12) n -= 12;
            return n;
        }).sort(function (a, b) { return a - b; });
    }

    /* ---------------- engine ---------------- */

    function init() {
        if (ctx || !AC) return ctx;
        try {
            ctx = new AC();
            var comp = ctx.createDynamicsCompressor();
            comp.threshold.value = -12;
            comp.knee.value = 8;
            comp.ratio.value = 5;
            comp.attack.value = 0.003;
            comp.release.value = 0.18;
            bus.master = ctx.createGain();
            comp.connect(bus.master);
            bus.master.connect(ctx.destination);
            bus.comp = comp;
            bus.verb = ctx.createConvolver();
            bus.verb.buffer = hall(2.4);
            var wet = ctx.createGain();
            wet.gain.value = 0.32;
            bus.verb.connect(wet);
            wet.connect(comp);
            bus.music = ctx.createGain();
            bus.music.gain.value = 0.55;
            bus.music.connect(comp);
            bus.sfx = ctx.createGain();
            bus.sfx.gain.value = 0.9;
            bus.sfx.connect(comp);
            bus.sfxv = ctx.createGain();          // effects that ring in the hall
            bus.sfxv.connect(bus.sfx);
            send(bus.sfxv, 0.5);
            noise = ctx.createBuffer(1, ctx.sampleRate, ctx.sampleRate);
            var d = noise.getChannelData(0), r = rng(7);
            for (var i = 0; i < d.length; i++) d[i] = r() * 2 - 1;
            curve = new Float32Array(1024);
            for (i = 0; i < 1024; i++) { var x = i / 511.5 - 1; curve[i] = Math.tanh(x * 4) / Math.tanh(4); }
            var re = new Float32Array(40), im = new Float32Array(40);
            for (i = 1; i < 40; i++) re[i] = 2 / (i * Math.PI) * Math.sin(i * Math.PI * 0.25);
            pulseWave = ctx.createPeriodicWave(re, im);
            applyVolume();
        } catch (e) {
            ctx = null;
        }
        return ctx;
    }

    // Stereo hall impulse: decaying noise that gets darker as it fades.
    function hall(sec) {
        var sr = ctx.sampleRate, len = Math.floor(sr * sec), buf = ctx.createBuffer(2, len, sr);
        for (var c = 0; c < 2; c++) {
            var d = buf.getChannelData(c), r = rng(11 + c * 97), lp = 0;
            for (var i = 0; i < len; i++) {
                var k = i / len, a = 0.15 + 0.8 * k;
                lp += (r() * 2 - 1 - lp) * (1 - a);
                d[i] = (i < sr * 0.012 ? 0 : lp) * Math.pow(1 - k, 2.6);
            }
        }
        return buf;
    }

    function send(node, amount) {
        var g = ctx.createGain();
        g.gain.value = amount;
        node.connect(g);
        g.connect(bus.verb);
        return g;
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
    // Attack, sustain, release; safe for very short notes.
    function hold(g, t, dur, vol, att, rel) {
        att = Math.min(att, dur * 0.4);
        rel = Math.min(rel, dur * 0.5);
        g.gain.setValueAtTime(0.0001, t);
        g.gain.linearRampToValueAtTime(vol, t + att);
        g.gain.setValueAtTime(vol, t + dur - rel);
        g.gain.linearRampToValueAtTime(0.0001, t + dur);
    }
    function gain(out, v) {
        var g = ctx.createGain();
        g.gain.value = v === undefined ? 1 : v;
        g.connect(out);
        return g;
    }
    function filter(type, freq, q, out) {
        var f = ctx.createBiquadFilter();
        f.type = type;
        f.frequency.value = freq;
        f.Q.value = q || 0.7;
        if (out) f.connect(out);
        return f;
    }
    function osc(type, f, t, end, out, detune) {
        var o = ctx.createOscillator();
        if (type === 'pulse') o.setPeriodicWave(pulseWave);
        else o.type = type;
        o.frequency.value = f;
        if (detune) o.detune.value = detune;
        o.connect(out);
        o.start(t);
        o.stop(end);
        return o;
    }
    function tone(type, f, t, dur, vol, out, f2, attack) {
        var g = ctx.createGain(), o = osc(type, f, t, t + (attack || 0.005) + dur + 0.05, g);
        o.frequency.setValueAtTime(f, t);
        if (f2) o.frequency.exponentialRampToValueAtTime(f2, t + dur);
        env(g, t, attack || 0.005, vol, dur);
        g.connect(out);
        return o;
    }
    function hiss(t, dur, vol, out, type, freq, q, attack) {
        var s = ctx.createBufferSource(), g = ctx.createGain(), f = filter(type, freq, q, g);
        s.buffer = noise;
        env(g, t, attack || 0.002, vol, dur);
        s.connect(f);
        g.connect(out);
        s.start(t, (t * 7.31) % 0.5);
        s.stop(t + (attack || 0.002) + dur + 0.05);
        return f;
    }
    function vib(o, t, f, depth, rate, delay, end) {
        var lfo = ctx.createOscillator(), lg = ctx.createGain();
        lfo.frequency.value = rate;
        lg.gain.setValueAtTime(0, t);
        lg.gain.linearRampToValueAtTime(f * depth, t + delay);
        lfo.connect(lg);
        lg.connect(o.frequency);
        lfo.start(t);
        lfo.stop(end);
    }
    function riser(t, dur, vol, out, f0, f1) {
        var s = ctx.createBufferSource(), g = ctx.createGain(), f = filter('bandpass', f0 || 400, 2.2, g);
        s.buffer = noise;
        s.loop = true;
        f.frequency.setValueAtTime(f0 || 400, t);
        f.frequency.exponentialRampToValueAtTime(f1 || 7000, t + dur);
        g.gain.setValueAtTime(0.0001, t);
        g.gain.exponentialRampToValueAtTime(vol, t + dur);
        g.gain.linearRampToValueAtTime(0.0001, t + dur + 0.05);
        s.connect(f);
        g.connect(out);
        s.start(t);
        s.stop(t + dur + 0.08);
    }

    /* ---------------- drums ---------------- */

    function kick(t, v, o) {
        var g = ctx.createGain(), s = osc('sine', 160, t, t + 0.45, g);
        s.frequency.setValueAtTime(165, t);
        s.frequency.exponentialRampToValueAtTime(48, t + 0.09);
        env(g, t, 0.002, v, 0.38);
        g.connect(o);
        hiss(t, 0.008, v * 0.35, o, 'highpass', 2500);
        beats.push({t: t, v: Math.min(1, v * 1.2)});
    }
    function snare(t, v, o) {
        tone('triangle', 230, t, 0.08, v * 0.55, o, 160, 0.001);
        hiss(t, 0.16, v * 0.8, o, 'highpass', 1700, 0.6);
        hiss(t, 0.05, v * 0.4, o, 'bandpass', 4200, 1);
    }
    function clap(t, v, o) {
        hiss(t, 0.02, v, o, 'bandpass', 1300, 0.9);
        hiss(t + 0.011, 0.02, v * 0.9, o, 'bandpass', 1300, 0.9);
        hiss(t + 0.022, 0.14, v * 0.8, o, 'bandpass', 1250, 0.9);
    }
    function hat(t, v, o, open) { hiss(t, open ? 0.22 : 0.035, v, o, 'highpass', open ? 7000 : 8200, 0.8); }
    function crash(t, v, o, len) {
        hiss(t, len || 1.5, v, o, 'highpass', 5200, 0.5);
        hiss(t, (len || 1.5) * 0.4, v * 0.6, o, 'bandpass', 8500, 1.4);
    }
    function rim(t, v, o) {
        tone('triangle', 820, t, 0.022, v, o, 0, 0.001);
        hiss(t, 0.018, v * 0.6, o, 'bandpass', 2600, 4);
    }
    function tom(t, f, v, o) {
        var g = ctx.createGain(), s = osc('sine', f, t, t + 0.5, g);
        s.frequency.setValueAtTime(f * 1.7, t);
        s.frequency.exponentialRampToValueAtTime(f, t + 0.07);
        env(g, t, 0.002, v, 0.4);
        g.connect(o);
        hiss(t, 0.04, v * 0.3, o, 'lowpass', 2400);
    }
    // Big cinematic drum: low membrane, sub tail and a skin slap.
    function boom(t, v, o) {
        var g = ctx.createGain(), s = osc('sine', 110, t, t + 1.3, g);
        s.frequency.setValueAtTime(115, t);
        s.frequency.exponentialRampToValueAtTime(40, t + 0.4);
        env(g, t, 0.003, v, 1.0);
        g.connect(o);
        tone('sine', 52, t, 1.2, v * 0.45, o, 44, 0.01);
        hiss(t, 0.22, v * 0.5, o, 'lowpass', 600, 0.8);
        hiss(t, 0.03, v * 0.25, o, 'bandpass', 1800, 1);
        beats.push({t: t, v: Math.min(1, v * 1.1)});
    }
    function shaker(t, v, o) { hiss(t, 0.05, v, o, 'bandpass', 7200, 1.4, 0.012); }
    function conga(t, f, v, o) {
        tone('sine', f, t, 0.22, v, o, f * 0.85, 0.002);
        hiss(t, 0.02, v * 0.3, o, 'bandpass', 3000, 2);
    }
    function wood(t, f, v, o) {
        tone('sine', f, t, 0.06, v, o, 0, 0.001);
        tone('sine', f * 2.7, t, 0.02, v * 0.4, o, 0, 0.001);
    }

    /* ---------------- melodic instruments ---------------- */

    // Karplus-Strong string (pizzicato, guitar, harp), rendered once per period into a small buffer.
    var KS_SR = 22050, ksCache = {};
    function ksBuffer(f) {
        var n = Math.max(4, Math.floor(KS_SR / f - 0.5)), c = ksCache[n];
        if (!c) {
            var len = Math.floor(KS_SR * 1.4), buf = ctx.createBuffer(1, len, KS_SR), d = buf.getChannelData(0),
                r = rng(n * 7919), i, lp = 0, peak = 0, loss = Math.pow(0.001, 1 / (1.3 * f));
            for (i = 0; i < n; i++) { lp += (r() * 2 - 1 - lp) * 0.6; d[i] = lp; }
            for (i = 0; i < n; i++) peak = Math.max(peak, Math.abs(d[i]));
            for (i = 0; i < n; i++) d[i] *= 0.9 / (peak || 1);
            d[n] = loss * 0.5 * (d[0] + d[n - 1]);
            for (i = n + 1; i < len; i++) d[i] = loss * 0.5 * (d[i - n] + d[i - n - 1]);
            var fade = Math.floor(KS_SR * 0.1);
            for (i = 0; i < fade; i++) d[len - 1 - i] *= i / fade;
            c = ksCache[n] = {buf: buf, n: n};
        }
        return {buf: c.buf, rate: f * (c.n + 0.5) / KS_SR};
    }
    function string(f, t, dur, vol, out) {
        var b = ksBuffer(f), s = ctx.createBufferSource(), g = ctx.createGain(), end = t + Math.min(1.3, dur + 0.25);
        s.buffer = b.buf;
        s.playbackRate.value = b.rate;
        g.gain.setValueAtTime(0, t);
        g.gain.linearRampToValueAtTime(vol, t + 0.003);
        g.gain.setValueAtTime(vol, end - 0.1);
        g.gain.linearRampToValueAtTime(0.0001, end);
        s.connect(g);
        g.connect(out);
        s.start(t);
        s.stop(end + 0.02);
    }

    var I = {};
    I.piano = function (f, t, dur, vol, out) {
        var dec = Math.min(2.2, 1.6 * Math.pow(262 / f, 0.35)), end = t + Math.max(0.25, dur) + 0.18,
            P = [1, 0.45, 0.22, 0.12, 0.06], g = ctx.createGain();
        g.gain.setValueAtTime(1, t);
        g.gain.setValueAtTime(1, end - 0.16);
        g.gain.linearRampToValueAtTime(0.0001, end);
        g.connect(out);
        P.forEach(function (a, k) {
            var pg = ctx.createGain();
            env(pg, t, 0.002, vol * a, dec / (1 + 0.7 * k));
            pg.connect(g);
            if (f * (k + 1) < 16000) osc(k ? 'sine' : 'triangle', f * (k + 1) * (1 + 0.0007 * k * k), t, end + 0.02, pg);
        });
        hiss(t, 0.012, vol * 0.25, out, 'bandpass', Math.min(9000, f * 6), 1.2);
    };
    I.epiano = function (f, t, dur, vol, out) {
        var g = ctx.createGain(), mg = ctx.createGain(), end = t + Math.max(0.3, dur) + 0.25,
            c = osc('sine', f, t, end, g), m = osc('sine', f, t, end, mg);
        mg.gain.setValueAtTime(f * 1.8, t);
        mg.gain.exponentialRampToValueAtTime(f * 0.15, t + 0.5);
        mg.connect(c.frequency);
        g.gain.setValueAtTime(0.0001, t);
        g.gain.linearRampToValueAtTime(vol, t + 0.004);
        g.gain.exponentialRampToValueAtTime(vol * 0.35, t + 0.6);
        g.gain.setValueAtTime(vol * 0.35, end - 0.2);
        g.gain.linearRampToValueAtTime(0.0001, end);
        g.connect(out);
        tone('sine', f * 4.02, t, 0.25, vol * 0.12, out, 0, 0.002);
        void m;
    };
    I.bell = function (f, t, dur, vol, out) {
        [[1, 1, 1.6], [2.76, 0.45, 0.6], [5.4, 0.22, 0.3], [8.93, 0.1, 0.15]].forEach(function (p) {
            if (f * p[0] < 16000) tone('sine', f * p[0], t, p[2], vol * p[1], out, 0, 0.001);
        });
    };
    I.mallet = function (f, t, dur, vol, out) {
        tone('sine', f, t, 0.5, vol, out, 0, 0.003);
        tone('sine', f * 3.99, t, 0.11, vol * 0.25, out, 0, 0.002);
        if (f < 1600) tone('sine', f * 9.8, t, 0.03, vol * 0.06, out, 0, 0.001);
    };
    I.pluck = function (f, t, dur, vol, out) {
        var g = ctx.createGain(), lp = filter('lowpass', 3000, 2, g), end = t + 0.45;
        lp.frequency.setValueAtTime(Math.min(9000, f * 9), t);
        lp.frequency.exponentialRampToValueAtTime(Math.max(300, f * 1.2), t + 0.3);
        env(g, t, 0.002, vol, 0.4);
        g.connect(out);
        osc('sawtooth', f, t, end, lp, -6);
        osc('sawtooth', f, t, end, lp, 6);
    };
    I.saw = function (f, t, dur, vol, out) {     // supersaw lead
        var g = ctx.createGain(), lp = filter('lowpass', 4000, 0.9, g), end = t + dur + 0.08;
        lp.frequency.setValueAtTime(Math.min(10000, f * 3), t);
        lp.frequency.linearRampToValueAtTime(Math.min(12000, f * 8), t + 0.04);
        lp.frequency.setTargetAtTime(Math.min(9000, f * 5), t + 0.05, 0.2);
        hold(g, t, dur + 0.05, vol, 0.008, 0.06);
        g.connect(out);
        [-14, -6, 0, 6, 14].forEach(function (d, i) {
            var o = osc('sawtooth', f, t, end, lp, d);
            if (i === 2 && dur > 0.35) vib(o, t, f, 0.004, 5.5, 0.3, end);
        });
    };
    I.square = function (f, t, dur, vol, out) {  // 8-bit lead: 25% pulse
        var g = ctx.createGain(), o = osc('pulse', f, t, t + dur + 0.04, g);
        if (dur > 0.3) vib(o, t, f, 0.006, 6, 0.2, t + dur + 0.04);
        hold(g, t, Math.max(0.05, dur * 0.92), vol, 0.002, 0.02);
        g.connect(out);
    };
    I.brass = function (f, t, dur, vol, out) {
        var g = ctx.createGain(), lp = filter('lowpass', 400, 1.1, g), end = t + dur + 0.08;
        lp.frequency.setValueAtTime(350, t);
        lp.frequency.linearRampToValueAtTime(Math.min(6000, f * 7), t + 0.06);
        lp.frequency.setTargetAtTime(Math.min(4500, f * 4), t + 0.08, 0.25);
        hold(g, t, dur + 0.04, vol, 0.03, 0.08);
        g.connect(out);
        [-7, 7].forEach(function (d) {
            var o = osc('sawtooth', f, t, end, lp, d);
            o.frequency.setValueAtTime(f * 0.985, t);
            o.frequency.linearRampToValueAtTime(f, t + 0.05);
        });
    };
    I.strings = function (f, t, dur, vol, out) {
        var g = ctx.createGain(), lp = filter('lowpass', 3200, 0.7, g), end = t + dur + 0.25, att = Math.min(0.12, dur * 0.3);
        g.gain.setValueAtTime(0.0001, t);
        g.gain.linearRampToValueAtTime(vol, t + att);
        g.gain.setValueAtTime(vol, t + dur);
        g.gain.linearRampToValueAtTime(0.0001, t + dur + 0.2);
        g.connect(out);
        [-9, 0, 9].forEach(function (d, i) {
            var o = osc('sawtooth', f, t, end, lp, d);
            if (i === 1 && dur > 0.3) vib(o, t, f, 0.005, 5.2, 0.25, end);
        });
    };
    I.pizz = function (f, t, dur, vol, out) { string(f, t, Math.min(dur, 0.35), vol * 1.6, out); };
    I.harp = function (f, t, dur, vol, out) { string(f, t, 1.2, vol * 1.4, out); };
    I.guitar = function (f, t, dur, vol, out) {   // overdriven lead guitar
        var ws = ctx.createWaveShaper(), pre = ctx.createGain(), g = ctx.createGain(), lp = filter('lowpass', 3200, 0.8, g),
            end = t + dur + 0.1;
        ws.curve = curve;
        pre.gain.value = 3;
        pre.connect(ws);
        ws.connect(lp);
        hold(g, t, dur + 0.06, vol, 0.004, 0.06);
        g.connect(out);
        var o = osc('sawtooth', f, t, end, pre, -5);
        osc('sawtooth', f * 1.002, t, end, pre, 5);
        if (dur > 0.3) vib(o, t, f, 0.008, 5.8, 0.2, end);
    };
    I.organ = function (f, t, dur, vol, out) {
        var g = ctx.createGain(), lp = filter('lowpass', 3000, 0.7, g), h = gain(g, 0.55), end = t + dur + 0.06;
        hold(g, t, dur + 0.04, vol, 0.012, 0.05);
        g.connect(out);
        osc('square', f, t, end, lp);
        osc('sine', f * 2, t, end, h);
        osc('sine', f * 3, t, end, h);
        osc('sine', f * 0.5, t, end, h);
    };
    I.flute = function (f, t, dur, vol, out) {
        var g = ctx.createGain(), end = t + dur + 0.1;
        hold(g, t, dur + 0.05, vol, 0.06, 0.08);
        g.connect(out);
        vib(osc('sine', f, t, end, g), t, f, 0.006, 5, 0.25, end);
        osc('triangle', f * 2, t, end, gain(g, 0.12));
        hiss(t, Math.min(0.2, dur), vol * 0.25, out, 'bandpass', f * 2, 3);
    };
    I.choir = function (f, t, dur, vol, out) {
        var g = ctx.createGain(), mix = ctx.createGain(), end = t + dur + 0.35;
        mix.connect(filter('bandpass', 750, 2.5, g));
        mix.connect(filter('bandpass', 1150, 3.5, g));
        mix.connect(filter('lowpass', 500, 0.7, g));
        g.gain.setValueAtTime(0.0001, t);
        g.gain.linearRampToValueAtTime(vol, t + Math.min(0.18, dur * 0.4));
        g.gain.setValueAtTime(vol, t + dur);
        g.gain.linearRampToValueAtTime(0.0001, t + dur + 0.3);
        g.connect(out);
        [-10, 0, 10].forEach(function (d, i) {
            var o = osc('sawtooth', f, t, end, mix, d);
            if (i === 1) vib(o, t, f, 0.006, 4.8, 0.2, end);
        });
    };

    // Basses: root note in MIDI (the caller already chose the octave).
    var BASS = {
        synth: function (m, t, dur, vol, out) {
            var f = mhz(m), g = ctx.createGain(), lp = filter('lowpass', 800, 3, g), end = t + dur + 0.06;
            lp.frequency.setValueAtTime(1600, t);
            lp.frequency.exponentialRampToValueAtTime(260, t + Math.min(0.3, dur + 0.05));
            hold(g, t, dur + 0.03, vol, 0.004, 0.04);
            g.connect(out);
            osc('sawtooth', f, t, end, lp);
            osc('sine', f / 2, t, end, gain(g, 0.9));
        },
        sub: function (m, t, dur, vol, out) {
            var g = ctx.createGain(), end = t + dur + 0.06;
            hold(g, t, dur + 0.03, vol * 1.3, 0.006, 0.05);
            g.connect(out);
            osc('sine', mhz(m), t, end, g);
            osc('triangle', mhz(m + 12), t, end, gain(g, 0.15));
        },
        chip: function (m, t, dur, vol, out) {
            var g = ctx.createGain();
            hold(g, t, Math.max(0.05, dur * 0.85), vol * 1.2, 0.002, 0.02);
            g.connect(out);
            osc('triangle', mhz(m + 12), t, t + dur + 0.04, g);
        },
        upright: function (m, t, dur, vol, out) {
            var g = ctx.createGain(), f = mhz(m + 12), end = t + Math.min(dur, 0.6) + 0.1;
            env(g, t, 0.004, vol * 1.3, Math.min(dur, 0.6) + 0.05);
            g.connect(out);
            osc('triangle', f, t, end, g);
            osc('sine', f / 2, t, end, gain(g, 0.6));
            hiss(t, 0.02, vol * 0.2, out, 'lowpass', 900);
        },
        pizz: function (m, t, dur, vol, out) { string(mhz(m + 12), t, Math.min(dur, 0.5), vol * 2, out); }
    };

    // Chords: notes in MIDI.
    var PAD = {
        pad: function (notes, t, dur, vol, out) {
            var g = ctx.createGain(), lp = filter('lowpass', 1200, 0.6, g), end = t + dur + 0.5;
            g.gain.setValueAtTime(0.0001, t);
            g.gain.linearRampToValueAtTime(vol, t + Math.min(0.4, dur * 0.4));
            g.gain.setValueAtTime(vol, t + dur);
            g.gain.linearRampToValueAtTime(0.0001, t + dur + 0.45);
            g.connect(out);
            notes.forEach(function (m) {
                osc('sawtooth', mhz(m), t, end, lp, -9);
                osc('triangle', mhz(m), t, end, lp, 9);
            });
        },
        strings: function (notes, t, dur, vol, out) {
            notes.forEach(function (m) { I.strings(mhz(m), t, dur, vol * 0.6, out); });
        },
        choir: function (notes, t, dur, vol, out) {
            notes.forEach(function (m) { I.choir(mhz(m), t, dur, vol * 0.9, out); });
        },
        saw: function (notes, t, dur, vol, out) {
            var g = ctx.createGain(), lp = filter('lowpass', 3500, 0.8, g), end = t + dur + 0.1;
            hold(g, t, dur + 0.05, vol, 0.01, 0.08);
            g.connect(out);
            notes.forEach(function (m) {
                [-12, 0, 12].forEach(function (d) { osc('sawtooth', mhz(m), t, end, lp, d); });
            });
        },
        organ: function (notes, t, dur, vol, out) {
            notes.forEach(function (m) { I.organ(mhz(m), t, dur, vol * 0.6, out); });
        },
        brass: function (notes, t, dur, vol, out) {
            notes.forEach(function (m) { I.brass(mhz(m), t, dur, vol * 0.7, out); });
        },
        piano: function (notes, t, dur, vol, out) {
            notes.forEach(function (m, i) { I.piano(mhz(m), t + i * 0.004, dur, vol * 0.7, out); });
        },
        epiano: function (notes, t, dur, vol, out) {
            notes.forEach(function (m) { I.epiano(mhz(m), t, dur, vol * 0.7, out); });
        },
        pluck: function (notes, t, dur, vol, out) {
            notes.forEach(function (m) { I.pluck(mhz(m), t, dur, vol * 0.6, out); });
        },
        // Power chord through distortion: root, fifth, octave.
        guitar: function (notes, t, dur, vol, out, cd) {
            var r = cd.r + 12, ws = ctx.createWaveShaper(), pre = ctx.createGain(), g = ctx.createGain(),
                lp = filter('lowpass', dur < 0.2 ? 1400 : 2600, 0.8, g), end = t + dur + 0.08;
            ws.curve = curve;
            pre.gain.value = 2.5;
            pre.connect(ws);
            ws.connect(lp);
            hold(g, t, dur + 0.04, vol, 0.003, 0.04);
            g.connect(out);
            [r, r + 7, r + 12].forEach(function (m, i) { osc('sawtooth', mhz(m), t + i * 0.003, end, pre, i ? 4 : -4); });
        },
        harp: function (notes, t, dur, vol, out) {
            notes.forEach(function (m, i) { string(mhz(m), t + i * 0.03, 1.2, vol * 1.2, out); });
        }
    };

    // Relative loudness of every instrument.
    var LEVEL = {piano: 0.2, epiano: 0.17, bell: 0.1, mallet: 0.22, pluck: 0.1, saw: 0.05, square: 0.075, brass: 0.09,
        strings: 0.065, pizz: 0.28, harp: 0.24, guitar: 0.06, organ: 0.06, flute: 0.13, choir: 0.08};
    var PADLEVEL = {pad: 0.03, strings: 0.045, choir: 0.05, saw: 0.017, organ: 0.04, brass: 0.06, piano: 0.12, epiano: 0.11,
        pluck: 0.08, guitar: 0.05, harp: 0.12};

    /* ---------------- grooves ---------------- */

    // One bar of drum codes: an array of strings, one per step, several codes per step.
    // k kick, s snare, c clap, h hat, i soft hat, o open hat, r rim, x crash, B boom, t m n toms,
    // z shaker, g q congas, X impact.
    function groove(name, spb, bpb) {
        var n = spb * bpb, a = [], e = spb === 3 ? 1 : spb / 2, comp = spb === 3, k;
        for (k = 0; k < n; k++) a.push('');
        function on(beat, c) { var p = Math.round(beat * spb); if (p >= 0 && p < n) a[p] += c; }
        function every(step, c, from) { for (var q = from || 0; q < n; q += step) a[q] += c; }
        var half = e / spb;   // an eighth note in beats
        if (name === 'pop' || name === 'rock') {
            if (bpb === 3) { on(0, 'k'); on(1, 'r'); on(2, 'r'); every(e, 'h'); }
            else {
                on(0, 'k');
                if (name === 'rock') on(half, 'k');
                if (bpb === 4) { on(2, 'k'); on(2 + half, 'k'); on(1, 's'); on(3, 's'); }
                else if (bpb === 2) on(1, 's');
                else { on(1, 's'); on(3, 's'); }
                every(e, 'h');
                if (comp && bpb === 2) a[n - 1] += 'k';
            }
        } else if (name === 'half') {
            on(0, 'k');
            if (bpb >= 4) on(2, 's'); else if (bpb === 2) on(1, 'r'); else on(bpb - 1, 'r');
            every(spb, 'i');
        } else if (name === 'four' || name === 'disco') {
            for (k = 0; k < bpb; k++) {
                on(k, 'k');
                if (!comp && k % 2 === 1) on(k, 'c');
                if (!comp) on(k + half, 'o');
            }
            if (comp) { on(1, 'c'); every(1, 'i'); }
            if (bpb === 3) on(1, 'c');
            if (name === 'disco' || spb === 4) every(spb === 4 ? 1 : e, 'i');
        } else if (name === 'epic') {
            on(0, 'B');
            if (bpb === 4) { on(1, 'm'); on(1 + half, 't'); on(2, 'B'); on(3, 'm'); on(3 + half, 'n'); }
            else if (bpb === 2) { on(1, 'm'); on(1 + half, 'n'); }
            else if (bpb === 3) { on(1, 'm'); on(2, 'n'); }
            else { for (k = 1; k < bpb; k++) on(k, 'm'); }
            every(e, 'z');
        } else if (name === 'boom') {
            on(0, 'B');
            if (bpb === 4) on(2, 't');
        } else if (name === 'lofi') {
            on(0, 'k');
            if (bpb === 4) { on(1, 'r'); on(2 + half, 'k'); on(3, 'r'); }
            else if (bpb === 3) { on(1, 'r'); on(2, 'r'); }
            else on(1, 'r');
            every(e, 'i');
        } else if (name === 'latin') {
            on(0, 'k'); on(bpb / 2, 'k');
            [0, 3, 6].forEach(function (x) { if (x * e < n) a[x * e] += 'r'; });
            for (k = 0; k < bpb; k++) { on(k + half, 'q'); }
            on(bpb - 1, 'g'); on(bpb - 1 + half, 'g');
            every(e, 'z');
        } else if (name === 'swing') {
            for (k = 0; k < bpb; k++) {
                on(k, 'i');
                if (k % 2 === 1) { on(k, 'r'); on(k + half, 'i'); }
                if (k % 2 === 0) on(k, 'k');
            }
        } else if (name === 'gallop') {
            for (k = 0; k < bpb; k++) { on(k, 'k'); on(k + half, 's'); }
            every(e, 'i');
        } else if (name === 'waltz') {
            on(0, 'k'); on(1, 'r'); on(2, 'r'); every(spb, 'i');
        } else if (name === 'ticks') {
            every(e, 'i');
            on(0, 'k');
        }
        return a;
    }

    // Last bar of a section.
    function fillBar(type, base, spb, bpb) {
        var n = spb * bpb, a = base.slice(), from = n - spb * (bpb >= 4 ? 2 : 1), k;
        if (type === 'snare') {
            for (k = from; k < n; k++) a[k] = (k === from ? 'k' : '') + (spb === 4 || k % (spb === 3 ? 1 : spb / 2) === 0 ? 's' : '');
        } else if (type === 'tom') {
            var T = ['n', 'n', 'm', 'm', 't', 't', 'B', 'B'];
            for (k = from; k < n; k++) a[k] = (spb === 4 && k % 2) ? '' : T[Math.floor((k - from) / (n - from) * 8)];
        } else if (type === 'riser') {
            a[0] += 'R';
            a[n - spb] += 's';
        }
        return a;
    }

    /* ---------------- songs ---------------- */

    var BAD = [];

    // One public-domain melody in a style. v: id, name, by, bpm, spb (steps per beat), bpb (beats per bar),
    // mel, ch (chords, evenly spaced), style, lead (main instrument), swing, accel, sec (own sections).
    function song(v) {
        var mel = parseMel(v.mel), L = mel.note.length, steps = v.spb * v.bpb, chs = v.ch.split(/\s+/).map(chord),
            slot = L / chs.length, secs = (v.sec || STYLES[v.style]).map(function (s) {
                var o = {}, k;
                for (k in s) if (s.hasOwnProperty(k)) o[k] = s[k];
                if (o.lead === '*') o.lead = v.lead || STYLE_LEAD[v.style];
                if (o.l2 === '*') o.l2 = v.lead || STYLE_LEAD[v.style];
                o.base = groove(o.dr || 'none', v.spb, v.bpb);
                o.last = o.fill ? fillBar(o.fill, o.base, v.spb, v.bpb) : o.base;
                o.urg = groove(o.dr === 'none' || o.dr === 'boom' || o.dr === 'ticks' || !o.dr ? 'pop' : o.dr, v.spb, v.bpb)
                    .map(function (s2, i) { return s2 + (v.spb === 4 || i % (v.spb === 3 ? 1 : v.spb / 2) === 0 ? 'h' : ''); });
                return o;
            }), S = secs.length, bars = L / steps;
        if (L % steps || slot !== Math.floor(slot)) BAD.push(v.name + ': ' + L + ' steps, ' + chs.length + ' chords, bar ' + steps);
        var tonic = chs[0].r, sw = v.swing ? 1 / 3 : 0, half = v.spb === 3 ? 0 : v.spb / 2;
        function pass(c) { return Math.floor(c / L); }
        function secOf(k) { return k < S ? k : S === 1 ? 0 : 1 + ((k - 1) % (S - 1)); }
        return {
            bpm: v.bpm, spb: v.spb, bpb: v.bpb, urgent: 1.12, v: v, tonic: tonic, gain: v.gain || STYLE_GAIN[v.style] || 1,
            rate: v.accel ? function (c) { return 1 + v.accel * Math.min(3, pass(c)); } : null,
            play: function (p, c, t, sd) {
                var k = pass(c), sec = secs[secOf(k)], j = c % L, bar = Math.floor(j / steps), pos = j % steps,
                    acc = 0.9 + 0.2 * hash(c * 7 + v.id * 131), cd = chs[Math.floor(j / slot)], H = p.h, beatPos = pos % v.spb;
                if (sw && half && beatPos === half) t += sd * half * sw;
                if (sec.pump && !p.pump) {
                    p.pump = gain(p.h);
                    H = p.pump;
                } else if (sec.pump) H = p.pump;
                var slotStart = j % slot === 0, slotDur = slot * sd;
                // pads
                if (sec.pad && slotStart) {
                    PAD[sec.pad](voice(cd, sec.pl || 55), t, slotDur, PADLEVEL[sec.pad] * (sec.pv || 1), H, cd);
                }
                // bass
                var bp = sec.bass, isBeat = beatPos === 0, isHalf = half && beatPos === half, bn = cd.r - 12;
                if (bp) {
                    var bi = BASS[sec.bi || v.bass || 'synth'], bv = 0.26 * (sec.bv || 1), b = null, bl = sd;
                    if (bp === 'root' && slotStart) { b = bn; bl = slotDur * 0.95; }
                    else if (bp === 'beat' && isBeat) { b = bn; bl = sd * v.spb * 0.9; }
                    else if (bp === 'eighth' && (isBeat || isHalf || v.spb === 3)) { b = bn; bl = sd * (half || 1) * 0.8; }
                    else if (bp === 'off') {
                        if (isHalf || (v.spb === 3 && beatPos === 2)) { b = bn; bl = sd * (half || 1) * 0.9; }
                        else if (v.spb === 4 && beatPos === 3) { b = bn + 12; bl = sd * 0.8; bv *= 0.6; }
                    }
                    else if (bp === 'oct' && (isBeat || isHalf)) { b = bn + (isHalf ? 12 : 0); bl = sd * (half || 1) * 0.8; }
                    else if (bp === 'oompa' && isBeat) {
                        var bt = Math.floor(pos / v.spb);
                        b = bn + (bt % 2 ? 7 : 0);
                        bl = sd * v.spb * 0.6;
                    } else if (bp === 'walk' && isBeat) {
                        var w = Math.floor(pos / v.spb) % 4, nx = chs[(Math.floor(j / slot) + 1) % chs.length].r - 12;
                        b = [bn, bn + cd.iv[1], bn + 7, nx + (nx > bn ? -1 : 1)][w];
                        bl = sd * v.spb * 0.9;
                    }
                    if (b !== null) bi(b, t, bl, bv * acc, p.out);
                }
                // comping chords
                if (sec.comp) {
                    var cp = sec.cr || 'off', hitIt = false, cl = sd;
                    if (cp === 'off') { hitIt = isHalf || (v.spb === 3 && beatPos === 1); cl = sd * (half || 1) * 0.7; }
                    else if (cp === 'beats') { hitIt = isBeat && pos > 0; cl = sd * v.spb * 0.5; }
                    else if (cp === 'eighth') { hitIt = isBeat || isHalf || v.spb === 3; cl = sd * (half || 1) * 0.6; }
                    else if (cp === 'push') { hitIt = slotStart || (pos === steps - (half || 1)); cl = sd * 2; }
                    if (hitIt) PAD[sec.comp](voice(cd, sec.cl || 60), t, cl, PADLEVEL[sec.comp] * (sec.cv || 1) * acc, H, cd);
                }
                // arpeggio
                if (sec.arp) {
                    var rateA = sec.ar || (v.spb === 4 ? 1 : v.spb === 3 ? 1 : v.spb / 2);
                    if (pos % rateA === 0) {
                        var vn = voice(cd, sec.al || 67), idx = (pos / rateA) % (vn.length * 2 - 2 || 1),
                            an = vn[idx < vn.length ? idx : vn.length * 2 - 2 - idx];
                        I[sec.arp](mhz(an), t, sd * rateA * 0.9, LEVEL[sec.arp] * 0.45 * (sec.av || 1) * acc, (pos / rateA) % 2 ? p.R : p.L);
                    }
                }
                // melody
                if (mel.fresh[j] && sec.lead) {
                    var dur = mel.len[j] * sd, note = mel.note[j] + (sec.o || 0) + (v.o || 0);
                    I[sec.lead](mhz(note), t, dur, LEVEL[sec.lead] * (sec.lv || 1) * acc, H);
                    if (sec.l2) I[sec.l2](mhz(note + (sec.o2 || 0)), t, dur, LEVEL[sec.l2] * 0.7 * (sec.l2v || 1) * acc, H);
                }
                // drums
                var dp = p.urgent ? sec.urg : sec.dp ? sec.dp : bar === bars - 1 ? sec.last : sec.base, codes = dp[pos] || '';
                if (j === 0 && sec.crash && k > 0) codes += 'x';
                hits(p, codes, t, sd, (v.dv || 1) * (sec.dv || 1), acc * (isBeat ? 1 : 0.85), cd);
            }
        };
    }

    function hits(p, codes, t, sd, dv, acc, cd) {
        for (var i = 0; i < codes.length; i++) {
            var c = codes.charAt(i), o = p.out, v = dv * acc;
            if (c === 'k') {
                kick(t, 0.85 * dv, o);
                if (p.pump) {
                    p.pump.gain.cancelScheduledValues(t);
                    p.pump.gain.setValueAtTime(0.3, t);
                    p.pump.gain.linearRampToValueAtTime(1, t + Math.min(0.28, sd * 3));
                }
            }
            else if (c === 's') snare(t, 0.42 * v, p.dr);
            else if (c === 'c') clap(t, 0.32 * v, p.dr);
            else if (c === 'h') hat(t, 0.075 * v, p.R);
            else if (c === 'i') hat(t, 0.045 * v, p.R);
            else if (c === 'o') hat(t, 0.06 * v, p.R, true);
            else if (c === 'r') rim(t, 0.16 * v, p.dr);
            else if (c === 'x') crash(t, 0.12 * dv, p.dr);
            else if (c === 'B') boom(t, 0.75 * v, p.dr);
            else if (c === 't') tom(t, 90, 0.45 * v, p.dr);
            else if (c === 'm') tom(t, 125, 0.4 * v, p.dr);
            else if (c === 'n') tom(t, 170, 0.36 * v, p.dr);
            else if (c === 'z') shaker(t, 0.05 * v, p.L);
            else if (c === 'g') conga(t, 200, 0.32 * v, p.L);
            else if (c === 'q') conga(t, 320, 0.26 * v, p.R);
            else if (c === 'R') riser(t, sd * 16, 0.08 * dv, p.dr);
            else if (c === 'X') {
                boom(t, 0.9 * dv, p.dr);
                kick(t, 0.8 * dv, o);
                crash(t, 0.16 * dv, p.dr, 2);
                if (cd) PAD.brass(voice(cd, 60), t, 0.35, 0.09 * dv, p.h, cd);
            }
        }
    }

    var STYLE_LEAD = {epic: 'strings', rock: 'guitar', edm: 'saw', disco: 'strings', pop: 'pluck', lofi: 'epiano', chip: 'square',
        orch: 'pizz', latin: 'brass', swing: 'piano', gallop: 'mallet'};

    // Loudness match between styles (measured), so no tune is much louder than the next one.
    var STYLE_GAIN = {epic: 0.8, swing: 1.8, latin: 1.9, orch: 1.8, chip: 1.2, gallop: 1.15, lofi: 1.05, pop: 0.95, disco: 0.9};

    var STYLES = {
        epic: [
            {lead: '*', pad: 'strings', pv: 0.8, bass: 'root', bi: 'sub', dr: 'boom', fill: 'tom'},
            {lead: '*', l2: 'brass', o2: -12, pad: 'choir', bass: 'beat', bi: 'sub', dr: 'epic', arp: 'pizz', av: 0.7, fill: 'tom', crash: 1},
            {lead: 'brass', l2: 'strings', o2: 12, pad: 'strings', bass: 'eighth', bi: 'synth', dr: 'epic', arp: 'pluck', comp: 'brass', cr: 'push', cv: 0.5, fill: 'riser', crash: 1}],
        rock: [
            {lead: '*', pad: 'pad', pv: 0.7, bass: 'eighth', dr: 'ticks', fill: 'snare'},
            {lead: '*', comp: 'guitar', cr: 'eighth', bass: 'eighth', dr: 'rock', fill: 'snare', crash: 1},
            {lead: 'saw', l2: '*', o2: -12, comp: 'guitar', cr: 'eighth', pad: 'strings', pv: 0.6, bass: 'eighth', dr: 'rock', fill: 'tom', crash: 1}],
        edm: [
            {lead: 'pluck', pad: 'pad', bass: 'root', bi: 'sub', bv: 0.7, dr: 'ticks', arp: 'pluck', fill: 'riser'},
            {lead: '*', l2: 'pluck', o2: 12, pad: 'saw', pump: 1, bass: 'off', dr: 'four', fill: 'snare', crash: 1},
            {lead: 'saw', l2: 'bell', o2: 12, pad: 'saw', pump: 1, bass: 'off', arp: 'pluck', dr: 'four', fill: 'riser', crash: 1}],
        disco: [
            {lead: '*', pad: 'strings', pv: 0.6, bass: 'oct', dr: 'disco', comp: 'epiano', cr: 'off', fill: 'snare'},
            {lead: 'brass', l2: 'strings', o2: 12, bass: 'oct', dr: 'disco', comp: 'guitar', cr: 'off', cv: 0.5, arp: 'bell', av: 0.6, fill: 'snare', crash: 1}],
        pop: [
            {lead: 'piano', pad: 'pad', pv: 0.8, bass: 'root', dr: 'half'},
            {lead: '*', pad: 'pad', bass: 'eighth', dr: 'pop', comp: 'piano', cr: 'off', cv: 0.6, fill: 'snare', crash: 1},
            {lead: '*', l2: 'bell', o2: 12, pad: 'strings', pv: 0.8, bass: 'eighth', arp: 'pluck', dr: 'pop', fill: 'snare', crash: 1}],
        lofi: [
            {lead: '*', pad: 'pad', pv: 0.9, bass: 'root', bi: 'sub', bv: 0.7, dr: 'lofi', dv: 0.8},
            {lead: '*', l2: 'bell', o2: 12, l2v: 0.6, pad: 'pad', bass: 'beat', bi: 'sub', bv: 0.7, arp: 'epiano', av: 0.5, dr: 'lofi', dv: 0.8}],
        chip: [
            {lead: 'square', bass: 'eighth', bi: 'chip', dr: 'pop', arp: 'square', av: 0.5, fill: 'snare'},
            {lead: 'square', l2: 'square', o2: 12, l2v: 0.5, bass: 'eighth', bi: 'chip', dr: 'pop', arp: 'square', av: 0.5, fill: 'snare', crash: 1}],
        orch: [
            {lead: '*', pad: 'strings', pv: 0.6, bass: 'beat', bi: 'pizz', dr: 'none'},
            {lead: 'strings', l2: 'flute', o2: 12, pad: 'strings', pv: 0.7, bass: 'beat', bi: 'pizz', arp: 'harp', av: 0.6, dr: 'boom', fill: 'tom'},
            {lead: 'brass', l2: 'strings', o2: 12, pad: 'strings', bass: 'beat', bi: 'sub', dr: 'epic', arp: 'bell', av: 0.5, fill: 'tom', crash: 1}],
        latin: [
            {lead: '*', comp: 'piano', cr: 'off', bass: 'oompa', bi: 'upright', dr: 'latin'},
            {lead: 'brass', l2: 'brass', o2: -12, comp: 'piano', cr: 'off', bass: 'oompa', bi: 'upright', dr: 'latin', fill: 'snare', crash: 1}],
        swing: [
            {lead: '*', comp: 'piano', cr: 'beats', cv: 0.6, bass: 'walk', bi: 'upright', dr: 'swing'},
            {lead: 'brass', l2: 'brass', o2: -12, comp: 'piano', cr: 'beats', cv: 0.6, bass: 'walk', bi: 'upright', dr: 'swing', fill: 'snare', crash: 1}],
        gallop: [
            {lead: '*', bass: 'oompa', bi: 'pizz', dr: 'gallop', comp: 'pluck', cr: 'off', cv: 0.6},
            {lead: 'strings', l2: 'mallet', o2: 12, pad: 'strings', pv: 0.6, bass: 'oompa', dr: 'gallop', fill: 'snare', crash: 1},
            {lead: 'brass', l2: 'strings', o2: 12, bass: 'oompa', dr: 'gallop', comp: 'brass', cr: 'off', cv: 0.5, fill: 'snare', crash: 1}]
    };

    function at(n, pos, tok, fill) {
        var a = [];
        for (var k = 0; k < n; k++) a.push(pos.indexOf(k) >= 0 ? tok : fill);
        return a.join(fill === '-' ? ' ' : '');
    }
    function times(s, n) { return new Array(n + 1).join(s + ' '); }
    function codes(s) { return s.split(''); }
    var MARS = [0, 2, 4, 6, 12, 18, 21, 24];

    // Every melody here is public domain: the composers died long ago (the year is in `by`),
    // or it is a traditional folk tune. Order: styles alternate so neighbouring questions differ.
    var QUESTION = [
        song({id: 20, name: 'В пещере горного короля', by: 'Э. Григ (1843–1907)', style: 'rock', bpm: 126, spb: 2, bpb: 4, accel: 0.1, o: -12,
            mel: "b, c# d e f# d f# - | f c# f - e c e - | b, c# d e f# d f# b | a f# d f# a - - -",
            ch: 'Bm Bm C# C Bm Bm D D'}),
        song({id: 21, name: 'Турецкий марш', by: 'В. А. Моцарт (1756–1791)', style: 'edm', bpm: 124, spb: 4, bpb: 2, o: -12,
            mel: "b a g# a c' - d' c' | b c' e' - f' e' d#' e' | b' a' g#' a' b' a' g#' a' | c'' - - - a' - b' -",
            ch: 'Am Am Am E Am E Am E'}),
        song({id: 22, name: 'Коробейники', by: 'русская народная песня', style: 'chip', bpm: 140, spb: 2, bpb: 4,
            mel: "e' - b c' d' - c' b | a - a c' e' - d' c' | b - - c' d' - e' - | c' - a - a - - - |" +
                 ". d' - f' a' - g' f' | e' - - c' e' - d' c' | b - b c' d' - e' - | c' - a - a - - -",
            ch: 'E Am E Am Dm C E Am'}),
        song({id: 23, name: 'Канкан', by: 'Ж. Оффенбах (1819–1880)', style: 'gallop', bpm: 144, spb: 2, bpb: 2, o: 12,
            mel: "c - - - | d f e d | g - g - | g a e f | d - d - | d f e d | c c' b a | g f e d",
            ch: 'C G7 C F G7 G7 C G7'}),
        song({id: 24, name: 'К Элизе', by: 'Л. ван Бетховен (1770–1827)', style: 'lofi', bpm: 140, spb: 2, bpb: 3, lead: 'epiano',
            mel: "e' d#' e' b d' c' | a - . c e a | b - . e g# b | c' - . e e' d#' |" +
                 "e' d#' e' b d' c' | a - . c e a | b - . e c' b | a - . . e' d#'",
            ch: 'Am Am E Am Am Am E Am'}),
        song({id: 25, name: 'Симфония № 5', by: 'Л. ван Бетховен (1770–1827)', style: 'epic', bpm: 112, spb: 2, bpb: 2, lead: 'strings',
            mel: ". g g g | eb - - - | . f f f | d - - - | . g g g | eb . ab ab | ab g . eb' | eb' eb' c' -",
            ch: 'Cm Cm G G Cm Ab Fm Cm'}),
        song({id: 26, name: 'Маленькая ночная серенада', by: 'В. А. Моцарт (1756–1791)', style: 'disco', bpm: 122, spb: 2, bpb: 4,
            mel: "g' - - d' g' - - d' | g' d' g' b' d'' - - - | c'' - - a' c'' - - a' | c'' a' f#' a' d' - - - |" +
                 "g' - - d' g' - - d' | g' d' g' b' d'' - - - | c'' - - a' c'' - - a' | c'' a' f#' a' g' - - -",
            ch: 'G G D7 D G G D7 G', o: -12}),
        song({id: 27, name: 'Пьяный матрос', by: 'английская народная песня', style: 'rock', bpm: 150, spb: 2, bpb: 4, lead: 'brass',
            mel: "a - a a a - a a | a - d - f - a - | g - g g g - g g | g - c - e - g - |" +
                 "a - a a a - a a | a - b - c' - d' - | c' - a - g - e - | d - - - d - - -",
            ch: 'Dm Dm C C Dm Dm C Dm'}),
        song({id: 28, name: 'Весна («Времена года»)', by: 'А. Вивальди (1678–1741)', style: 'edm', bpm: 126, spb: 2, bpb: 4, o: -12,
            mel: "e' - g#' g#' g#' - f#' e' | b' - - - - - b' a' | g#' - g#' g#' g#' - f#' e' | b' - - - - - b' a' |" +
                 "g#' - a' b' a' - g#' - | f#' - d#' - b - - - | g#' - a' b' a' - g#' - | f#' - d#' - e' - - -",
            ch: 'E E E E E B E E'}),
        song({id: 29, name: 'Хава нагила', by: 'еврейская народная мелодия', style: 'edm', bpm: 132, spb: 2, bpb: 4, lead: 'saw',
            mel: "e - - e g# - f e | g# - - g# b - a g# | a - - a c' - b a | g# - f - e - - - |" +
                 "e - - e g# - f e | g# - - g# b - a g# | a - - a c' - b a | g# f g# a g# - - -",
            ch: 'E E Am E E E Am E', o: 12}),
        song({id: 30, name: 'Лебединое озеро', by: 'П. И. Чайковский (1840–1893)', style: 'epic', bpm: 96, spb: 2, bpb: 4, lead: 'strings',
            mel: "f#' - - - b c#' d' e' | f#' - - - - - d' - | f#' - - - - - d' - | f#' - - b d' b g d' |" +
                 "b - - - - - - - | . . . . . . . .",
            ch: 'Bm Bm D Bm Bm F#'}),
        song({id: 31, name: 'Регтайм «Артист»', by: 'С. Джоплин (1868–1917)', style: 'swing', bpm: 96, spb: 4, bpb: 2,
            mel: "d d# e c' - e c' - | e c' - - - - c' d' | d#' e' c' d' e' - b d' | c' - - - - - d d# |" +
                 "e c' - e c' - e c' | - - - - - - a g | f# a c' e' - d' c' a | d' - - - - - - -",
            ch: 'C C G7 C C C D7 G7'}),
        song({id: 32, name: 'Марс («Планеты»)', by: 'Г. Холст (1874–1934)', gain: 1.6, bpm: 150, spb: 6, bpb: 5,
            mel: times(at(30, MARS, 'g,', '-'), 4), ch: 'G5 G5 Ab5 G5',
            sec: [{lead: 'pizz', pad: 'strings', pv: 0.7, dp: codes(at(30, [0], 'B', '.'))},
                {lead: 'guitar', o: -12, l2: 'strings', o2: 12, pad: 'choir', dp: codes(at(30, MARS, 't', '.')).map(function (c, i) { return i === 0 ? 'B' : c; })},
                {lead: 'guitar', o: -12, l2: 'brass', o2: 12, pad: 'strings', bass: 'root', bi: 'sub', dp: codes(at(30, MARS, 'B', '.')), crash: 1}]}),
        song({id: 33, name: 'Ля кукарача', by: 'мексиканская народная песня', style: 'latin', bpm: 120, spb: 2, bpb: 4, lead: 'harp',
            mel: "c c c f - a - - | c c c f - a - - | f - f e e d d - | c - - - - - - - |" +
                 "c c c e - g - - | c c c e - g - - | c' - d' c' bb a g a | f - - - - - - -",
            ch: 'F F C7 C7 C7 C7 F F', o: 12}),
        song({id: 34, name: 'Вильгельм Телль, финал', by: 'Дж. Россини (1792–1868)', style: 'rock', bpm: 132, spb: 4, bpb: 2, lead: 'guitar',
            mel: "g g g - g g g - | g g c' - d' - e' - | g g g - g g g - | g g d' - b - g - |" +
                 "c' c' c' - c' c' c' - | c' c' f' - g' - a' - | g' - f' - e' - d' - | c' - e' - c' - - -",
            ch: 'C C C G F F G C'}),
        song({id: 35, name: 'Утро («Пер Гюнт»)', by: 'Э. Григ (1843–1907)', style: 'lofi', bpm: 76, spb: 3, bpb: 2, lead: 'flute',
            mel: "g' - e' d' c' d' | e' - - g' - e' | d' c' d' e' d' e' | g' - e' g' - a' |" +
                 "e' - a' g' - e' | d' - c' - - - | c' - - - - - | . . . . . .",
            ch: 'C C G C Am Am G C'}),
        song({id: 36, name: 'Симфония № 40', by: 'В. А. Моцарт (1756–1791)', style: 'pop', bpm: 112, spb: 2, bpb: 4, lead: 'saw',
            mel: "eb' d' d' - eb' d' d' - | eb' d' d' - bb' - - - | bb' a' g' - g' f' eb' - | eb' d' c' - c' - - - |" +
                 "d' c' c' - d' c' c' - | d' c' c' - a' - - - | a' g' f#' - f#' eb' d' - | d' c' bb - bb - - -",
            ch: 'Gm Gm Cm Cm D7 D7 D7 Gm', o: -12}),
        song({id: 37, name: 'Полёт шмеля', by: 'Н. А. Римский-Корсаков (1844–1908)', style: 'rock', bpm: 132, spb: 4, bpb: 2, lead: 'saw',
            mel: "e'' d#'' d'' c#'' d'' c#'' c'' b' | c'' b' bb' a' g#' g' f#' f' | e' f' e' d#' e' f' e' d#' | e' f' f#' g' g#' a' a#' b' |" +
                 "e'' d#'' d'' c#'' d'' c#'' c'' b' | c'' b' bb' a' g#' g' f#' f' | e' f' e' d#' e' f' e' d#' | a' - e' - a - - -",
            ch: 'Am Am E E Am Am E Am', o: -12}),
        song({id: 38, name: 'Когда святые маршируют', by: 'американская народная песня', style: 'swing', bpm: 168, spb: 2, bpb: 4, swing: 1, lead: 'brass',
            mel: ". . c - e - f - | g - - - - - - - | . . c - e - f - | g - - - - - - - |" +
                 ". . c - e - f - | g - - - e - - - | c - - - e - - - | d - - - - - - - |" +
                 ". . e - e - d - | c - - - c - e - | g - - - g - f - | - - - - - - - - |" +
                 ". . e - f - g - | e - - - c - - - | d - - - - - - - | c - - - - - - -",
            ch: 'C C C C C C G G C C7 F F C G C C'}),
        song({id: 39, name: 'Канон ре мажор', by: 'И. Пахельбель (1653–1706)', style: 'pop', bpm: 100, spb: 2, bpb: 4, lead: 'strings',
            mel: "f#'' - - - e'' - - - | d'' - - - c#'' - - - | b' - - - a' - - - | b' - - - c#'' - - - |" +
                 "d'' - c#'' - b' - a' - | g' - f#' - g' - e' - | f#' - d' - e' - c#' - | d' - b - c#' - a -",
            ch: 'D A Bm F#m G D G A D A Bm F#m G D G A', o: -12}),
        song({id: 40, name: 'Менуэт соль мажор', by: 'Х. Петцольд (1677–1733)', style: 'chip', bpm: 132, spb: 2, bpb: 3,
            mel: "d'' - g' a' b' c'' | d'' - g' - g' - | e'' - c'' d'' e'' f#'' | g'' - g' - g' - |" +
                 "c'' - d'' c'' b' a' | b' - c'' b' a' g' | f#' - g' a' b' g' | a' - - - - -",
            ch: 'G G C G C G D D', o: -12}),
        song({id: 41, name: 'Токката и фуга ре минор', by: 'И. С. Бах (1685–1750)', gain: 1.1, bpm: 76, spb: 4, bpb: 4,
            mel: "a' g' a' - - - - - - - - - - - - - | g f e d c# - - - d - - - - - - -",
            ch: 'Dm Dm A7 Dm',
            sec: [{lead: 'organ', pad: 'organ', pv: 0.5, dr: 'none'},
                {lead: 'organ', o: -12, pad: 'choir', bass: 'root', bi: 'sub', dr: 'boom', fill: 'tom'},
                {lead: 'organ', o: -12, l2: 'saw', o2: 0, pad: 'strings', bass: 'eighth', comp: 'guitar', cr: 'eighth', dr: 'rock', fill: 'snare', crash: 1}]}),
        song({id: 42, name: 'О, Сюзанна', by: 'С. Фостер (1826–1864)', style: 'pop', bpm: 132, spb: 2, bpb: 4, lead: 'harp',
            mel: "e - g - g - - a | g - e - c - - d | e - e - d - c - | d - - - - - c d |" +
                 "e - g - g - - a | g - e - c - - d | e - e - d - d - | c - - - - - c d",
            ch: 'C C C G C C G C'}),
        song({id: 43, name: 'Сюрприз (симфония № 94)', by: 'Й. Гайдн (1732–1809)', style: 'orch', gain: 2.7, bpm: 120, spb: 2, bpb: 2,
            mel: "c - c - | e - e - | g - g - | e - - - | f - f - | d - d - | b, - b, - | g, - - - |" +
                 "c - c - | e - e - | g - g - | e - - - | f - f - | d - d - | b, - b, - | g, - - . ",
            ch: 'C C C C G7 G7 G G C C C C G7 G7 G G', o: 12,
            sec: [{lead: 'pizz', pad: 'strings', pv: 0.5, bass: 'beat', bi: 'pizz', dp: null, dr: 'none',
                    fill: null},
                {lead: 'strings', l2: 'flute', o2: 12, pad: 'strings', pv: 0.7, bass: 'beat', bi: 'pizz', arp: 'harp', av: 0.6, dr: 'waltz', crash: 1}]}),
        song({id: 44, name: 'Зелёные рукава', by: 'английская народная песня', style: 'orch', bpm: 92, spb: 3, bpb: 2, lead: 'flute',
            mel: "c' - d' e' f' e' | d' - b g a b | c' - a a g# a | b - g# e - a |" +
                 "c' - d' e' f' e' | d' - b g a b | c' b a g# f# g# | a - - a - -",
            ch: 'Am G Am E Am G E Am'}),
        song({id: 45, name: 'Мне радостно (кантата 147)', by: 'И. С. Бах (1685–1750)', style: 'pop', bpm: 92, spb: 3, bpb: 3, lead: 'piano',
            mel: "g a b d' c' c' e' d' d' | g' f#' g' d' b g a b c' | d' e' d' c' b a b g f# | g a d f# a c' b a b",
            ch: 'G G D D'}),
        song({id: 46, name: 'Аллилуйя', by: 'Г. Ф. Гендель (1685–1759)', style: 'epic', bpm: 92, spb: 4, bpb: 4, lead: 'choir',
            mel: "d' - - - a - - b a - - - . . . . | d' - - - a - - b a - - - . . . . |" +
                 "a - b - a - b - a - - - . . . . | a - - b c#' - - - d' - - - . . . .",
            ch: 'D D G A'}),
        song({id: 47, name: 'Братец Жак', by: 'французская народная песня', style: 'gallop', gain: 1.7, bpm: 132, spb: 2, bpb: 4,
            mel: "c - d - e - c - | c - d - e - c - | e - f - g - - - | e - f - g - - - |" +
                 "g a g f e - c - | g a g f e - c - | c - g, - c - - - | c - g, - c - - -",
            ch: 'C C C C C C G C', o: 12}),
        song({id: 48, name: 'Ода к радости', by: 'Л. ван Бетховен (1770–1827)', style: 'disco', bpm: 120, spb: 2, bpb: 4,
            mel: "f# - f# - g - a - | a - g - f# - e - | d - d - e - f# - | f# - - e e - - - |" +
                 "f# - f# - g - a - | a - g - f# - e - | d - d - e - f# - | e - - d d - - -",
            ch: 'D D A A D D D A D D A A D D A D'}),
        song({id: 49, name: 'Звёздочка (вариации)', by: 'В. А. Моцарт (1756–1791)', style: 'edm', bpm: 124, spb: 2, bpb: 4, lead: 'bell',
            mel: "c - c - g - g - | a - a - g - - - | f - f - e - e - | d - d - c - - - |" +
                 "g - g - f - f - | e - e - d - - - | g - g - f - f - | e - e - d - - -",
            ch: 'C C F C F C G C C F C G C F C G', o: 12}),
        song({id: 50, name: 'Бубенцы', by: 'Дж. Пирпонт (1822–1893)', style: 'swing', bpm: 176, spb: 2, bpb: 4, swing: 1, lead: 'bell',
            mel: "e - e - e - - - | e - e - e - - - | e - g - c - d - | e - - - - - - - |" +
                 "f - f - f - f - | f - e - e - e e | e - d - d - e - | d - - - g - - -",
            ch: 'C C C C F C D7 G', o: 12})
    ];

    var LOBBY = [
        // Dvorak, Symphony No. 9, Largo
        song({id: 1, name: 'Симфония «Из Нового Света», ларго', by: 'А. Дворжак (1841–1904)', style: 'lofi', bpm: 70, spb: 2, bpb: 4, lead: 'epiano',
            mel: "e - - g g - - - | e - - d c - - - | d - - e g - - e | d - - - - - - - |" +
                 "e - - g g - - - | e - - d c - - - | d - - e d - - c | c - - - - - - -",
            ch: 'D Bm A A D Bm A D', o: 2}),
        // Satie, Gymnopedie No. 1
        song({id: 2, name: 'Гимнопедия № 1', by: 'Э. Сати (1866–1925)', style: 'lofi', bpm: 84, spb: 2, bpb: 3, lead: 'epiano',
            mel: ". . f#'' - a'' - | g'' - f#'' - c#'' - | b' - c#'' - d'' - | a' - - - - - |" +
                 "f#' - - - - - | - - - - - - | . . . . . . | . . . . . .",
            ch: 'GM7 DM7 GM7 DM7 GM7 DM7 GM7 DM7', o: -12}),
        // Strauss II, The Blue Danube
        song({id: 3, name: 'На прекрасном голубом Дунае', by: 'И. Штраус-сын (1825–1899)', style: 'lofi', bpm: 120, spb: 2, bpb: 3, lead: 'bell',
            mel: ". . . . d - | d - f# - a - | a - - - a' - | a' - - - f#' - | f#' - - - d - | d - f# - a - | a - - - a' - | a' - - - g' - |" +
                 "g' - - - c# - | c# - e - b - | b - - - b' - | b' - - - g' - | g' - - - c# - | c# - e - b - | b - - - b' - | b' - - - f#' - ",
            ch: 'D D D D D D A7 A7 A7 A7 A7 A7 A7 A7 D D'})
    ];

    var FINAL = [
        song({id: 7, name: 'Ода к радости', by: 'Л. ван Бетховен (1770–1827)', style: 'epic', bpm: 112, spb: 2, bpb: 4, lead: 'brass',
            mel: "f# - f# - g - a - | a - g - f# - e - | d - d - e - f# - | f# - - e e - - - |" +
                 "f# - f# - g - a - | a - g - f# - e - | d - d - e - f# - | e - - d d - - -",
            ch: 'D D A A D D D A D D A A D D A D'}),
        song({id: 8, name: 'Аллилуйя', by: 'Г. Ф. Гендель (1685–1759)', style: 'epic', bpm: 96, spb: 4, bpb: 4, lead: 'choir',
            mel: "d' - - - a - - b a - - - . . . . | d' - - - a - - b a - - - . . . . |" +
                 "a - b - a - b - a - - - . . . . | a - - b c#' - - - d' - - - . . . .",
            ch: 'D D G A'})
    ];

    // After the leaderboard hit: a short bright groove in D.
    var BOARD_TAIL = song({id: 9, name: 'board', bpm: 120, spb: 4, bpb: 2, style: 'pop',
        mel: "d' - f#' - a' - d'' - | c#'' - a' - e' - a' -",
        ch: 'D A',
        sec: [{lead: 'pluck', l2: 'bell', o2: 12, l2v: 0.6, pad: 'saw', pump: 1, bass: 'off', dr: 'four'}]});

    var TRACKS = {
        lobby: LOBBY,
        question: QUESTION,
        final: FINAL,
        // Snare roll and riser for ~0.9 s, a hit when the rows move, then the tail.
        board: {
            bpm: 120, spb: 4,
            play: function (p, c, t, sd) {
                var N = 7;
                if (c === 0) {
                    riser(t, sd * N, 0.1, p.dr, 300, 6000);
                    PAD.strings([50, 57, 62, 66], t, sd * N, 0.03, p.h);
                }
                if (c < N) {
                    var k = (c + 1) / N;
                    snare(t, 0.08 + 0.3 * k * k, p.dr);
                    snare(t + sd / 2, 0.06 + 0.28 * k * k, p.dr);
                    if (c % 2 === 0) tom(t, 90, 0.2 + 0.3 * k, p.dr);
                    return;
                }
                if (c === N) {
                    boom(t, 0.8, p.dr);
                    kick(t, 0.8, p.out);
                    crash(t, 0.16, p.dr, 2);
                    PAD.brass([62, 66, 69, 74], t, 0.45, 0.1, p.h);
                }
                BOARD_TAIL.play(p, c - N, t, sd);
            }
        }
    };

    function stepDur(p) {
        var d = p.def, r = d.rate ? d.rate(p.count) : 1;
        return 60 / (d.bpm * r * (p.urgent ? d.urgent || 1 : 1)) / d.spb;
    }

    function schedule() {
        if (!ctx) return;
        var now = ctx.currentTime;
        playing = playing.filter(function (p) {
            if (p.end && p.end <= now) {
                urgentOff(p);
                try { p.out.disconnect(); p.h.disconnect(); } catch (e) { /* ignore */ }
                return false;
            }
            return true;
        });
        playing.forEach(function (p) {
            if (p.next < now - 0.25) p.next = now + 0.03;   // back from a pause
            while (p.next < now + LOOKAHEAD && (!p.end || p.next < p.end)) {
                var sd = stepDur(p);
                try { p.def.play(p, p.count, p.next, sd); } catch (e) { errors += 1; }
                p.count += 1;
                p.next += sd;
            }
        });
        if (beats.length > 64) beats = beats.slice(-32);
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

    function resolve() {
        var def = want.name && TRACKS.hasOwnProperty(want.name) ? TRACKS[want.name] : null;
        if (!def) return null;
        if (!def.length) return {def: def, v: 0};
        var n = def.length, v = +want.variant, last = lastVariant.hasOwnProperty(want.name) ? lastVariant[want.name] : -1;
        if (want.variant !== null && want.variant !== undefined && isFinite(v)) v = ((Math.floor(v) % n) + n) % n;
        else if (current && current.name === want.name) v = current.variant;
        else v = last < 0 ? Math.floor(Math.random() * n) : (last + 1) % n;
        return {def: def[v], v: v, multi: true};
    }

    // Per-track routing: out (dry) -> music bus; h (harmonic) and dr (drums) also feed the hall; L/R panned.
    function voiceBus(out) {
        var p = {out: out, h: gain(out), dr: gain(out)};
        send(p.h, 0.35);
        send(p.dr, 0.18);
        if (ctx.createStereoPanner) {
            p.L = ctx.createStereoPanner();
            p.L.pan.value = -0.35;
            p.R = ctx.createStereoPanner();
            p.R.pan.value = 0.35;
            p.L.connect(p.h);
            p.R.connect(p.h);
        } else {
            p.L = p.h;
            p.R = p.h;
        }
        return p;
    }

    function startMusic() {
        if (!ctx) return;
        var r = resolve(), level = (want.quiet ? 0.28 : 1) * (r && r.def.gain || 1);
        if (current && r && current.name === want.name && current.variant === r.v) {
            fadeTo(current.out.gain, level, 0.4);
            return;
        }
        var same = !!(current && r && current.name === want.name), keepUrgent = same && current.urgent;
        if (current) {
            fadeTo(current.out.gain, 0.0001, r ? 0.9 : 1.2);
            current.end = ctx.currentTime + (r ? 0.95 : 1.25);
            urgentOff(current);
            current = null;
        }
        if (!r) return;
        if (r.multi) lastVariant[want.name] = r.v;
        var out = ctx.createGain();
        out.gain.value = 0.0001;
        out.connect(bus.music);
        current = voiceBus(out);
        current.name = want.name;
        current.variant = r.v;
        current.def = r.def;
        current.count = 0;
        current.next = ctx.currentTime + 0.06;
        current.end = 0;
        current.urgent = false;
        fadeTo(out.gain, level, same ? 0.35 : want.name === 'board' ? 0.05 : 0.6);
        playing.push(current);
        if (keepUrgent) urgentOn(current);
        if (!timer) timer = setInterval(schedule, TICK_MS);
        schedule();
    }

    // Last seconds of a question: faster tempo, busier drums, a rising tension drone.
    function urgentOn(p) {
        p.urgent = true;
        if (p.ud || !p.def.tonic) return;
        var t = ctx.currentTime, g = ctx.createGain(), lp = filter('lowpass', 500, 2, g), os = [];
        g.gain.setValueAtTime(0.0001, t);
        g.gain.linearRampToValueAtTime(0.05, t + 1.5);
        g.connect(p.h);
        lp.frequency.setValueAtTime(500, t);
        lp.frequency.linearRampToValueAtTime(2500, t + 5);
        [p.def.tonic, p.def.tonic + 7, p.def.tonic + 12].forEach(function (m, i) {
            var o = ctx.createOscillator();
            o.type = 'sawtooth';
            o.frequency.value = mhz(m);
            o.detune.setValueAtTime(i * 3, t);
            o.detune.linearRampToValueAtTime(200 + i * 3, t + 5);
            o.connect(lp);
            o.start(t);
            o.stop(t + 9);
            os.push(o);
        });
        p.ud = {g: g, os: os};
    }
    function urgentOff(p) {
        p.urgent = false;
        if (!p.ud) return;
        var t = ctx.currentTime;
        try {
            fadeTo(p.ud.g.gain, 0.0001, 0.3);
            p.ud.os.forEach(function (o) { o.stop(t + 0.4); });
        } catch (e) { /* ignore */ }
        p.ud = null;
    }

    /* ---------------- effects ---------------- */

    var joinN = 0, answeredN = 0, PENTA = [0, 2, 4, 7, 9];
    function penta(k, base) { return base + PENTA[k % 5] + 12 * Math.floor(k / 5); }
    function chordAt(notes, t, ins, vol, out, spread) {
        notes.forEach(function (m, i) { I[ins](mhz(m), t + i * (spread || 0), 0.6, vol, out); });
    }
    // Drum roll that speeds up and gets louder from t0 to t1.
    function roll(t0, t1, v0, v1, o) {
        var tt = t0, dt = 0.09;
        while (tt < t1) {
            var k = (tt - t0) / (t1 - t0);
            snare(tt, v0 + (v1 - v0) * k * k, o);
            dt = Math.max(0.032, dt * 0.95);
            tt += dt;
        }
    }

    var SFX = {
        // Game start: a big ensemble drum hit ("ba-BOOM") instead of a gong.
        start: function (t, o, v) {
            tom(t, 125, 0.45, v);
            tom(t + 0.09, 90, 0.55, v);
            boom(t + 0.2, 1, v);
            kick(t + 0.2, 0.9, o);
            boom(t + 0.22, 0.6, v);
            crash(t + 0.2, 0.2, v, 2.5);
            riser(t + 0.25, 0.7, 0.05, v, 2000, 300);
            PAD.brass([43, 50, 55, 59, 62], t + 0.2, 0.9, 0.12, v);
        },
        // 3-2-1: a drum per number, higher as it gets closer; n = the number shown.
        count: function (t, o, v, n) {
            var f = n >= 3 ? 90 : n === 2 ? 125 : 170;
            tom(t, f, 0.5, v);
            kick(t, 0.5, o);
            wood(t, 1400 + (3 - Math.min(3, n)) * 250, 0.12, o);
            if (n === 1) riser(t + 0.2, 0.75, 0.06, v, 500, 8000);
        },
        // Answers open: an impact with a bright chord.
        go: function (t, o, v) {
            kick(t, 0.95, o);
            snare(t, 0.4, v);
            boom(t, 0.5, v);
            crash(t, 0.14, v, 1.6);
            PAD.saw([62, 67, 71, 74], t, 0.35, 0.03, v);
            hiss(t, 0.35, 0.06, v, 'bandpass', 3000, 0.8).frequency.exponentialRampToValueAtTime(9000, t + 0.3);
        },
        // Last seconds of a question: tick-tock, n seconds left.
        clock: function (t, o, v, n) {
            wood(t, n % 2 ? 1500 : 1150, 0.24 + (5 - Math.min(5, n)) * 0.04, o);
            if (n <= 3) kick(t, 0.25 + (3 - n) * 0.1, o);
        },
        // Time is up.
        timeup: function (t, o, v) {
            boom(t, 0.7, v);
            crash(t, 0.1, v, 1.2);
            tone('sawtooth', 220, t, 0.45, 0.06, filter('lowpass', 900, 1, v), 110);
        },
        tick: function (t, o) { wood(t, 1500, 0.15, o); },
        join: function (t, o, v) {
            var m = penta(joinN++ % 10, 72);
            tone('sine', mhz(m - 12), t, 0.08, 0.18, o, mhz(m), 0.002);
            I.bell(mhz(m), t + 0.03, 0.5, 0.12, v);
        },
        // A player's answer was taken.
        answer: function (t, o, v) {
            tone('sine', 420, t, 0.09, 0.3, o, 980, 0.002);
            I.bell(mhz(84), t + 0.06, 0.3, 0.07, v);
        },
        // Host screen: the "answered" counter went up.
        answered: function (t, o, v) {
            var m = penta(answeredN++ % 10, 67);
            I.pluck(mhz(m), t, 0.2, 0.13, v);
        },
        correct: function (t, o, v) {
            I.bell(mhz(76), t, 0.4, 0.14, v);
            I.bell(mhz(83), t + 0.1, 0.6, 0.16, v);
            chordAt([64, 67, 71, 76], t + 0.1, 'pluck', 0.06, v, 0.02);
            hiss(t + 0.1, 0.5, 0.04, v, 'highpass', 9000);
            kick(t + 0.1, 0.4, o);
        },
        wrong: function (t, o, v) {
            var lp = filter('lowpass', 1100, 1, o);
            tone('square', mhz(55), t, 0.18, 0.09, lp, mhz(54));
            tone('square', mhz(50), t + 0.2, 0.45, 0.09, lp, mhz(48));
            tom(t + 0.2, 80, 0.35, o);
        },
        streak: function (t, o, v) {
            [67, 71, 74, 79, 83].forEach(function (m, i) { I.pluck(mhz(m), t + i * 0.05, 0.2, 0.08, v); });
            riser(t, 0.3, 0.06, v, 800, 8000);
            I.bell(mhz(86), t + 0.28, 0.8, 0.15, v);
            for (var k = 0; k < 6; k++) hiss(t + 0.3 + k * 0.045 * (1 + hash(k)), 0.02, 0.05, v, 'bandpass', 2500 + 2000 * hash(k + 9), 3);
        },
        // Before the answer is shown: a short roll and a hit.
        reveal: function (t, o, v) {
            roll(t, t + 0.55, 0.05, 0.3, v);
            boom(t + 0.6, 0.7, v);
            kick(t + 0.6, 0.7, o);
            crash(t + 0.6, 0.12, v, 1.4);
            chordAt([74, 78, 81, 86], t + 0.6, 'bell', 0.06, v, 0.03);
        },
        // Rows overtaking each other on the leaderboard.
        rise: function (t, o, v) {
            hiss(t, 0.45, 0.2, v, 'bandpass', 600, 1.5, 0.3).frequency.exponentialRampToValueAtTime(6000, t + 0.4);
            tone('sine', 300, t, 0.35, 0.12, v, 900, 0.1);
        },
        // Numbers counting up for ms milliseconds (same easing as the counter): ticks, then a ding.
        count_up: function (t, o, v, ms) {
            var dur = Math.max(0.3, (ms || 900) / 1000), N = Math.min(22, Math.round(dur * 16));
            for (var k = 1; k <= N; k++) {
                var x = 1 - Math.pow(1 - k / N, 1 / 3), f = 1100 + 900 * (k / N);
                tone('triangle', f, t + x * dur, 0.025, 0.07, o, 0, 0.001);
            }
            I.bell(mhz(88), t + dur, 0.5, 0.1, v);
        },
        tap: function (t, o) { tone('sine', 620, t, 0.03, 0.14, o, 440); },
        // End of the game, synced with the podium: 3rd place at 1.0 s, 2nd at 2.0 s, 1st at 3.3 s.
        finale: function (t, o, v) {
            roll(t, t + 1, 0.04, 0.3, v);
            boom(t + 1, 0.6, v);
            crash(t + 1, 0.08, v, 0.8);
            PAD.brass([55, 62, 67], t + 1, 0.4, 0.08, v);
            roll(t + 1.25, t + 2, 0.05, 0.3, v);
            boom(t + 2, 0.7, v);
            crash(t + 2, 0.1, v, 0.8);
            PAD.brass([57, 64, 69], t + 2, 0.4, 0.09, v);
            roll(t + 2.2, t + 3.3, 0.05, 0.42, v);
            riser(t + 2.3, 1, 0.07, v, 400, 8000);
            var T = t + 3.3;
            boom(T, 1, v);
            kick(T, 1, o);
            boom(T + 0.03, 0.7, v);
            crash(T, 0.22, v, 3);
            PAD.brass([50, 62, 66, 69, 74], T, 1.6, 0.14, v);
            PAD.choir([62, 66, 69, 74], T, 1.8, 0.06, v);
            [74, 78, 81, 86, 90].forEach(function (m, i) { I.bell(mhz(m), T + 0.05 + i * 0.06, 1, 0.08, v); });
        }
    };
    SFX.gong = SFX.start;
    SFX.fanfare = SFX.finale;

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

    function list(arr) { return arr.map(function (d) { return {name: d.v.name, by: d.v.by, style: d.v.style || ''}; }); }

    window.QuizAudio = {
        available: !!AC,
        variants: {question: QUESTION.length, lobby: LOBBY.length, final: FINAL.length},
        tracks: {question: list(QUESTION), lobby: list(LOBBY), final: list(FINAL)},
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
        // music('question', {variant: n}) picks n % count; without a variant the next one in turn.
        music: function (name, opts) {
            want = {name: name || null, quiet: !!(opts && opts.quiet), variant: opts && opts.variant !== undefined ? opts.variant : null};
            try { if (ctx && unlocked) startMusic(); } catch (e) { /* ignore */ }
        },
        urgent: function (on) {
            try {
                if (!ctx || !current || current.name !== 'question') return;
                if (on && !current.urgent) urgentOn(current);
                else if (!on && current.urgent) urgentOff(current);
            } catch (e) { /* ignore */ }
        },
        state: function () {
            return {name: current ? current.name : null, variant: current ? current.variant : null,
                title: current && current.def.v ? current.def.v.name : null,
                urgent: !!(current && current.urgent), errors: errors, bad: BAD.slice()};
        },
        // 0..1: how hard the last kick or drum hit, decaying; for visuals in time with the music.
        beat: function () {
            if (!ctx || muted || ctx.state !== 'running') return 0;
            var now = ctx.currentTime, best = 0;
            for (var i = beats.length - 1; i >= 0 && i >= beats.length - 8; i--) {
                var b = beats[i], dt = now - b.t;
                if (dt >= 0 && dt < 0.5) best = Math.max(best, b.v * Math.exp(-dt * 7));
            }
            return best;
        },
        sfx: function (name, arg) {
            if (!ctx || !unlocked || muted || !SFX.hasOwnProperty(name)) return;
            try { SFX[name](ctx.currentTime + 0.01, bus.sfx, bus.sfxv, arg); } catch (e) { errors += 1; }
        },
        vibrate: function (pattern) {
            if (muted || !navigator.vibrate) return false;
            try { return navigator.vibrate(pattern); } catch (e) { return false; }
        },
        _tick: function () { schedule(); },
        _ctx: function () { return ctx; },
        _bus: function () { return bus; }
    };
})();
