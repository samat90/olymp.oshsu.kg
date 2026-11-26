// "Online now" for admins (home page and attendance dashboard). Plain HTTP polling: works behind the proxy.
(function () {
    var box = document.getElementById('online-live'), groups = document.getElementById('online-groups');
    var total = document.getElementById('online-total'), sub = document.getElementById('online-sub');
    var open = {}, busy = false, SHOW = 6;
    function el(tag, cls, text) {
        var e = document.createElement(tag);
        if (cls) e.className = cls;
        if (text !== undefined) e.textContent = text;
        return e;
    }
    function render(d) {
        total.textContent = d.total;
        sub.textContent = d.users + ' + ' + d.guests;
        groups.textContent = '';
        d.groups.forEach(function (g) {
            var row = el('div', 'online-group online-' + g.kind), head = el('div', 'online-ghead');
            var title = g.url ? el('a', 'online-title', g.title) : el('span', 'online-title', g.title);
            if (g.url) title.href = g.url;
            head.appendChild(title);
            head.appendChild(el('span', 'online-count', g.count));
            row.appendChild(head);
            var names = g.users, list = el('div', 'online-names'), key = g.title;
            var shown = open[key] ? names : names.slice(0, SHOW);
            shown.forEach(function (n) { list.appendChild(el('span', 'online-name', n)); });
            if (g.guests) list.appendChild(el('span', 'online-name online-guest', '+' + g.guests));
            var hidden = names.length - shown.length + (open[key] ? g.more : 0);
            if (hidden > 0) {
                var more = el('button', 'online-more', '+' + hidden);
                more.type = 'button';
                more.onclick = function () { open[key] = !open[key]; render(d); };
                list.appendChild(more);
            }
            row.appendChild(list);
            groups.appendChild(row);
        });
        box.hidden = false;
    }
    function poll() {
        if (busy || document.visibilityState !== 'visible') return;
        busy = true;
        fetch(box.dataset.url, {credentials: 'same-origin', headers: {'X-Requested-With': 'XMLHttpRequest'}})
            .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
            .then(render)
            .catch(function () {})
            .then(function () { busy = false; });
    }
    document.addEventListener('visibilitychange', poll);
    setInterval(poll, 10000);
    poll();
})();
