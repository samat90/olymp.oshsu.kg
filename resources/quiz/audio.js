/* Quiz sounds and music. Everything is synthesized with the Web Audio API: no audio files.
 * The music imitates a komuz (three plucked strings, open-string drones) with a frame drum.
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

    // Melody in scale degrees: "1 - 5, 4'" -> MIDI per step; ' raises, , lowers an octave, '-' holds.
    function parseMel(text, base, mode) {
        var out = {note: [], fresh: []}, last = base;
        text.split(/\s+/).forEach(function (s) {
            if (!s || s === '|') return;
            var isNew = s !== '-';
            if (isNew) {
                last = base + mode[+s.charAt(0) - 1];
                for (var j = 1; j < s.length; j++) last += s.charAt(j) === "'" ? 12 : -12;
            }
            out.note.push(last);
            out.fresh.push(isNew);
        });
        return out;
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

    // Sustained soft drone and a chopo-choor-like clay flute.
    function pad(f, t, dur, vol, out) {
        var g = ctx.createGain(), lp = filter('lowpass', 520, 0.6, g);
        g.gain.setValueAtTime(0.0001, t);
        g.gain.linearRampToValueAtTime(vol, t + 1.5);
        g.gain.setValueAtTime(vol, t + dur - 1.5);
        g.gain.linearRampToValueAtTime(0.0001, t + dur);
        g.connect(out);
        [-5, 5].forEach(function (cents) {
            var o = ctx.createOscillator();
            o.type = 'triangle';
            o.frequency.value = f;
            o.detune.value = cents;
            o.connect(lp);
            o.start(t);
            o.stop(t + dur + 0.05);
        });
    }
    function choor(f, t, dur, vol, out) {
        var o = ctx.createOscillator(), g = ctx.createGain(), lfo = ctx.createOscillator(), lg = ctx.createGain();
        o.frequency.value = f;
        lfo.frequency.value = 4.6;
        lg.gain.value = f * 0.005;
        lfo.connect(lg);
        lg.connect(o.frequency);
        g.gain.setValueAtTime(0.0001, t);
        g.gain.linearRampToValueAtTime(vol, t + 0.3);
        g.gain.setValueAtTime(vol, t + dur - 0.5);
        g.gain.linearRampToValueAtTime(0.0001, t + dur);
        o.connect(g);
        g.connect(out);
        o.start(t);
        lfo.start(t);
        o.stop(t + dur + 0.05);
        lfo.stop(t + dur + 0.05);
        hiss(t, 0.3, vol * 0.35, out, 'bandpass', f * 2, 2.5);
    }

    /* ---------------- music ---------------- */

    var URG_P = {6: 'DuDuDu', 8: 'DuDuDuDu'}, URG_D = {6: 'BtrBtr', 8: 'BtrtBtrr'}, FILL = {6: 'Btrtrr', 8: 'B.trtrrr'};

    // A komuz piece: drone strings follow the bar's chord root, the melody rides the middle string.
    // v: bpm, spb (steps per beat), bpb (beats per bar), tonic (MIDI of the drone), d (second drone
    // string, semitones), mode, mo (melody octave above tonic), mel, ch (chord degree per bar),
    // p / p2 / pc (strum pattern, second pass, cadence bar), dr (drum pattern), vol, dv (drum level).
    function piece(v) {
        var mel = parseMel(v.mel, v.tonic + 12 * v.mo, v.mode), steps = v.spb * v.bpb, L = mel.note.length,
            bars = L / steps;
        return {
            bpm: v.bpm, spb: v.spb, urgent: 1.12, v: v,
            play: function (p, c, t, sd) {
                var i = c % L, pass = Math.floor(c / L) % 2, bar = Math.floor(i / steps), pos = i % steps,
                    u = p.urgent, vol = v.vol || 1, dv = (v.dv || 1) * vol, h = hash(c * 7 + v.id * 131),
                    acc = 0.88 + 0.24 * h, a = v.tonic + (v.ch ? shift(v.mode, v.ch[bar % v.ch.length]) : 0),
                    n = mel.note[i], notes = [a, n, a + v.d];
                var pat = u ? URG_P[steps] : bar % 4 === 3 ? v.pc : pass && v.p2 ? v.p2 : v.p, ch = pat.charAt(pos);
                if (ch === 'D' || ch === 'd') {
                    strum(p, notes, t, (ch === 'D' ? 0.46 : 0.3) * acc * vol, 1, (ch === 'D' ? 0.016 : 0.01) * (0.8 + 0.4 * h));
                } else if (ch === 'u') {
                    strum(p, notes, t, 0.24 * acc * vol, -1, 0.008);
                } else if (mel.fresh[i]) {
                    pluck(mhz(n), t, 0.36 * acc * vol, p.kz, 0, p.str, 1);
                }
                var dp = u ? URG_D[steps] : pass && bar === bars - 1 ? FILL[steps] : v.dr, dc = dp.charAt(pos);
                if (dc === 'B') drum(t, 0.5 * dv, p.out);
                else if (dc === 'b') drum(t, 0.28 * dv, p.out);
                else if (dc === 't') slap(t, 0.13 * dv * acc, p.out);
                else if (dc === 'r') { slap(t, 0.1 * dv, p.out); slap(t + sd / 2, 0.08 * dv, p.out); }
                if (v.extra) v.extra(p, i, t, sd);
            }
        };
    }

    var QUESTION = [
        // D Dorian, 6/8 gallop
        piece({id: 10, bpm: 116, spb: 3, bpb: 2, tonic: 50, d: 7, mode: DOR, mo: 1,
            mel: '1 - 1 5 - 4 | 3 - 4 5 - - | 5 5 6 5 - 4 | 3 - 2 1 - - |' +
                 '4 - 4 1\' - 7 | 6 - 5 4 - 5 | 3 3 4 2 - 7, | 1 - - 5, - -',
            ch: [0, 0, 0, 0, 3, 3, 6, 0], p: 'D.uDdu', p2: 'D.uDuu', pc: 'D.uD..', dr: 'B.tb.t'}),
        // G Mixolydian, 2/4 long-short-short gallop
        piece({id: 11, bpm: 128, spb: 4, bpb: 2, tonic: 55, d: 7, mode: MIX, mo: 1,
            mel: '1 - 1 1 5 - 4 3 | 2 - 3 4 5 - - - | 6 - 5 4 5 - 4 3 | 2 - 1 7, 1 - - - |' +
                 '4 - 4 4 1\' - 7 6 | 5 - 6 7 1\' - - - | 7 - 6 5 4 - 3 2 | 1 - 5, - 1 - - -',
            ch: [0, 0, 3, 0, 3, 3, 6, 0], p: 'D.udD.ud', p2: 'D.udDudu', pc: 'D.udD...', dr: 'B..tB.t.'}),
        // A Aeolian, 3/4 long-short-short
        piece({id: 12, bpm: 104, spb: 2, bpb: 3, tonic: 57, d: 7, mode: AEO, mo: 1,
            mel: '5, - 1 1 2 3 | 4 - 3 2 1 - | 5 - 5 4 5 6 | 5 - - 4 3 2 |' +
                 '1\' - 7 6 5 - | 4 4 5 4 3 - | 2 - 3 2 7, - | 1 - - 5, - -',
            ch: [0, 3, 0, 0, 5, 3, 6, 0], p: 'D.duDu', p2: 'D.duDd', pc: 'D.D.D.', dr: 'B.t.bt'}),
        // F Ionian without the leading tone, syncopated 2/4
        piece({id: 13, bpm: 136, spb: 4, bpb: 2, tonic: 53, d: 7, mode: ION, mo: 1,
            mel: '1 - 3 - 5 5 - 3 | 4 - 4 3 2 - 1 - | 5 - 6 - 1\' 1\' - 6 | 5 - - 4 3 - - - |' +
                 '2 - 2 3 4 - 5 - | 6 6 5 - 4 - 3 - | 2 - 5, - 2 - 3 2 | 1 - - - 5, - - -',
            ch: [0, 3, 0, 0, 4, 3, 4, 0], p: 'D.u.uDu.', p2: 'D.u.uDud', pc: 'D.u.D...', dr: 'B..b..t.'}),
        // E Dorian, fast 6/8 triplets
        piece({id: 14, bpm: 138, spb: 3, bpb: 2, tonic: 52, d: 7, mode: DOR, mo: 1,
            mel: '1 1 2 3 - 1 | 5 - 4 3 2 1 | 4 4 5 6 - 4 | 5 - 4 5 - - |' +
                 '1\' - 7 6 - 5 | 6 5 4 5 - - | 3 3 4 2 - 7, | 1 - - 5, - -',
            ch: [0, 0, 3, 0, 6, 3, 6, 0], p: 'DuuDuu', p2: 'DudDuu', pc: 'DuuD..', dr: 'Bt.Bt.'}),
        // C Mixolydian, syncopated 3/4, drone on the fourth below
        piece({id: 15, bpm: 110, spb: 2, bpb: 3, tonic: 60, d: -5, mode: MIX, mo: 0,
            mel: '5 - 5 1\' - 7 | 6 5 4 5 - - | 3 - 4 5 6 5 | 4 - 3 2 - - |' +
                 '1 - 1 5 - 4 | 3 4 5 7 - 6 | 5 - 4 3 2 3 | 1 - - 5, - -',
            ch: [0, 3, 0, 3, 0, 6, 4, 0], p: 'Du.uD.', p2: 'Du.uDu', pc: 'D.D...', dr: 'B..tb.'})
    ];

    var LOBBY = piece({id: 1, bpm: 76, spb: 3, bpb: 2, tonic: 57, d: 7, mode: DOR, mo: 1, vol: 0.85, dv: 0.6,
        mel: '5, - - 1 - - | 1 1 2 3 - 2 | 1 - - 5, - - | 4, - 5, 6, - - | 5, - - 2 - 1 | 7, - 1 2 - 3 |' +
             '2 - 1 7, - 5, | 1 - - - - - | 3 - - 5 - - | 4 4 3 4 - 5 | 3 - 2 1 - - | 2 - 3 4 - 3 |' +
             '5 - - 4 3 2 | 1 - 2 7, - 5, | 6, - 7, 1 - 7, | 1 - - - - -',
        ch: [0, 0, 0, 6, 0, 6, 0, 0, 2, 3, 0, 6, 4, 0, 6, 0],
        p: 'D..u..', p2: 'D..du.', pc: 'D.....', dr: 'b.....',
        extra: function (p, i, t, sd) {
            if (i === 0) {
                pad(mhz(45), t, sd * 96 + 1.5, 0.05, p.out);
                pad(mhz(52), t, sd * 96 + 1.5, 0.035, p.out);
            }
            if (i === 48) choor(mhz(64), t, sd * 11, 0.06, p.out);
            if (i === 78) choor(mhz(57), t, sd * 16, 0.055, p.out);
        }});

    var FINAL = piece({id: 7, bpm: 132, spb: 3, bpb: 2, tonic: 55, d: 7, mode: ION, mo: 1,
        mel: '1 - 3 5 - 3 | 4 - 3 2 - 1 | 5 5 6 5 4 3 | 2 - - 5, - - | 1 - 3 5 - 1\' | 7 - 6 5 - 3 |' +
             '4 4 3 2 3 2 | 1 - - - - - | 5 - 5 6 - 5 | 4 - 4 5 - 4 | 3 - 3 4 - 3 | 2 - 1 2 - 5, |' +
             '1 1 5 5 6 5 | 4 - 3 4 - 5 | 6 - 5 4 3 2 | 1 - 5, - 1 -',
        ch: [0, 3, 0, 4, 0, 0, 3, 0, 4, 3, 0, 4, 0, 3, 4, 0],
        p: 'DuuDud', p2: 'DudDuu', pc: 'D.uD..', dr: 'B.tBtt'});

    var BOARD_TAIL = piece({id: 9, bpm: 120, spb: 4, bpb: 2, tonic: 50, d: 7, mode: ION, mo: 1, vol: 0.85,
        mel: '5 - 5 6 5 - 3 - | 4 - 3 2 1 - - - | 3 - 3 4 5 - 6 5 | 4 - 2 - 1 - - -',
        ch: [0, 3, 4, 0], p: 'D.udD.ud', pc: 'D...D...', dr: 'b..tb.t.'});

    var TRACKS = {
        lobby: LOBBY,
        question: QUESTION,
        final: FINAL,
        // Frame-drum roll with tremolo strums, a full chord on the hit, then a light cadence groove.
        board: {
            bpm: 120, spb: 4,
            play: function (p, c, t, sd) {
                var I = 9, chord = [50, 62, 57];
                if (c < I) {
                    var k = (c + 1) / I, kk = k * k;
                    strum(p, chord, t, 0.08 + 0.3 * kk, 1, 0.006);
                    strum(p, chord, t + sd / 2, 0.06 + 0.22 * kk, -1, 0.005);
                    for (var j = 0; j < 3; j++) slap(t + j * sd / 3, (0.04 + 0.2 * kk) * (0.85 + 0.3 * hash(c * 3 + j)), p.out);
                    if (c % 4 === 0) drum(t, 0.25 + 0.3 * k, p.out);
                    return;
                }
                if (c === I) {
                    drum(t, 0.9, p.out);
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
