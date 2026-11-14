/* Quiz avatars: 24 funny characters drawn from plain shapes (own art, no third-party images).
   Only the number 0..23 travels over the network; the picture is built here and cached. */
(function () {
    'use strict';
    var D = '#2b2233', W = '#fff';

    function eye(x, y, r) { return '<circle cx="' + x + '" cy="' + y + '" r="' + (r || 3) + '" fill="' + D + '"/>'; }
    function bigEye(x, y, r, dx) {
        return '<circle cx="' + x + '" cy="' + y + '" r="' + r + '" fill="' + W + '"/><circle cx="' + (x + (dx || 0)) + '" cy="' + y +
            '" r="' + (r * .5) + '" fill="' + D + '"/>';
    }
    function smile(y, w) {
        w = w || 7;
        return '<path d="M' + (32 - w) + ' ' + y + 'q' + w + ' ' + (w * .9) + ' ' + 2 * w + ' 0" fill="none" stroke="' + D + '" stroke-width="2.4" stroke-linecap="round"/>';
    }
    function tongue(x, y) { return '<path d="M' + x + ' ' + y + 'v5a3 3 0 0 0 6 0v-5z" fill="#ff6b8b"/>'; }
    function circ(x, y, r, c) { return '<circle cx="' + x + '" cy="' + y + '" r="' + r + '" fill="' + c + '"/>'; }
    function poly(p, c) { return '<path d="' + p + '" fill="' + c + '"/>'; }
    function rect(x, y, w, h, r, c) { return '<rect x="' + x + '" y="' + y + '" width="' + w + '" height="' + h + '" rx="' + r + '" fill="' + c + '"/>'; }
    function cheeks(c) { return circ(19, 40, 3.5, c || '#ff8fa8') + circ(45, 40, 3.5, c || '#ff8fa8'); }

    // Each entry: [background, name, drawing]
    var A = [
        ['#ffe3b3', 'Кот', function () {
            return poly('M12 30L14 8l16 12zM52 30L50 8 34 20z', '#f59a3b') + circ(32, 36, 21, '#f59a3b') + poly('M16 16l-1 8 7-4zM48 16l1 8-7-4z', '#ffb3c1') +
                eye(24, 33, 3) + eye(40, 33, 3) + poly('M29 39h6l-3 3z', '#e0577a') + smile(43, 4) +
                '<path d="M8 38l10 2M8 46l10-3M56 38l-10 2M56 46l-10-3" stroke="' + D + '" stroke-width="1.6" stroke-linecap="round"/>';
        }],
        ['#d9ecff', 'Пёс', function () {
            return rect(5, 18, 14, 28, 7, '#7b4a2b') + rect(45, 18, 14, 28, 7, '#7b4a2b') + circ(32, 34, 20, '#c68b59') +
                circ(32, 42, 11, '#f1d2ab') + eye(24, 30, 3) + eye(40, 30, 3) + circ(32, 38, 4, D) + tongue(32, 45) +
                '<path d="M32 42v3" stroke="' + D + '" stroke-width="2"/>';
        }],
        ['#e1f5d8', 'Лис', function () {
            return poly('M10 30L12 6l18 14zM54 30L52 6 34 20z', '#e8662b') + poly('M32 56L10 34q10-14 22-14t22 14z', '#f08a3d') +
                circ(32, 36, 20, '#f08a3d') + poly('M32 58L16 40q16 6 32 0z', W) + eye(24, 33, 3) + eye(40, 33, 3) + circ(32, 50, 3.2, D) +
                poly('M12 8l2 12 8-5zM52 8l-2 12-8-5z', '#3a2a2a');
        }],
        ['#ffd9d0', 'Мишка', function () {
            return circ(14, 16, 9, '#8a5a3a') + circ(50, 16, 9, '#8a5a3a') + circ(14, 16, 4.5, '#d9a679') + circ(50, 16, 4.5, '#d9a679') +
                circ(32, 36, 22, '#a8714a') + circ(32, 44, 10, '#e9c9a3') + eye(23, 31, 3) + eye(41, 31, 3) + circ(32, 41, 3.6, D) + smile(46, 4);
        }],
        ['#eaf3ea', 'Панда', function () {
            return circ(14, 16, 9, D) + circ(50, 16, 9, D) + circ(32, 36, 22, W) +
                '<ellipse cx="22" cy="32" rx="6" ry="8" transform="rotate(25 22 32)" fill="' + D + '"/><ellipse cx="42" cy="32" rx="6" ry="8" transform="rotate(-25 42 32)" fill="' + D + '"/>' +
                circ(22, 32, 2.2, W) + circ(42, 32, 2.2, W) + circ(32, 41, 3.5, D) + smile(45, 4);
        }],
        ['#f6f0b0', 'Лягушка', function () {
            return circ(20, 16, 10, '#5cc15c') + circ(44, 16, 10, '#5cc15c') + bigEye(20, 16, 7, 1) + bigEye(44, 16, 7, -1) +
                '<ellipse cx="32" cy="38" rx="25" ry="20" fill="#5cc15c"/>' +
                '<path d="M14 40q18 16 36 0" fill="#c64a63"/><path d="M14 40q18 8 36 0" fill="none" stroke="' + D + '" stroke-width="2.2" stroke-linecap="round"/>' +
                circ(24, 32, 1.6, '#3b8f3b') + circ(40, 32, 1.6, '#3b8f3b');
        }],
        ['#ffe0ec', 'Поросёнок', function () {
            return poly('M10 22l4-14 12 10zM54 22l-4-14-12 10z', '#f48fb1') + circ(32, 36, 22, '#f8b4c8') +
                '<ellipse cx="32" cy="42" rx="11" ry="8" fill="#f48fb1"/>' + circ(28, 42, 2, '#a8335a') + circ(36, 42, 2, '#a8335a') +
                eye(22, 30, 3) + eye(42, 30, 3) + cheeks('#ff7aa0');
        }],
        ['#e6e6f6', 'Мышонок', function () {
            return circ(13, 17, 11, '#9aa0b4') + circ(51, 17, 11, '#9aa0b4') + circ(13, 17, 6, '#ffb3c1') + circ(51, 17, 6, '#ffb3c1') +
                '<ellipse cx="32" cy="38" rx="19" ry="21" fill="#b8bdd0"/>' + eye(25, 33, 3) + eye(39, 33, 3) + circ(32, 43, 3.4, '#ff7aa0') +
                '<path d="M32 46v2M26 46l6 3 6-3" stroke="' + D + '" stroke-width="1.8" fill="none" stroke-linecap="round"/>' +
                '<path d="M32 50v-1" stroke="' + D + '"/><path d="M6 40l11 2M6 46l11-2M58 40l-11 2M58 46l-11-2" stroke="' + D + '" stroke-width="1.4" stroke-linecap="round"/>' +
                rect(28, 50, 3.5, 5, 1, W) + rect(32.5, 50, 3.5, 5, 1, W);
        }],
        ['#d8f1f1', 'Заяц', function () {
            return '<ellipse cx="22" cy="14" rx="7" ry="15" fill="#fff"/><ellipse cx="42" cy="14" rx="7" ry="15" fill="#fff" transform="rotate(8 42 14)"/>' +
                '<ellipse cx="22" cy="14" rx="3.5" ry="11" fill="#ffb3c1"/><ellipse cx="42" cy="14" rx="3.5" ry="11" fill="#ffb3c1" transform="rotate(8 42 14)"/>' +
                circ(32, 40, 19, W) + eye(25, 37, 3) + eye(39, 37, 3) + circ(32, 44, 2.8, '#ff7aa0') + rect(29, 47, 3, 6, 1, '#f0e4e4') + rect(32, 47, 3, 6, 1, '#f0e4e4') +
                cheeks();
        }],
        ['#ffe9c7', 'Сова', function () {
            return poly('M10 24L8 6l14 8zM54 24l2-18-14 8z', '#8b5e3c') + '<ellipse cx="32" cy="36" rx="23" ry="24" fill="#a77449"/>' +
                circ(22, 30, 11, '#f5deb3') + circ(42, 30, 11, '#f5deb3') + bigEye(22, 30, 7, 1) + bigEye(42, 30, 7, -1) +
                poly('M28 38h8l-4 8z', '#f2a226') + '<path d="M16 48q8 6 16 0q8 6 16 0" fill="none" stroke="#7a5230" stroke-width="2.4"/>';
        }],
        ['#d6ecff', 'Пингвин', function () {
            return '<ellipse cx="32" cy="36" rx="23" ry="24" fill="#2f3b52"/><ellipse cx="32" cy="42" rx="15" ry="17" fill="#fff"/>' +
                circ(24, 30, 6, W) + circ(40, 30, 6, W) + eye(25, 31, 2.6) + eye(39, 31, 2.6) + poly('M26 38h12l-6 7z', '#ff9f1c') +
                '<ellipse cx="14" cy="46" rx="4" ry="9" fill="#2f3b52" transform="rotate(20 14 46)"/>' + cheeks('#ff9fb5');
        }],
        ['#ffeccc', 'Обезьянка', function () {
            return circ(10, 34, 9, '#7a4a2b') + circ(54, 34, 9, '#7a4a2b') + circ(10, 34, 5, '#f0c9a0') + circ(54, 34, 5, '#f0c9a0') +
                circ(32, 32, 21, '#8d5a36') + '<path d="M20 28q12-6 24 0q4 8-2 14q-10 8-20 0q-6-6-2-14z" fill="#f0c9a0"/>' + eye(25, 32, 3) + eye(39, 32, 3) +
                circ(30, 40, 1.4, D) + circ(34, 40, 1.4, D) + smile(44, 5);
        }],
        ['#fff0b3', 'Лев', function () {
            var m = '';
            for (var i = 0; i < 12; i++) m += '<circle cx="' + (32 + 24 * Math.cos(i * Math.PI / 6)).toFixed(1) + '" cy="' + (34 + 24 * Math.sin(i * Math.PI / 6)).toFixed(1) + '" r="9" fill="#b9651e"/>';
            return m + circ(32, 34, 21, '#f2b04c') + circ(22, 15, 5, '#f2b04c') + circ(42, 15, 5, '#f2b04c') +
                eye(25, 31, 3) + eye(39, 31, 3) + poly('M28 37h8l-4 5z', '#7a3b19') + smile(44, 4) + cheeks('#f58a6a');
        }],
        ['#e5e5e5', 'Робот', function () {
            return '<path d="M32 4v8" stroke="' + D + '" stroke-width="2.4"/>' + circ(32, 5, 4, '#ff5a5f') + rect(8, 12, 48, 44, 10, '#9fb4c7') +
                rect(14, 20, 36, 20, 6, D) + circ(24, 30, 5, '#58e0ff') + circ(40, 30, 5, '#58e0ff') + circ(24, 30, 2, '#fff') + circ(40, 30, 2, '#fff') +
                rect(20, 45, 24, 6, 3, D) + '<path d="M26 45v6M32 45v6M38 45v6" stroke="#9fb4c7" stroke-width="1.6"/>' + rect(3, 28, 6, 12, 3, '#7f95a8') + rect(55, 28, 6, 12, 3, '#7f95a8');
        }],
        ['#e8dcff', 'Пришелец', function () {
            return '<path d="M20 14L14 4M44 14l6-10" stroke="#2f9e5b" stroke-width="2.4"/>' + circ(14, 4, 3.5, '#ffd23f') + circ(50, 4, 3.5, '#ffd23f') +
                '<path d="M32 14C10 14 8 38 20 50q12 10 24 0C56 38 54 14 32 14z" fill="#6bd68a"/>' +
                '<ellipse cx="22" cy="32" rx="7" ry="9" transform="rotate(25 22 32)" fill="' + D + '"/><ellipse cx="42" cy="32" rx="7" ry="9" transform="rotate(-25 42 32)" fill="' + D + '"/>' +
                circ(20, 29, 2, W) + circ(40, 29, 2, W) + '<path d="M28 46q4 3 8 0" stroke="' + D + '" stroke-width="2" fill="none" stroke-linecap="round"/>';
        }],
        ['#d9e9ff', 'Привидение', function () {
            return '<path d="M10 56V30C10 12 54 12 54 30v26l-8-6-7 6-7-6-7 6-7-6z" fill="#fff" stroke="#c9d6ea" stroke-width="2"/>' +
                eye(24, 32, 3.5) + eye(40, 32, 3.5) + '<ellipse cx="32" cy="42" rx="4" ry="5" fill="' + D + '"/>' + cheeks('#ffc0d0');
        }],
        ['#fff3d6', 'Кактус', function () {
            return rect(22, 8, 20, 50, 10, '#4caf6a') + rect(6, 24, 12, 8, 4, '#4caf6a') + rect(6, 16, 8, 16, 4, '#4caf6a') +
                rect(46, 30, 12, 8, 4, '#4caf6a') + rect(50, 22, 8, 16, 4, '#4caf6a') + circ(32, 8, 5, '#ff5fa2') + circ(32, 8, 2, '#ffd23f') +
                eye(27, 28, 3) + eye(37, 28, 3) + smile(35, 4) + '<path d="M32 18v2M26 46l2 1M38 46l-2 1M32 50v2" stroke="#2f7d49" stroke-width="1.6" stroke-linecap="round"/>';
        }],
        ['#dff5d0', 'Тыква', function () {
            return '<path d="M30 12q2-8 8-8" stroke="#4c8a2b" stroke-width="3" fill="none" stroke-linecap="round"/><ellipse cx="20" cy="36" rx="14" ry="20" fill="#f0771f"/><ellipse cx="44" cy="36" rx="14" ry="20" fill="#f0771f"/>' +
                '<ellipse cx="32" cy="36" rx="13" ry="21" fill="#ff9330"/>' + poly('M20 28l6 7h-12zM44 28l6 7H38z', D) + '<path d="M18 44l5 4 4-4 5 4 5-4 4 4 5-4" fill="none" stroke="' + D + '" stroke-width="3" stroke-linejoin="round"/>';
        }],
        ['#ffe9ec', 'Картошка', function () {
            return '<path d="M12 36C8 18 26 8 40 10q18 4 14 26T34 58Q14 56 12 36z" fill="#c9a06b"/>' + circ(22, 24, 1.8, '#a07a47') + circ(44, 44, 1.8, '#a07a47') + circ(46, 22, 1.8, '#a07a47') +
                rect(15, 26, 15, 10, 4, D) + rect(34, 26, 15, 10, 4, D) + rect(29, 29, 6, 3, 1, D) + circ(21, 29, 2, '#fff') + circ(41, 29, 2, '#fff') + smile(46, 6) + tongue(34, 48);
        }],
        ['#e3f0ff', 'Сырок', function () {
            return poly('M4 52L18 12q14-8 42 6z', '#ffd23f') + poly('M4 52h56v-8H4z', '#f2b705') + circ(30, 22, 4, '#f2b705') + circ(46, 30, 3, '#f2b705') + circ(16, 36, 2.6, '#f2b705') +
                eye(26, 36, 3) + eye(42, 36, 3) + smile(42, 5);
        }],
        ['#ffe0f3', 'Единорог', function () {
            return poly('M32 2l5 18H27z', '#ffd23f') + poly('M12 30L12 12l14 10zM52 30V12L38 22z', '#f4f0ff') +
                '<path d="M10 40C4 24 12 14 22 14l-4 22zM54 40C60 24 52 14 42 14l4 22z" fill="#ff7ac8"/>' + circ(32, 36, 20, '#fff') + '<path d="M22 14q10-6 20 0l-4 6h-12z" fill="#7ad7ff"/>' +
                eye(24, 36, 3) + eye(40, 36, 3) + smile(44, 4) + cheeks('#ffb0d8');
        }],
        ['#e1f7e1', 'Динозаврик', function () {
            return poly('M18 10l5 8-9 1zM30 6l5 9h-10zM42 10l1 8-9-1z', '#f2994a') + circ(32, 38, 22, '#59c36a') + circ(18, 44, 3, '#3e9e50') + circ(46, 28, 3, '#3e9e50') +
                eye(24, 32, 3) + eye(40, 32, 3) + circ(28, 41, 1.4, '#3e9e50') + circ(36, 41, 1.4, '#3e9e50') +
                '<path d="M20 46q12 9 24 0" fill="#fff" stroke="' + D + '" stroke-width="2"/><path d="M26 49l2 3 2-3M34 49l2 3 2-3" fill="none" stroke="' + D + '" stroke-width="1.4"/>';
        }],
        ['#d9f0ff', 'Солнышко', function () {
            var r = '';
            for (var i = 0; i < 12; i++) r += '<path d="M32 4v8" stroke="#ff9f1c" stroke-width="4" stroke-linecap="round" transform="rotate(' + (i * 30) + ' 32 34)"/>';
            return r + circ(32, 34, 20, '#ffd23f') + rect(14, 26, 16, 10, 5, D) + rect(34, 26, 16, 10, 5, D) + rect(28, 29, 8, 3, 1, D) +
                '<path d="M20 42q12 12 24 0z" fill="' + D + '"/>' + tongue(36, 48).replace('#ff6b8b', '#ff6b8b') + cheeks('#ff9f6b');
        }],
        ['#e9e2ff', 'Осьминог', function () {
            return '<path d="M8 40q0-34 24-34t24 34q-2 8-4 6-2 12-4 8-3 4-4-2-2 6-4 2-4 6-4 0-4 6-4-2-2 6-4-4-4 2-4-8-4-6z" fill="#a45fe0"/>' +
                '<ellipse cx="22" cy="28" rx="5" ry="6" fill="#fff"/><ellipse cx="42" cy="28" rx="5" ry="6" fill="#fff"/>' + circ(23, 29, 2.6, D) + circ(41, 29, 2.6, D) +
                '<path d="M26 40q6 5 12 0" stroke="' + D + '" stroke-width="2.2" fill="none" stroke-linecap="round"/>' + circ(32, 16, 3, '#c88bff') + circ(20, 38, 2, '#c88bff') + circ(44, 38, 2, '#c88bff');
        }]
    ];

    var cache = {};

    function fix(id, fallback) {
        id = parseInt(id, 10);
        if (isNaN(id) || id < 0) id = parseInt(fallback, 10) || 0;
        return id % A.length;
    }

    function svg(id, fallback) {
        id = fix(id, fallback);
        if (!cache[id]) {
            var a = A[id];
            cache[id] = '<svg viewBox="0 0 64 64" aria-hidden="true" focusable="false"><circle cx="32" cy="32" r="32" fill="' + a[0] + '"/>' +
                '<g transform="translate(32 33) scale(.9) translate(-32 -32)">' + a[2]() + '</g></svg>';
        }
        return cache[id];
    }

    // A ready element: <span class="qz-av">…</span>; size is set by CSS (.qz-av-s / -m / -l / -xl)
    function el(id, size, fallback) {
        var span = document.createElement('span');
        span.className = 'qz-av qz-av-' + (size || 'm');
        span.innerHTML = svg(id, fallback);
        return span;
    }

    function name(id) { return A[fix(id)][1]; }

    window.QuizAvatars = {count: A.length, svg: svg, el: el, name: name, fix: fix};
})();
