// Admins' attendance dashboard. Plain HTTP polling once a minute; all text goes in through textContent.
(function () {
    'use strict';
    var root = document.getElementById('attendance');
    if (!root) return;
    var L = JSON.parse(root.dataset.labels);
    var tip = document.getElementById('at-tip');
    var period = {pages: 'today', sources: 'today'};
    var data = null, busy = false;

    function $(id) { return document.getElementById(id); }

    function el(tag, cls, text) {
        var node = document.createElement(tag);
        if (cls) node.className = cls;
        if (text !== undefined && text !== null) node.textContent = text;
        return node;
    }

    function num(value) { return Number(value).toLocaleString('ru-RU'); }

    function shortDate(iso) { return iso.slice(8, 10) + '.' + iso.slice(5, 7); }

    function showTip(target, lines) {
        tip.textContent = '';
        lines.forEach(function (line, i) { tip.appendChild(el(i ? 'span' : 'b', null, line)); });
        tip.hidden = false;
        var box = target.getBoundingClientRect(), host = root.getBoundingClientRect();
        var left = box.left - host.left + box.width / 2 - tip.offsetWidth / 2;
        tip.style.left = Math.max(0, Math.min(left, host.width - tip.offsetWidth)) + 'px';
        tip.style.top = (box.top - host.top - tip.offsetHeight - 6) + 'px';
    }

    function withTip(node, lines, pointerOnly) {
        // The heat map has 168 cells: they are named for screen readers but kept out of the Tab order.
        if (pointerOnly) node.setAttribute('role', 'img');
        else node.tabIndex = 0;
        node.setAttribute('aria-label', lines.join(', '));
        node.addEventListener('pointerenter', function () { showTip(node, lines); });
        node.addEventListener('focus', function () { showTip(node, lines); });
        node.addEventListener('pointerleave', function () { tip.hidden = true; });
        node.addEventListener('blur', function () { tip.hidden = true; });
    }

    // Column chart: every item has stacked parts [{value, cls}], an optional reference mark and tooltip lines.
    function columns(box, items, every) {
        var max = 1;
        items.forEach(function (item) {
            var sum = item.parts.reduce(function (a, p) { return a + p.value; }, 0);
            max = Math.max(max, sum, item.mark || 0);
        });
        box.textContent = '';
        box.appendChild(el('span', 'at-max', num(max)));
        var plot = el('div', 'at-plot'), axis = el('div', 'at-axis');
        items.forEach(function (item, i) {
            var column = el('div', 'at-col'), stack = el('div', 'at-stack');
            item.parts.forEach(function (part) {
                if (!part.value) return;
                var bar = el('i', 'at-bar ' + part.cls);
                bar.style.height = (part.value * 100 / max) + '%';
                stack.appendChild(bar);
            });
            column.appendChild(stack);
            if (item.mark) {
                var mark = el('i', 'at-mark');
                mark.style.bottom = (item.mark * 100 / max) + '%';
                column.appendChild(mark);
            }
            withTip(column, item.tip);
            plot.appendChild(column);
            var shown = (items.length - 1 - i) % every === 0;
            axis.appendChild(el('span', shown ? null : 'at-blank', shown ? item.label : ''));
        });
        box.appendChild(plot);
        box.appendChild(axis);
    }

    function legend(box, entries) {
        box.textContent = '';
        entries.forEach(function (entry) {
            var item = el('span');
            item.appendChild(el('i', entry[0]));
            item.appendChild(document.createTextNode(entry[1]));
            box.appendChild(item);
        });
    }

    function tiles(d) {
        var box = $('at-tiles'), last = d.activity[d.activity.length - 1];
        box.textContent = '';
        function tile(title, value, sub) {
            var node = el('div', 'at-tile');
            node.appendChild(el('span', 'at-tile-title', title));
            node.appendChild(el('b', null, value));
            node.appendChild(el('small', null, sub));
            box.appendChild(node);
        }
        function split(x) { return L.users + ' ' + num(x.users) + ' · ' + L.guests + ' ' + num(x.guests); }
        tile(L.visitors + ' · ' + L.today, num(d.today.visitors), split(d.today));
        tile(L.views + ' · ' + L.today, num(d.today.views), L.yesterday + ' ' + num(d.yesterday.views));
        tile(L.peak, num(d.today.peak), d.today.peak_time || '—');
        tile(L.visitors + ' · ' + L.week, num(d.week.visitors), split(d.week));
        tile(L.visitors + ' · ' + L.month, num(d.month.visitors), split(d.month));
        tile(L.submissions + ' · ' + L.today, num(last.submissions), L.authors + ' ' + num(last.authors));
        tile(L.registrations + ' · ' + L.today, num(last.registrations),
             L.month + ' ' + num(d.activity.reduce(function (a, r) { return a + r.registrations; }, 0)));
    }

    function hours(d) {
        legend($('at-hours-legend'), [['at-users', L.today], ['at-key-mark', L.yesterday]]);
        columns($('at-hours'), d.hours.today.map(function (row, h) {
            var before = d.hours.yesterday[h].visitors, time = (h < 10 ? '0' : '') + h + ':00';
            return {
                label: String(h),
                parts: [{value: row.visitors, cls: 'at-users'}],
                mark: before,
                tip: [time, L.visitors + ': ' + num(row.visitors), L.views + ': ' + num(row.views),
                      L.yesterday + ': ' + num(before)]
            };
        }), 3);
    }

    function days(d) {
        legend($('at-days-legend'), [['at-users', L.users], ['at-guests', L.guests]]);
        columns($('at-days'), d.days.map(function (row) {
            return {
                label: shortDate(row.date),
                parts: [{value: row.users, cls: 'at-users'}, {value: row.guests, cls: 'at-guests'}],
                tip: [shortDate(row.date), L.users + ': ' + num(row.users), L.guests + ': ' + num(row.guests),
                      L.views + ': ' + num(row.views)]
            };
        }), 7);

        var table = $('at-days-table');
        table.textContent = '';
        var head = el('tr');
        [L.date, L.users, L.guests, L.views, L.submissions, L.authors, L.registrations, L.quiz_games, L.typing]
            .forEach(function (name) { head.appendChild(el('th', null, name)); });
        table.appendChild(head);
        for (var i = d.days.length - 1; i >= 0; i--) {
            var a = d.activity[i], v = d.days[i], row = el('tr');
            [shortDate(v.date), v.users, v.guests, v.views, a.submissions, a.authors, a.registrations,
             a.quiz_games, a.typing].forEach(function (cell) { row.appendChild(el('td', null, cell)); });
            table.appendChild(row);
        }
    }

    function heat(d) {
        var box = $('at-heat'), max = 0;
        d.heat.forEach(function (row) { max = Math.max.apply(null, row.concat(max)); });
        box.textContent = '';
        box.appendChild(el('span'));
        for (var h = 0; h < 24; h++) box.appendChild(el('span', 'at-heat-hour', h % 3 ? '' : h));
        d.heat.forEach(function (row, day) {
            box.appendChild(el('span', 'at-heat-day', L.weekdays[day]));
            row.forEach(function (value, hour) {
                var cell = el('i', 'at-cell');
                if (value) cell.style.setProperty('--level', Math.round(12 + 88 * value / max) + '%');
                withTip(cell, [L.weekdays[day] + ' ' + (hour < 10 ? '0' : '') + hour + ':00',
                               L.visitors + ': ' + num(value)], true);
                box.appendChild(cell);
            });
        });
    }

    function activity(d) {
        ['submissions', 'registrations', 'quiz_games', 'typing'].forEach(function (key) {
            var total = 0;
            columns($('at-act-' + key), d.activity.map(function (row) {
                total += row[key];
                var lines = [shortDate(row.date), L[key] + ': ' + num(row[key])];
                if (key === 'submissions') lines.push(L.authors + ': ' + num(row.authors));
                return {label: shortDate(row.date), parts: [{value: row[key], cls: 'at-users'}], tip: lines};
            }), 14);
            $('at-total-' + key).textContent = num(total);
        });
    }

    function list(id, rows) {
        var box = $(id);
        box.textContent = '';
        if (!rows.length) {
            box.appendChild(el('li', 'at-empty', L.empty));
            return;
        }
        var max = Math.max.apply(null, rows.map(function (r) { return r.value; })) || 1;
        rows.forEach(function (r) {
            var item = el('li'), name = el(r.url ? 'a' : 'span', 'at-name', r.title);
            if (r.url) name.href = r.url;
            var bar = el('i', 'at-meter');
            bar.style.width = (r.value * 100 / max) + '%';
            item.appendChild(name);
            item.appendChild(el('span', 'at-value', num(r.value)));
            item.appendChild(bar);
            box.appendChild(item);
        });
    }

    function lists(d) {
        list('at-pages', d.pages[period.pages].map(function (p) {
            return {title: p.title, url: p.url, value: p.views};
        }));
        list('at-sources', d.sources[period.sources].map(function (s) { return {title: s[0], value: s[1]}; }));
        list('at-devices', ['desktop', 'mobile', 'tablet'].map(function (k) {
            return {title: L[k], value: d.devices[k]};
        }).filter(function (r) { return r.value; }));
        list('at-browsers', d.browsers.map(function (b) {
            return {title: b[0] === 'other' ? L.other : b[0], value: b[1]};
        }));
    }

    function render(d) {
        data = d;
        tip.hidden = true;
        var note = L.updated + ' ' + d.generated;
        if (d.since) note += ' · ' + L.since + ' ' + d.since.split('-').reverse().join('.');
        $('at-note').textContent = note;
        tiles(d);
        hours(d);
        days(d);
        heat(d);
        activity(d);
        lists(d);
    }

    Array.prototype.forEach.call(root.querySelectorAll('.at-switch'), function (group) {
        group.addEventListener('click', function (event) {
            var button = event.target.closest('button');
            if (!button) return;
            period[group.dataset.list] = button.dataset.period;
            Array.prototype.forEach.call(group.children, function (b) { b.classList.toggle('active', b === button); });
            if (data) lists(data);
        });
    });

    function poll() {
        if (busy || document.visibilityState !== 'visible') return;
        busy = true;
        fetch(root.dataset.url, {credentials: 'same-origin', headers: {'X-Requested-With': 'XMLHttpRequest'}})
            .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
            .then(render)
            .catch(function () { $('at-note').textContent = L.failed; })
            .then(function () { busy = false; });
    }

    document.addEventListener('visibilitychange', poll);
    setInterval(poll, 60000);
    poll();
})();
