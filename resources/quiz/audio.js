/* Quiz sounds and music. Everything is synthesized with the Web Audio API: no audio files.
 * Music: arranged public-domain classical themes (orchestral, organ, electronic) plus original
 * Kyrgyz-flavoured pieces (komuz, temir komuz). Gong, drums and strings are synthesized too.
 * window.QuizAudio: unlock, setMuted, isMuted, setVolume, getVolume, music, urgent, sfx, vibrate, state. */
(function () {
    'use strict';

    var AC = window.AudioContext || window.webkitAudioContext;
    var ctx = null, bus = {}, noise = null, unlocked = false;
    var muted = false, volume = 0.8;
    var want = {name: null, quiet: false, variant: null}, current = null, playing = [], timer = null;
    var lastVariant = -1, voices = 0, MAX_VOICES = 48;
    var LOOKAHEAD = 0.12, TICK_MS = 25;

    try {
        muted = localStorage.getItem('qz-muted') === '1';
        var stored = parseFloat(localStorage.getItem('qz-volume'));
        if (stored >= 0 && stored <= 1) volume = stored;
    } catch (e) { /* storage blocked */ }

    function save(key, value) { try { localStorage.setItem(key, value); } catch (e) { /* ignore */ } }
    function noop() {}

    /* ---------------- notes, modes, random ---------------- */

    function mhz(m) { return 440 * Math.pow(2, (m - 69) / 12); }

    var ION = [0, 2, 4, 5, 7, 9, 11], MIX = [0, 2, 4, 5, 7, 9, 10],
        DOR = [0, 2, 3, 5, 7, 9, 10], AEO = [0, 2, 3, 5, 7, 8, 10];

    // Deterministic generators: the same step always gets the same humanization.
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

    // Melody, one token per step: scale degree "1".."7" or note name "c#" / "eb" (octave 4);
    // ' raises, , lowers an octave, '-' holds, '.' rests. len = steps the note lasts.
    var SEMI = {c: 0, d: 2, e: 4, f: 5, g: 7, a: 9, b: 11};
    function parseMel(text, base, mode) {
        var out = {note: [], fresh: [], len: []}, last = base;
        text.split(/[\s|]+/).forEach(function (s) {
            if (!s) return;
            var isNew = s !== '-' && s !== '.', c = s.charAt(0), j = 1;
            if (s === '.') last = null;
            else if (isNew) {
                if (SEMI.hasOwnProperty(c)) {
                    last = 60 + SEMI[c];
                    if (s.charAt(1) === '#') { last += 1; j = 2; } else if (s.charAt(1) === 'b') { last -= 1; j = 2; }
                } else {
                    last = base + mode[+c - 1];
                }
                for (; j < s.length; j++) last += s.charAt(j) === "'" ? 12 : -12;
            }
            out.note.push(last);
            out.fresh.push(isNew);
        });
        for (var i = out.note.length - 1; i >= 0; i--) {
            var k = i + 1, cont = k < out.note.length && !out.fresh[k] && out.note[k] !== null;
            out.len[i] = 1 + (cont ? out.len[k] : 0);
        }
        return out;
    }
    // Chord symbol "Bm", "F#", "G7", "C5" -> root (A2..G#3) and pad voicing.
    function chord(sym) {
        var m = /^([A-G])([#b]?)(m|5|7)?$/.exec(sym), r = 48 + SEMI[m[1].toLowerCase()] + (m[2] === '#' ? 1 : m[2] === 'b' ? -1 : 0);
        if (r > 56) r -= 12;
        var q = m[3], n = [r, r + 7, r + 12];
        if (q !== '5') n.push(r + (q === 'm' ? 15 : 16));
        if (q === '7') n.push(r + 10);
        return {r: r, n: n};
    }
    // Chord root offset for a scale degree, kept within a fifth of the tonic.
    function shift(mode, deg) { var s = mode[deg]; return s > 6 ? s - 12 : s; }

    /* ---------------- engine ---------------- */

    function init() {
        if (ctx || !AC) return ctx;
        try {
            ctx = new AC();
            var comp = ctx.createDynamicsCompressor();
            comp.threshold.value = -14;
            comp.knee.value = 10;
            comp.ratio.value = 6;
            comp.attack.value = 0.003;
            comp.release.value = 0.2;
            bus.master = ctx.createGain();
            comp.connect(bus.master);
            bus.master.connect(ctx.destination);
            bus.music = ctx.createGain();
            bus.music.gain.value = 0.5;
            bus.music.connect(comp);
            bus.sfx = ctx.createGain();
            bus.sfx.gain.value = 0.9;
            bus.sfx.connect(comp);
            bus.kz = body(bus.sfx);
            noise = ctx.createBuffer(1, ctx.sampleRate, ctx.sampleRate);
            var d = noise.getChannelData(0), r = rng(7);
            for (var i = 0; i < d.length; i++) d[i] = r() * 2 - 1;
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

    // Filtered noise burst from the shared buffer; returns the filter so callers can sweep it.
    function hiss(t, dur, vol, out, type, freq, q) {
        var s = ctx.createBufferSource(), g = ctx.createGain(), f = filter(type, freq, q, g);
        s.buffer = noise;
        env(g, t, 0.002, vol, dur);
        s.connect(f);
        g.connect(out);
        s.start(t, (t * 7.31) % 0.5);
        s.stop(t + dur + 0.05);
        return f;
    }

    // Dobulbas-like frame drum: low membrane tone with a soft thump; slap = rim/finger stroke.
    function drum(t, vol, out) {
        var o = ctx.createOscillator(), g = ctx.createGain();
        o.frequency.setValueAtTime(122, t);
        o.frequency.exponentialRampToValueAtTime(74, t + 0.16);
        env(g, t, 0.003, vol, 0.3);
        o.connect(g);
        g.connect(out);
        o.start(t);
        o.stop(t + 0.36);
        hiss(t, 0.05, vol * 0.4, out, 'lowpass', 600, 0.8);
    }
    function slap(t, vol, out) {
        hiss(t, 0.06, vol, out, 'bandpass', 1700, 1.2);
        tone('triangle', 280, t, 0.04, vol * 0.3, out, 210, 0.002);
    }

    // Wooden body of the komuz: shared by all strings of one track.
    function body(out) {
        var hp = filter('highpass', 80, 0.7), p1 = filter('peaking', 250, 1.3), p2 = filter('peaking', 1300, 1.1),
            lp = filter('lowpass', 3400, 0.6);
        p1.gain.value = 5;
        p2.gain.value = 3;
        hp.connect(p1);
        p1.connect(p2);
        p2.connect(lp);
        lp.connect(out);
        return hp;
    }

    // Karplus-Strong string rendered once per period into a low-rate buffer (warm, small).
    var KS_SR = 22050, ksCache = {};
    function ksBuffer(f) {
        var n = Math.max(4, Math.floor(KS_SR / f - 0.5)), c = ksCache[n];
        if (!c) {
            var low = f < 200, len = Math.floor(KS_SR * (low ? 1.5 : 1.1)),
                buf = ctx.createBuffer(1, len, KS_SR), d = buf.getChannelData(0),
                r = rng(n * 7919), i, lp = 0, mean = 0, peak = 0, k = Math.max(1, Math.round(n * 0.14)),
                loss = Math.pow(0.001, 1 / ((low ? 1.7 : 1.15) * f));
            for (i = 0; i < n; i++) { lp += (r() * 2 - 1 - lp) * 0.5; d[i] = lp; mean += lp; }
            mean /= n;
            for (i = 0; i < n; i++) d[i] -= mean;
            for (i = n - 1; i >= k; i--) d[i] -= 0.7 * d[i - k];   // pluck position: hollow, not bell-like
            for (i = 0; i < n; i++) peak = Math.max(peak, Math.abs(d[i]));
            for (i = 0; i < n; i++) d[i] *= 0.9 / (peak || 1);
            d[n] = loss * 0.5 * (d[0] + d[n - 1]);
            for (i = n + 1; i < len; i++) d[i] = loss * 0.5 * (d[i - n] + d[i - n - 1]);
            var fade = Math.floor(KS_SR * 0.08);
            for (i = 0; i < fade; i++) d[len - 1 - i] *= i / fade;
            c = ksCache[n] = {buf: buf, n: n};
        }
        return {buf: c.buf, rate: f * (c.n + 0.5) / KS_SR};
    }

    // One plucked string. strs/key: per-track string slots, a new pluck damps the old one on that string.
    function pluck(f, t, vol, out, ring, strs, key) {
        if (strs && voices > MAX_VOICES && vol < 0.3) return;
        var b = ksBuffer(f), s = ctx.createBufferSource(), g = ctx.createGain();
        s.buffer = b.buf;
        s.playbackRate.value = b.rate;
        g.gain.setValueAtTime(0, t);
        g.gain.linearRampToValueAtTime(vol, t + 0.004);
        s.connect(g);
        g.connect(out);
        voices += 1;
        s.onended = function () {
            voices -= 1;
            try { g.disconnect(); s.disconnect(); } catch (e) { /* ignore */ }
        };
        s.start(t);
        var v = {s: s, g: g, t: t};
        if (ring) damp(v, t + ring);
        if (strs) {
            if (strs[key]) damp(strs[key], t);
            strs[key] = v;
        }
    }
    function damp(v, t) {
        if (v.done) return;
        v.done = true;
        t = Math.max(t, v.t + 0.01);
        try {
            v.g.gain.cancelScheduledValues(t);
            v.g.gain.setTargetAtTime(0, t, 0.015);
            v.s.stop(t + 0.12);
        } catch (e) { /* ignore */ }
    }

    // Strum three strings in physical order; dir < 0 is an up-stroke over the two upper strings.
    function strum(p, notes, t, vol, dir, spread) {
        var order = dir < 0 ? [2, 1] : [0, 1, 2];
        for (var i = 0; i < order.length; i++) {
            var k = order[i];
            pluck(mhz(notes[k]), t + i * spread, vol * (k === 1 ? 1 : 0.8), p.kz, 0, p.str, k);
        }
        if (dir > 0 && vol > 0.3) hiss(t, 0.012, vol * 0.05, p.kz, 'highpass', 2600);   // nail on the strings
    }

    // Envelope with attack, sustain and release, safe for short notes.
    function hold(g, t, dur, vol, att, rel) {
        att = Math.min(att, dur * 0.3);
        rel = Math.min(rel, dur * 0.4);
        g.gain.setValueAtTime(0.0001, t);
        g.gain.linearRampToValueAtTime(vol, t + att);
        g.gain.setValueAtTime(vol, t + dur - rel);
        g.gain.linearRampToValueAtTime(0.0001, t + dur);
    }
    function osc(type, f, t, end, out, detune) {
        var o = ctx.createOscillator();
        o.type = type;
        o.frequency.value = f;
        if (detune) o.detune.value = detune;
        o.connect(out);
        o.start(t);
        o.stop(end);
        return o;
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

    // Chopo-choor: clay flute, nearly pure tone with a breathy onset.
    function choor(f, t, dur, vol, out) {
        var g = ctx.createGain(), end = t + dur + 0.05;
        hold(g, t, dur, vol, 0.2, 0.4);
        g.connect(out);
        vib(osc('sine', f, t, end, g), t, f, 0.005, 4.6, 0.4, end);
        hiss(t, Math.min(0.3, dur), vol * 0.4, out, 'bandpass', f * 2, 2.5);
    }

    // Bowed strings (also the kyl kyyak colour): detuned saws, nasal peak, delayed vibrato, bow noise.
    function bow(f, t, dur, vol, out) {
        var g = ctx.createGain(), pk = filter('peaking', 1100, 1.2), lp = filter('lowpass', 2600, 0.7, g), end = t + dur + 0.05;
        pk.gain.value = 6;
        pk.connect(lp);
        hold(g, t, dur, vol, 0.08, 0.15);
        g.connect(out);
        vib(osc('sawtooth', f, t, end, pk, -7), t, f, 0.006, 5.4, 0.35, end);
        osc('sawtooth', f, t, end, pk, 7);
        hiss(t, dur, vol * 0.2, out, 'bandpass', 2800, 1.5);
    }

    // Warm horn section: saws through a filter that opens on the attack.
    function horn(f, t, dur, vol, out) {
        var g = ctx.createGain(), lp = filter('lowpass', 500, 0.9, g), end = t + dur + 0.05;
        lp.frequency.setValueAtTime(450, t);
        lp.frequency.linearRampToValueAtTime(1500, t + 0.07);
        lp.frequency.setTargetAtTime(1000, t + 0.1, 0.3);
        hold(g, t, dur, vol, 0.04, 0.12);
        g.connect(out);
        osc('sawtooth', f, t, end, lp, -6);
        osc('sawtooth', f, t, end, lp, 6);
    }

    // Pipe organ: square fundamental plus octave and twelfth.
    function organ(f, t, dur, vol, out) {
        var g = ctx.createGain(), lp = filter('lowpass', 2400, 0.7, g), h = ctx.createGain(), end = t + dur + 0.05;
        hold(g, t, dur, vol, 0.03, 0.08);
        g.connect(out);
        h.gain.value = 0.6;
        h.connect(g);
        osc('square', f, t, end, lp);
        osc('sine', f * 2, t, end, h);
        osc('sine', f * 3, t, end, h);
    }

    // Marimba-like mallet: fundamental, the 4x bar partial and a short click.
    function mallet(f, t, vol, out, dec) {
        tone('sine', f, t, dec, vol, out, 0, 0.003);
        tone('sine', f * 3.99, t, dec * 0.22, vol * 0.25, out, 0, 0.002);
        tone('sine', f * 9.8, t, 0.04, vol * 0.06, out, 0, 0.001);
    }

    // Temir komuz (jaw harp): a low reed tone with a sweeping formant picking out the melody harmonic.
    function jaw(f0, fm, t, dur, vol, out) {
        var g = ctx.createGain(), bp = filter('bandpass', fm, 14), bg = ctx.createGain(), lp = filter('lowpass', 650, 0.7, g),
            o = osc('sawtooth', f0, t, t + dur + 0.05, bp);
        bg.gain.value = 5;
        bp.connect(bg);
        bg.connect(g);
        o.connect(lp);
        bp.frequency.setValueAtTime(fm * 0.72, t);
        bp.frequency.exponentialRampToValueAtTime(fm, t + 0.06);
        env(g, t, 0.004, vol, dur);
        g.connect(out);
    }

    // Drums: taiko, electronic kit, noise riser.
    function taiko(t, vol, out) {
        var o = ctx.createOscillator(), g = ctx.createGain();
        o.frequency.setValueAtTime(96, t);
        o.frequency.exponentialRampToValueAtTime(46, t + 0.3);
        env(g, t, 0.004, vol, 0.65);
        o.connect(g);
        g.connect(out);
        o.start(t);
        o.stop(t + 0.72);
        hiss(t, 0.14, vol * 0.5, out, 'lowpass', 900, 0.7);
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
    function hat(t, vol, out) { hiss(t, 0.035, vol, out, 'highpass', 7500); }
    function clap(t, vol, out) {
        hiss(t, 0.03, vol, out, 'bandpass', 1300, 0.9);
        hiss(t + 0.012, 0.12, vol * 0.8, out, 'bandpass', 1300, 0.9);
    }
    function riser(t, dur, vol, out) {
        var s = ctx.createBufferSource(), g = ctx.createGain(), f = filter('bandpass', 400, 2, g);
        s.buffer = noise;
        s.loop = true;
        f.frequency.setValueAtTime(400, t);
        f.frequency.exponentialRampToValueAtTime(6000, t + dur);
        g.gain.setValueAtTime(0.0001, t);
        g.gain.exponentialRampToValueAtTime(vol, t + dur);
        g.gain.linearRampToValueAtTime(0.0001, t + dur + 0.04);
        s.connect(f);
        g.connect(out);
        s.start(t);
        s.stop(t + dur + 0.06);
    }
    function bass(f, t, dur, vol, out) {
        var g = ctx.createGain(), lp = filter('lowpass', 700, 2, g);
        lp.frequency.setValueAtTime(900, t);
        lp.frequency.exponentialRampToValueAtTime(200, t + dur);
        env(g, t, 0.005, vol, dur);
        g.connect(out);
        osc('sawtooth', f, t, t + dur + 0.05, lp);
    }

    // Strings pad: detuned saws through a filter that opens over the attack.
    function strings(notes, t, dur, vol, out, att) {
        var g = ctx.createGain(), lp = filter('lowpass', 500, 0.8, g), end = t + dur + 0.05;
        lp.frequency.setValueAtTime(500, t);
        lp.frequency.linearRampToValueAtTime(2600, t + att);
        g.gain.setValueAtTime(0.0001, t);
        g.gain.linearRampToValueAtTime(vol, t + att);
        g.gain.setValueAtTime(vol, t + Math.max(att, dur - 0.4));
        g.gain.linearRampToValueAtTime(0.0001, t + dur);
        g.connect(out);
        notes.forEach(function (m, i) {
            osc('sawtooth', mhz(m), t, end, lp, -8 + i);
            osc('sawtooth', mhz(m), t, end, lp, 8 - i);
        });
    }

    // Gong: inharmonic partials in slightly detuned pairs (beating), slow shimmer, soft mallet thump.
    function gong(t, vol, out, len) {
        var R = [1, 1.48, 2.03, 2.76, 3.4, 4.17, 5.43], g = ctx.createGain(), lfo = ctx.createOscillator(), lg = ctx.createGain();
        g.gain.value = vol;
        g.connect(out);
        lfo.frequency.value = 0.31;
        lg.gain.value = 7;
        lfo.connect(lg);
        R.forEach(function (r, i) {
            [-1, 1].forEach(function (sg) {
                var a = ctx.createGain(), bloom = 0.012 + 0.03 * i, dec = len * 9 / (1 + i * 0.35),
                    o = osc('sine', 80 * r + sg * (0.35 + 0.18 * i), t, t + bloom + dec + 0.05, a);
                lg.connect(o.detune);
                a.gain.setValueAtTime(0.0001, t);
                a.gain.linearRampToValueAtTime(0.2 / (1 + i * 0.25), t + bloom);
                a.gain.exponentialRampToValueAtTime(0.0001, t + bloom + dec);
                a.connect(g);
            });
        });
        lfo.start(t);
        lfo.stop(t + 9 * len + 0.3);
        hiss(t, 0.12, vol * 0.45, out, 'lowpass', 280, 0.8);
        tone('sine', 56, t, 0.3, vol * 0.5, out, 44, 0.008);
    }

    /* ---------------- music ---------------- */

    var URG_P = {6: 'DuDuDu', 8: 'DuDuDuDu'}, URG_D = {6: 'BtrBtr', 8: 'BtrtBtrr'}, FILL = {6: 'Btrtrr', 8: 'B.trtrrr'};

    // Drum codes: B/b frame drum, t slap, r double slap, k shaker, T/U taiko, S orchestral stab,
    // R riser, K kick, X kick+clap, h hat.
    function hit(p, code, t, sd, dv, acc, cd) {
        if (!code || code === '.') return;
        var o = p.out;
        if (code === 'B') drum(t, 0.5 * dv, o);
        else if (code === 'b') drum(t, 0.28 * dv, o);
        else if (code === 't') slap(t, 0.13 * dv * acc, o);
        else if (code === 'r') { slap(t, 0.1 * dv, o); slap(t + sd / 2, 0.08 * dv, o); }
        else if (code === 'k') hiss(t, 0.05, 0.05 * dv * acc, o, 'bandpass', 6500, 1.2);
        else if (code === 'T' || code === 'U') taiko(t, (code === 'T' ? 0.8 : 0.45) * dv * acc, o);
        else if (code === 'S') {
            taiko(t, 0.7 * dv, o);
            if (cd) strings(cd.n.map(function (m) { return m + 12; }), t, 0.32, 0.07 * dv, o, 0.008);
        }
        else if (code === 'R') riser(t, sd * 8, 0.12 * dv, o);
        else if (code === 'h') hat(t, 0.045 * dv * acc, o);
        else if (code === 'K' || code === 'X') {
            kick(t, 0.75 * dv, o);
            if (code === 'X') clap(t, 0.16 * dv, o);
            if (p.pump) {   // sidechain-like pumping
                p.pump.gain.setValueAtTime(0.25, t);
                p.pump.gain.linearRampToValueAtTime(1, t + Math.min(0.3, sd * 3));
            }
        }
    }

    // Original Kyrgyz-flavoured pieces: melody in scale degrees over open-string drones.
    // v: bpm, spb (steps per beat), bpb (beats per bar), tonic, d (second drone), mode, mo (melody octave),
    // mel, ch (chord degree per bar), p / p2 / pc (strokes, second pass, cadence bar), dr (drums).
    var STYLE = {
        komuz: function (p, v, s, t) {
            var ch = s.ch, notes = [s.a, s.note, s.a + v.d], h = s.acc;
            if (ch === 'D' || ch === 'd') strum(p, notes, t, (ch === 'D' ? 0.46 : 0.3) * h, 1, ch === 'D' ? 0.016 : 0.01);
            else if (ch === 'u') strum(p, notes, t, 0.24 * h, -1, 0.008);
            else if (s.fresh) pluck(mhz(s.note), t, 0.36 * h, p.kz, 0, p.str, 1);
        },
        jaw: function (p, v, s, t, sd) {
            var ch = s.ch, k = ch === 'D' ? 1 : ch === 'd' ? 0.7 : ch === 'u' ? 0.5 : s.fresh ? 0.6 : 0;
            if (k) jaw(mhz(v.tonic), mhz(s.note), t, sd * (ch === 'D' ? 4 : 1.6), 0.22 * k * s.acc, p.out);
        }
    };
    function piece(v) {
        var mel = parseMel(v.mel, v.tonic + 12 * v.mo, v.mode), steps = v.spb * v.bpb, L = mel.note.length,
            bars = L / steps, play = STYLE[v.style || 'komuz'];
        return {
            bpm: v.bpm, spb: v.spb, urgent: 1.12, v: v,
            play: function (p, c, t, sd) {
                var i = c % L, pass = Math.floor(c / L) % 2, bar = Math.floor(i / steps), pos = i % steps, u = p.urgent,
                    pat = u ? URG_P[steps] : bar % 4 === 3 ? v.pc : pass && v.p2 ? v.p2 : v.p,
                    s = {note: mel.note[i], fresh: mel.fresh[i], ch: pat.charAt(pos), acc: 0.88 + 0.24 * hash(c * 7 + v.id * 131),
                        a: v.tonic + (v.ch ? shift(v.mode, v.ch[bar % v.ch.length]) : 0)};
                play(p, v, s, t, sd);
                hit(p, (u ? URG_D[steps] : pass && bar === bars - 1 ? FILL[steps] : v.dr).charAt(pos), t, sd, 1, s.acc);
            }
        };
    }

    function lead(name, m, t, dur, vol, p, dst) {
        var f = mhz(m);
        if (name === 'pizz') pluck(f, t, 0.5 * vol, p.kz, Math.min(dur, 0.45));
        else if (name === 'bow') bow(f, t, dur + 0.04, 0.12 * vol, dst);
        else if (name === 'horn') horn(f, t, dur, 0.1 * vol, dst);
        else if (name === 'organ') organ(f, t, dur, 0.07 * vol, dst);
        else if (name === 'mallet') mallet(f, t, 0.28 * vol, dst, 0.5);
        else if (name === 'choor') choor(f, t, dur, 0.09 * vol, dst);
        else if (name === 'synth') {
            if (!p.alp) p.alp = filter('lowpass', 2000, 1.2, dst);
            tone('sawtooth', f, t, dur * 0.9, 0.07 * vol, p.alp);
            tone('square', f * 1.004, t, dur * 0.9, 0.04 * vol, p.alp);
        }
    }
    // Urgent drums for a theme: fill the gaps with taps.
    function dense(s, electro) {
        var o = '';
        for (var k = 0; k < s.length; k++) o += s.charAt(k) !== '.' ? s.charAt(k) : electro ? 'h' : k % 2 ? 'k' : 't';
        return o;
    }

    // Arranged public-domain theme. Absolute-note melody repeated per section with its own
    // orchestration. v: bpm, spb, bpb, tonic (urgent drone), mel, ch (chords, 1+ per bar), bass ('saw'
    // or pizzicato), pump (electronic sidechain), sec: [{o, lead, l2, o2, pad, bp, arp, dr, fill}].
    function theme(v) {
        var mel = parseMel(v.mel, 60, ION), L = mel.note.length, steps = v.spb * v.bpb, bars = L / steps,
            chs = v.ch.split(' ').map(chord), slot = L / chs.length, total = L * v.sec.length;
        v.sec.forEach(function (s) { s.du = dense(s.dr, v.pump); });
        return {
            bpm: v.bpm, spb: v.spb, urgent: 1.12, v: v,
            play: function (p, c, t, sd) {
                var i = c % total, sec = v.sec[Math.floor(i / L)], j = i % L, bar = Math.floor(j / steps), pos = j % steps,
                    acc = 0.88 + 0.24 * hash(c * 7 + v.id * 131), cd = chs[Math.floor(j / slot)], vol = v.vol || 1, dst = p.out;
                if (v.pump && !p.pump) {
                    p.pump = ctx.createGain();
                    p.pump.connect(p.out);
                }
                if (p.pump) dst = p.pump;
                if (sec.pad && j % slot === 0) strings(cd.n, t, slot * sd + 0.35, 0.03 * vol * sec.pad, dst, Math.min(0.3, slot * sd * 0.3));
                var b = (sec.bp || '').charAt(pos);
                if (b === 'x' || b === 'o') {
                    if (v.bass === 'saw') bass(mhz(cd.r - 12 + (b === 'o' ? 12 : 0)), t, sd * 1.6, 0.3 * vol, dst);
                    else pluck(mhz(cd.r + (b === 'o' ? 12 : 0)), t, 0.42 * vol, p.kz, sd * 1.8);
                }
                if (sec.arp && j % 2 === 0) {
                    var an = cd.n[1 + (j / 2) % (cd.n.length - 1)] + 12;
                    if (sec.arp === 'synth') tone('square', mhz(an), t, 0.1, 0.03 * acc * vol, dst, 0, 0.003);
                    else mallet(mhz(an), t, 0.08 * acc * vol * (sec.av || 1), dst, 0.4);
                }
                if (mel.fresh[j]) {
                    var dur = mel.len[j] * sd;
                    lead(sec.lead, mel.note[j] + sec.o, t, dur, acc * vol, p, dst);
                    if (sec.l2) lead(sec.l2, mel.note[j] + sec.o2, t, dur, acc * vol * 0.8, p, dst);
                }
                var dp = p.urgent ? sec.du : bar === bars - 1 && sec.fill ? sec.fill : sec.dr;
                hit(p, dp.charAt(pos), t, sd, (v.dv || 1) * vol, acc, cd);
            }
        };
    }
    // Steps string with a token at the given positions, '-' elsewhere.
    function at(n, pos, tok, fill) {
        var a = [];
        for (var k = 0; k < n; k++) a.push(pos.indexOf(k) >= 0 ? tok : fill);
        return a.join(fill === '-' ? ' ' : '');
    }
    function times(s, n) { return new Array(n + 1).join(s + ' '); }

    var MARS = [0, 2, 4, 6, 12, 18, 21, 24];   // 5/4 ostinato: triplet, two quarters, two eighths, quarter

    var QUESTION = [
        // Grieg, In the Hall of the Mountain King: pizzicato, then strings, then horns and taiko
        theme({id: 20, bpm: 132, spb: 2, bpb: 4, tonic: 47,
            mel: 'b, c# d e f# d f# - | f c# f - e c e - | b, c# d e f# d f# b | a f# d f# a - - -',
            ch: 'B5 B5 C#5 C5 B5 B5 D D',
            sec: [{o: 0, lead: 'pizz', bp: 'x.x.x.x.', dr: 'U.......'},
                {o: 0, lead: 'pizz', l2: 'bow', o2: 12, pad: 1, bp: 'x.x.x.x.', dr: 'U...U...'},
                {o: 12, lead: 'horn', l2: 'bow', o2: 0, pad: 1.3, bp: 'xoxoxoxo', dr: 'T.tkT.tk', fill: 'T.T.TRTS'}]}),
        // Original: komuz, D Dorian, 6/8 gallop
        piece({id: 10, bpm: 116, spb: 3, bpb: 2, tonic: 50, d: 7, mode: DOR, mo: 1,
            mel: '1 - 1 5 - 4 | 3 - 4 5 - - | 5 5 6 5 - 4 | 3 - 2 1 - - |' +
                 '4 - 4 1\' - 7 | 6 - 5 4 - 5 | 3 3 4 2 - 7, | 1 - - 5, - -',
            ch: [0, 0, 0, 0, 3, 3, 6, 0], p: 'D.uDdu', p2: 'D.uDuu', pc: 'D.uD..', dr: 'B.tb.t'}),
        // Mozart, Rondo alla Turca: electronic, four on the floor
        theme({id: 21, bpm: 124, spb: 4, bpb: 2, tonic: 45, bass: 'saw', pump: 1,
            mel: 'b a g# a c\' - d\' c\' | b c\' e\' - f\' e\' d#\' e\' | b\' a\' g#\' a\' b\' a\' g#\' a\' | c\'\' - - - a\' - b\' -',
            ch: 'Am Am Am E Am E Am E',
            sec: [{o: -12, lead: 'mallet', bp: 'x.o.x.o.', arp: 'synth', dr: 'K.h.K.h.'},
                {o: -12, lead: 'synth', l2: 'mallet', o2: 0, pad: 0.8, bp: 'xoxoxoxo', arp: 'synth', dr: 'K.hhX.hh', fill: 'K.hhXRXX'}]}),
        // Beethoven, Symphony No. 5 opening: orchestral hits and taiko
        theme({id: 22, bpm: 112, spb: 2, bpb: 2, tonic: 48,
            mel: '. g g g | eb - - - | . f f f | d - - - | . g g g | eb . ab ab | ab g . eb\' | eb\' eb\' c\' -',
            ch: 'Cm Cm G G Cm Ab Fm Cm',
            sec: [{o: 0, lead: 'horn', l2: 'bow', o2: 12, pad: 1, bp: '.xxx', dr: 'T...'},
                {o: 12, lead: 'bow', l2: 'horn', o2: 0, pad: 1.3, bp: 'xxxx', dr: 'ThUh', fill: 'TRTS'}]}),
        // Offenbach, Galop infernal (can-can): xylophone galop, then strings
        theme({id: 23, bpm: 144, spb: 2, bpb: 2, tonic: 48,
            mel: 'c - - - | d f e d | g - g - | g a e f | d - d - | d f e d | c c\' b a | g f e d',
            ch: 'C G7 C F G7 G7 C G7',
            sec: [{o: 12, lead: 'mallet', bp: 'x.o.', dr: 'Bktk'},
                {o: 12, lead: 'bow', l2: 'mallet', o2: 12, pad: 0.8, bp: 'x.o.', dr: 'Tktk', fill: 'TtTS'}]}),
        // Original: temir komuz (jaw harp), G Mixolydian, 2/4 long-short-short
        piece({id: 11, style: 'jaw', bpm: 128, spb: 4, bpb: 2, tonic: 43, d: 7, mode: MIX, mo: 2,
            mel: '1 - 1 1 5 - 4 3 | 2 - 3 4 5 - - - | 6 - 5 4 5 - 4 3 | 2 - 1 7, 1 - - - |' +
                 '4 - 4 4 1\' - 7 6 | 5 - 6 7 1\' - - - | 7 - 6 5 4 - 3 2 | 1 - 5, - 1 - - -',
            p: 'D.udD.ud', p2: 'D.udDudu', pc: 'D.udD...', dr: 'B..tB.t.'}),
        // Holst, Mars: the 5/4 ostinato on G under rising string chords
        theme({id: 24, bpm: 150, spb: 6, bpb: 5, tonic: 43,
            mel: times(at(30, MARS, 'g,', '-'), 4),
            ch: 'G5 G5 Ab5 G5',
            sec: [{o: 0, lead: 'pizz', pad: 0.8, bp: at(30, MARS, 'x', '.'), dr: at(30, [0], 'U', '.')},
                {o: 0, lead: 'pizz', l2: 'horn', o2: 12, pad: 1.2, bp: at(30, MARS, 'x', '.'), dr: at(30, MARS, 'T', '.'),
                    fill: at(30, [0, 2, 4, 6, 12, 18, 24], 'T', '.').slice(0, 24) + 'R..S..'}]}),
        // Beethoven, Fur Elise: marimba over a soft electronic beat
        theme({id: 25, bpm: 140, spb: 2, bpb: 3, tonic: 45, bass: 'saw', pump: 1,
            mel: 'e\' d#\' e\' b d\' c\' | a - . c e a | b - . e g# b | c\' - . e e\' d#\' |' +
                 'e\' d#\' e\' b d\' c\' | a - . c e a | b - . e c\' b | a - . . e\' d#\'',
            ch: 'Am Am E Am Am Am E Am',
            sec: [{o: 0, lead: 'mallet', pad: 0.7, bp: 'x.....', dr: 'K.....'},
                {o: 0, lead: 'mallet', l2: 'synth', o2: -12, pad: 0.8, bp: 'x..o..', dr: 'K.hhXh', fill: 'K.hXXX'}]}),
        // Bach, Toccata in D minor BWV 565 opening: organ, descending octaves, drums build up
        theme({id: 26, bpm: 76, spb: 4, bpb: 4, tonic: 50,
            mel: 'a\' g\' a\' - - - - - - - - - - - - - | g f e d c# - - - d - - - - - - -',
            ch: 'Dm Dm A7 Dm',
            sec: [{o: 0, lead: 'organ', dr: 'T...............'},
                {o: -12, lead: 'organ', pad: 1, dr: 'T.......U.......'},
                {o: -12, lead: 'organ', l2: 'horn', o2: -24, pad: 1, bp: 'x.......x.......', dr: 'T...k...T...k.k.'},
                {o: 0, lead: 'organ', l2: 'bow', o2: -12, pad: 1.2, bp: 'x...x...x...x...', dr: 'T.h.X.h.T.h.X.hh', fill: 'T.h.X.h.R...SSTT'}]})
    ];

    // Lobby: Dvorak, Symphony No. 9, Largo theme: clay flute, then bowed strings, soft marimba.
    var LOBBY = theme({id: 1, bpm: 62, spb: 2, bpb: 4, tonic: 50, vol: 1.8,
        mel: 'e - - g g - - - | e - - d c - - - | d - - e g - - e | d - - - - - - - |' +
             'e - - g g - - - | e - - d c - - - | d - - e d - - c | c - - - - - - -',
        ch: 'D Bm A A D Bm A D',
        sec: [{o: 14, lead: 'choor', pad: 0.8, arp: 'mallet', av: 0.6, dr: ''},
            {o: 2, lead: 'bow', pad: 0.8, arp: 'mallet', av: 0.6, dr: 'b.......'}]});

    // Final: Beethoven, Symphony No. 9, "Ode to Joy": horns, then strings with drums.
    var FINAL = theme({id: 7, bpm: 118, spb: 2, bpb: 4, tonic: 50,
        mel: 'f# - f# - g - a - | a - g - f# - e - | d - d - e - f# - | f# - - e e - - - |' +
             'f# - f# - g - a - | a - g - f# - e - | d - d - e - f# - | e - - d d - - -',
        ch: 'D D A A D D D A D D A A D D A D',
        sec: [{o: 0, lead: 'horn', l2: 'bow', o2: 12, pad: 1, bp: 'x.x.x.x.', dr: 'T...U...', fill: 'T...R...'},
            {o: 12, lead: 'bow', l2: 'horn', o2: 0, pad: 1.3, bp: 'xoxoxoxo', arp: 'mallet', dr: 'T.tkT.tk', fill: 'T.tkRSSS'}]});

    // Board tail after the hit: a light original arpeggio in D.
    var BOARD_TAIL = theme({id: 9, bpm: 120, spb: 4, bpb: 2, tonic: 50, vol: 0.85,
        mel: 'd f# a d\' a f# d f# | e a c#\' e\' c#\' a e a',
        ch: 'D A',
        sec: [{o: 0, lead: 'mallet', pad: 0.8, bp: 'x...x...', dr: 'U..k..k.'}]});

    var TRACKS = {
        lobby: LOBBY,
        question: QUESTION,
        final: FINAL,
        // Build-up: taiko and frame-drum roll under a riser and swelling strings, a stab, then the tail.
        board: {
            bpm: 120, spb: 4,
            play: function (p, c, t, sd) {
                var I = 9;
                if (c === 0) {
                    strings([50, 57, 62, 66], t, sd * I + 0.4, 0.05, p.out, sd * I);
                    riser(t, sd * I, 0.12, p.out);
                }
                if (c < I) {
                    var k = (c + 1) / I, kk = k * k;
                    for (var j = 0; j < 3; j++) slap(t + j * sd / 3, (0.05 + 0.22 * kk) * (0.85 + 0.3 * hash(c * 3 + j)), p.out);
                    if (c % 2 === 0) taiko(t, 0.2 + 0.4 * k, p.out);
                    return;
                }
                if (c === I) {
                    taiko(t, 0.95, p.out);
                    strings([62, 66, 69, 74], t, 0.5, 0.08, p.out, 0.01);
                    hiss(t, 0.8, 0.08, p.out, 'highpass', 3500);
                }
                BOARD_TAIL.play(p, c - I, t, sd);
            }
        }
    };

    function stepDur(p) {
        return 60 / (p.def.bpm * (p.urgent ? p.def.urgent || 1 : 1)) / p.def.spb;
    }

    // Lookahead scheduler: a coarse timer queues notes slightly ahead on the precise audio clock.
    function schedule() {
        if (!ctx) return;
        var now = ctx.currentTime;
        playing = playing.filter(function (p) {
            if (p.end && p.end <= now) {
                urgentOff(p);
                try { p.out.disconnect(); } catch (e) { /* ignore */ }
                return false;
            }
            return true;
        });
        playing.forEach(function (p) {
            if (p.next < now - 0.25) p.next = now + 0.03;   // back from a pause
            while (p.next < now + LOOKAHEAD && (!p.end || p.next < p.end)) {
                var sd = stepDur(p);
                try { p.def.play(p, p.count, p.next, sd); } catch (e) { /* keep going */ }
                p.count += 1;
                p.next += sd;
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

    // Which definition and variant the wanted music maps to.
    function resolve() {
        var def = want.name && TRACKS.hasOwnProperty(want.name) ? TRACKS[want.name] : null;
        if (!def) return null;
        if (!def.length) return {def: def, v: 0};
        var n = def.length, v = +want.variant;
        if (want.variant !== null && want.variant !== undefined && isFinite(v)) v = ((Math.floor(v) % n) + n) % n;
        else if (current && current.name === want.name) v = current.variant;
        else v = (lastVariant + 1) % n;
        return {def: def[v], v: v, multi: true};
    }

    function startMusic() {
        if (!ctx) return;
        var level = want.quiet ? 0.28 : 1, r = resolve();
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
        if (r.multi) lastVariant = r.v;
        var out = ctx.createGain();
        out.gain.value = 0.0001;
        out.connect(bus.music);
        current = {name: want.name, variant: r.v, def: r.def, out: out, kz: body(out), str: [],
            count: 0, next: ctx.currentTime + 0.06, end: 0, urgent: false};
        fadeTo(out.gain, level, same ? 0.35 : 0.6);   // variant switch: quicker overlap
        playing.push(current);
        if (keepUrgent) urgentOn(current);
        if (!timer) timer = setInterval(schedule, TICK_MS);
        schedule();
    }

    // Last seconds of a question: faster strums, more drum, a rising drone in the variant's key.
    function urgentOn(p) {
        var v = p.def.v;
        p.urgent = true;
        if (!v || p.ud) return;
        var t = ctx.currentTime, g = ctx.createGain(), lp = filter('lowpass', 500, 1.5, g), os = [];
        g.gain.setValueAtTime(0.0001, t);
        g.gain.linearRampToValueAtTime(0.06, t + 1.5);
        g.connect(p.out);
        lp.frequency.setValueAtTime(500, t);
        lp.frequency.linearRampToValueAtTime(1500, t + 5);
        [v.tonic, v.tonic + 7].forEach(function (m) {
            var o = ctx.createOscillator();
            o.type = 'sawtooth';
            o.frequency.value = mhz(m);
            o.detune.setValueAtTime(0, t);
            o.detune.linearRampToValueAtTime(200, t + 5);
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

    var joinN = 0;
    function sStrum(notes, t, vol, spread, ring) {
        notes.forEach(function (m, i) { pluck(mhz(m), t + i * spread, vol, bus.kz, ring); });
    }

    var SFX = {
        tick: function (t, o) {
            tone('sine', 1250, t, 0.05, 0.3, o);
            hiss(t, 0.02, 0.12, o, 'bandpass', 3200, 2);
        },
        go: function (t, o) {
            drum(t, 0.7, o);
            sStrum([55, 62, 67], t, 0.45, 0.012, 0.9);
            sStrum([55, 62, 71], t + 0.14, 0.5, 0.012, 1.2);
            slap(t + 0.14, 0.15, o);
        },
        join: function (t) {
            var notes = [62, 64, 65, 67, 69];
            pluck(mhz(notes[joinN++ % notes.length]), t, 0.55, bus.kz, 1);
            pluck(mhz(50), t + 0.01, 0.25, bus.kz, 1);
        },
        answer: function (t, o) {
            tone('triangle', 660, t, 0.07, 0.25, o);
            tone('triangle', 990, t + 0.055, 0.12, 0.22, o);
        },
        correct: function (t) {
            sStrum([55, 62, 67], t, 0.4, 0.01, 1);
            pluck(mhz(71), t + 0.09, 0.5, bus.kz, 1);
            pluck(mhz(74), t + 0.18, 0.55, bus.kz, 1.2);
        },
        wrong: function (t, o) {
            var lp = filter('lowpass', 900, 0.7, o);
            tone('triangle', mhz(58), t, 0.16, 0.35, lp);
            tone('triangle', mhz(53), t + 0.13, 0.35, 0.35, lp, mhz(52));
        },
        reveal: function (t, o) {
            hiss(t, 0.45, 0.12, o, 'bandpass', 500, 1.5).frequency.exponentialRampToValueAtTime(5000, t + 0.4);
            drum(t + 0.32, 0.5, o);
            sStrum([50, 57, 62, 69], t + 0.32, 0.42, 0.025, 1.2);
        },
        // Strummed flourish: tremolo with a drum roll, a run up, three full chords.
        fanfare: function (t, o) {
            var k;
            for (k = 0; k < 8; k++) {
                sStrum(k % 2 ? [67, 62] : [55, 62, 67], t + k * 0.05, 0.12 + 0.035 * k, 0.006, 0.07);
                slap(t + k * 0.05, 0.05 + 0.025 * k, o);
            }
            [67, 69, 71, 74].forEach(function (m, i) { pluck(mhz(m), t + 0.42 + i * 0.06, 0.42, bus.kz, 0.3); });
            drum(t + 0.68, 0.8, o);
            sStrum([55, 62, 67, 71], t + 0.68, 0.5, 0.018, 0.3);
            drum(t + 0.95, 0.5, o);
            sStrum([53, 60, 65, 69], t + 0.95, 0.45, 0.018, 0.3);
            drum(t + 1.22, 0.95, o);
            hiss(t + 1.22, 1.0, 0.07, o, 'highpass', 4000);
            sStrum([43, 55, 62, 67, 71], t + 1.22, 0.55, 0.022, 1.5);
            for (k = 1; k < 7; k++) {
                sStrum(k % 2 ? [67, 62] : [55, 62, 67], t + 1.22 + k * 0.11, 0.3 - 0.035 * k, 0.008, 0.15);
                if (k < 4) slap(t + 1.22 + k * 0.11, 0.1 - 0.02 * k, o);
            }
        },
        gong: function (t, o) { gong(t, 0.55, o, 1); },
        // End of the game: gong, an accelerating drum roll with a riser, then a rising chord.
        finale: function (t, o) {
            gong(t, 0.4, o, 0.75);
            var tt = t + 0.25, dt = 0.13, n = 0, k, T = t + 2.6;
            while (tt < t + 2.3) {
                k = (tt - t) / 2.3;
                slap(tt, 0.04 + 0.2 * k * k, o);
                if (n++ % 3 === 0) drum(tt, 0.15 + 0.45 * k, o);
                dt = Math.max(0.035, dt * 0.93);
                tt += dt;
            }
            riser(t + 0.8, 1.5, 0.1, o);
            taiko(t + 2.3, 0.6, o);
            strings([50, 57, 62, 66], t + 2.3, 0.3, 0.05, o, 0.02);
            [62, 66, 69, 74].forEach(function (m, i) { mallet(mhz(m), t + 2.3 + i * 0.05, 0.16, o, 0.3); });
            taiko(T, 1, o);
            drum(T, 0.7, o);
            strings([43, 55, 62, 67, 71], T, 1.4, 0.07, o, 0.12);
            [67, 71, 74, 79].forEach(function (m, i) { mallet(mhz(m), T + i * 0.04, 0.22, o, 1.1); });
            hiss(T, 1.2, 0.07, o, 'highpass', 4500);
        },
        streak: function (t) {
            [62, 64, 65, 67, 69].forEach(function (m, i) { pluck(mhz(m), t + i * 0.05, 0.4, bus.kz, 0.35); });
            sStrum([57, 62, 69], t + 0.28, 0.45, 0.012, 1);
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
        variants: {question: QUESTION.length},
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
        // music('question') rotates variants; music('question', {variant: n}) picks n % count.
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
                urgent: !!(current && current.urgent), voices: voices};
        },
        sfx: function (name) {
            if (!ctx || !unlocked || muted || !SFX.hasOwnProperty(name)) return;
            try { SFX[name](ctx.currentTime + 0.01, bus.sfx); } catch (e) { /* ignore */ }
        },
        vibrate: function (pattern) {
            if (muted || !navigator.vibrate) return false;
            try { return navigator.vibrate(pattern); } catch (e) { return false; }
        }
    };
})();
