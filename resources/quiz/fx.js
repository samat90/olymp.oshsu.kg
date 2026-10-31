/* Quiz visual effects: confetti, counters, FLIP reorder, bars, answer shapes, 3-2-1, timer ring.
 * window.QuizFx. No libraries; everything respects prefers-reduced-motion. */
(function () {
    'use strict';

    // Same values as .qz-c0 ... .qz-c5 in theme.css.
    var COLORS = ['#0b7a72', '#bd4f0d', '#6a48c4', '#b42358', '#4f6b17', '#1c66a8'];

    function reducedMotion() {
        try { return window.matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) { return false; }
    }

    function fmt(n) {
        return String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
    }

    /* ---------------- shapes ---------------- */

    function star() {
        var pts = [];
        for (var k = 0; k < 10; k++) {
            var r = k % 2 ? 4.4 : 10.5, a = (k * 36 - 90) * Math.PI / 180;
            pts.push((12 + r * Math.cos(a)).toFixed(2) + ',' + (12.8 + r * Math.sin(a)).toFixed(2));
        }
        return '<polygon points="' + pts.join(' ') + '"/>';
    }
    var SHAPES = [
        star(),                                                                              // star
        '<polygon points="12,2 20.7,7 20.7,17 12,22 3.3,17 3.3,7"/>',                        // hexagon
        '<path d="M12 2.2C9 6.4 5 10.9 5 15a7 7 0 0 0 14 0c0-4.1-4-8.6-7-12.8z"/>',          // drop
        '<path d="M15.5 2.6a9.6 9.6 0 1 0 6 15.6A8 8 0 0 1 15.5 2.6z"/>',                    // crescent
        '<path d="M2.5 21v-8C2.5 7.5 7 3 12 3s9.5 4.5 9.5 10v8h-6.5v-5.5h-6v5.5z"/>',          // yurt
        '<path d="M6.6 19.5a4.6 4.6 0 0 1-.7-9.1 6.3 6.3 0 0 1 12-1.2 5.2 5.2 0 0 1-.2 10.3z"/>' // cloud
    ];
    var NAMES = ['звезда', 'шестиугольник', 'капля', 'полумесяц', 'юрта', 'облако'];

    function shape(i) {
        i = ((i % 6) + 6) % 6;
        return '<svg class="qz-shape" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" ' +
            'stroke-width="1.2" stroke-linejoin="round" role="img" aria-label="' + NAMES[i] + '">' + SHAPES[i] + '</svg>';
    }

    /* ---------------- confetti ---------------- */

    function confetti(durationMs) {
        if (reducedMotion()) return;
        var ms = durationMs || 3000, dpr = Math.min(window.devicePixelRatio || 1, 2);
        var cv = document.createElement('canvas'), g = cv.getContext('2d');
        if (!g) return;
        cv.className = 'qz-confetti';
        cv.setAttribute('aria-hidden', 'true');
        cv.style.cssText = 'position:fixed;inset:0;width:100%;height:100%;pointer-events:none;z-index:9999';
        document.body.appendChild(cv);
        var w = cv.width = window.innerWidth * dpr, h = cv.height = window.innerHeight * dpr;
        var parts = [], i;
        for (i = 0; i < 150; i++) {
            var fromSide = i % 3 === 0, left = i % 2 === 0, sp = (6 + Math.random() * 9) * dpr;
            var ang = left ? -Math.PI / 3 - Math.random() * 0.5 : -2 * Math.PI / 3 + Math.random() * 0.5;
            parts.push({
                x: fromSide ? (left ? 0 : w) : Math.random() * w,
                y: fromSide ? h * 0.8 : -20 * dpr - Math.random() * h * 0.4,
                vx: fromSide ? Math.cos(ang) * sp : (Math.random() - 0.5) * 2 * dpr,
                vy: fromSide ? Math.sin(ang) * sp * 1.6 : Math.random() * 2 * dpr,
                rot: Math.random() * 6.3, vr: (Math.random() - 0.5) * 0.3, phase: Math.random() * 6.3,
                size: (7 + Math.random() * 6) * dpr, kind: i % 4, color: COLORS[i % COLORS.length]
            });
        }
        var start = performance.now();
        function frame(now) {
            var t = now - start, alpha = Math.min(1, (ms - t) / 600);
            g.clearRect(0, 0, w, h);
            if (alpha <= 0) { cv.remove(); return; }
            g.globalAlpha = alpha;
            parts.forEach(function (p) {
                p.vy += 0.18 * dpr;
                p.vx *= 0.985;
                p.vy *= 0.985;
                p.x += p.vx + Math.sin((t / 300) + p.phase) * 0.6 * dpr;
                p.y += p.vy;
                p.rot += p.vr;
                g.save();
                g.translate(p.x, p.y);
                g.rotate(p.rot);
                g.fillStyle = p.color;
                if (p.kind < 2) {                               // ribbon fluttering around its axis
                    g.scale(1, Math.cos(t / 120 + p.phase));
                    g.fillRect(-p.size * 0.3, -p.size, p.size * 0.6, p.size * 2);
                } else {                                         // small hexagon or star
                    g.beginPath();
                    var n = p.kind === 2 ? 6 : 10;
                    for (var k = 0; k < n; k++) {
                        var r = p.kind === 2 || k % 2 === 0 ? p.size * 0.7 : p.size * 0.3, a = k * 2 * Math.PI / n;
                        g.lineTo(r * Math.cos(a), r * Math.sin(a));
                    }
                    g.fill();
                }
                g.restore();
            });
            requestAnimationFrame(frame);
        }
        requestAnimationFrame(frame);
    }

    /* ---------------- numbers ---------------- */

    function countUp(el, from, to, ms) {
        if (!el) return;
        if (el._qzCount) cancelAnimationFrame(el._qzCount);
        if (reducedMotion() || from === to) { el.textContent = fmt(to); return; }
        var start = performance.now(), dur = ms || 900;
        (function step(now) {
            var k = Math.min(1, (now - start) / dur), e = 1 - Math.pow(1 - k, 3);
            el.textContent = fmt(from + (to - from) * e);
            el._qzCount = k < 1 ? requestAnimationFrame(step) : 0;
        })(start);
    }

    /* ---------------- FLIP reorder ---------------- */

    // Children with data-key slide from their old to their new position after mutateFn() reorders them.
    function flip(container, mutateFn) {
        if (!container) { if (mutateFn) mutateFn(); return; }
        var before = {}, kids = container.querySelectorAll('[data-key]');
        Array.prototype.forEach.call(kids, function (el) { before[el.dataset.key] = el.getBoundingClientRect().top; });
        if (mutateFn) mutateFn();
        if (reducedMotion()) return;
        Array.prototype.forEach.call(container.querySelectorAll('[data-key]'), function (el) {
            var old = before[el.dataset.key];
            if (old === undefined) {
                el.classList.remove('qz-pop');
                void el.offsetWidth;
                el.classList.add('qz-pop');
                return;
            }
            var dy = old - el.getBoundingClientRect().top;
            if (!dy) return;
            el.style.transition = 'none';
            el.style.transform = 'translateY(' + dy + 'px)';
            void el.offsetWidth;
            el.style.transition = 'transform .6s cubic-bezier(.2,.8,.2,1)';
            el.style.transform = '';
            el.addEventListener('transitionend', function done() {
                el.style.transition = '';
                el.removeEventListener('transitionend', done);
            });
        });
    }

    /* ---------------- bars ---------------- */

    // Ensures container (.qz-bars) has one .qz-bar per value (reusing existing ones, e.g. pre-rendered
    // with labels), then grows each .qz-bar-fill to value/max via the --qz-v custom property.
    function bars(container, values, max) {
        if (!container) return;
        container.classList.add('qz-bars');
        max = max || Math.max.apply(null, values.concat([1]));
        values.forEach(function (v, i) {
            var bar = container.children[i];
            if (!bar || !bar.querySelector('.qz-bar-fill')) {
                bar = document.createElement('div');
                bar.className = 'qz-bar qz-c' + (i % 6);
                bar.innerHTML = '<span class="qz-bar-num">0</span><div class="qz-bar-fill"></div>';
                container.insertBefore(bar, container.children[i] || null);
            }
            var fill = bar.querySelector('.qz-bar-fill'), num = bar.querySelector('.qz-bar-num');
            fill.style.setProperty('--qz-v', '0');
            void fill.offsetWidth;
            fill.style.setProperty('--qz-v', String(Math.max(0, Math.min(1, v / max))));
            if (num) countUp(num, 0, v, 800);
        });
        return container;
    }

    /* ---------------- 3-2-1 ---------------- */

    function countdown(el, seconds, onDone) {
        var timer = null, left = Math.max(0, seconds || 3);
        function show() {
            var n = Math.ceil(left - 0.001);
            if (n <= 0) {
                el.innerHTML = '';
                if (onDone) onDone();
                return;
            }
            el.innerHTML = '<span class="qz-count">' + n + '</span>';
            var wait = left - (n - 1);                      // fractional first step keeps sync with the server
            left = n - 1;
            timer = setTimeout(show, wait * 1000);
        }
        show();
        return {cancel: function () { clearTimeout(timer); el.innerHTML = ''; }};
    }

    /* ---------------- timer ring ---------------- */

    function ring(el) {
        var R = 45, C = 2 * Math.PI * R;
        el.classList.add('qz-ring');
        el.innerHTML = '<svg viewBox="0 0 100 100" aria-hidden="true">' +
            '<circle class="qz-ring-track" cx="50" cy="50" r="' + R + '"/>' +
            '<circle class="qz-ring-bar" cx="50" cy="50" r="' + R + '" stroke-dasharray="' + C.toFixed(2) + '"/>' +
            '</svg><span class="qz-ring-num"></span>';
        var bar = el.querySelector('.qz-ring-bar'), num = el.querySelector('.qz-ring-num');
        return {
            set: function (fraction, secondsLeft) {
                var f = Math.max(0, Math.min(1, fraction)), s = Math.max(0, Math.ceil(secondsLeft));
                bar.style.strokeDashoffset = (C * (1 - f)).toFixed(2);
                if (num.textContent !== String(s)) num.textContent = s;
                el.classList.toggle('qz-ring-warm', f <= 0.4 && s > 5);
                el.classList.toggle('qz-ring-hot', s <= 5 && s > 0);
            }
        };
    }

    window.QuizFx = {
        reducedMotion: reducedMotion,
        format: fmt,
        colors: COLORS,
        confetti: confetti,
        countUp: countUp,
        flip: flip,
        bars: bars,
        shape: shape,
        countdown: countdown,
        ring: ring
    };
})();
