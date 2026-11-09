/* Endless lists: instead of the page buttons 1 2 3 the next page is loaded by itself when the reader
 * scrolls near the end of the list. Works on every list that has a pagination bar:
 *   - the bar: .bottom-pagination-bar (templates/list-pages.html) or .qz-pages (quiz catalog);
 *   - the next page: the link with rel="next" inside the bar;
 *   - the items: the element marked data-infinite-items, otherwise the last <tbody> before the bar.
 * Without JavaScript the page buttons stay as they are. */
(function () {
    'use strict';
    var BAR = '.bottom-pagination-bar, .qz-pages';
    var RETRY = {
        ru: 'Не удалось загрузить продолжение. Повторить',
        ky: 'Уландысын жүктөө мүмкүн болгон жок. Кайталоо',
        en: 'Could not load more. Try again'
    };

    function itemsFor(bar, root) {
        var marked = root.querySelectorAll('[data-infinite-items]');
        var before = function (el) {
            return el.compareDocumentPosition(bar) & Node.DOCUMENT_POSITION_FOLLOWING;
        };
        var list = Array.prototype.filter.call(marked, before);
        if (!list.length) list = Array.prototype.filter.call(root.querySelectorAll('tbody'), before);
        return list.length ? list[list.length - 1] : null;
    }

    function nextUrl(bar) {
        var a = bar && bar.querySelector('a[rel~="next"]');
        return a ? a.href : null;
    }

    function setup(bar, index) {
        var items = itemsFor(bar, document);
        var next = nextUrl(bar);
        if (!items || !next) return;
        bar.classList.add('infinite-on');

        var status = document.createElement('div');
        status.className = 'infinite-status';
        status.setAttribute('aria-live', 'polite');
        bar.parentNode.insertBefore(status, bar);

        var loading = false;
        var observer = null;

        function finish() {
            status.textContent = '';
            if (observer) observer.disconnect();
            window.removeEventListener('scroll', check);
        }

        function load() {
            if (loading || !next) return;
            loading = true;
            status.innerHTML = '<i class="fa fa-spinner fa-pulse"></i>';
            fetch(next, {credentials: 'same-origin', headers: {'X-Requested-With': 'infinite-scroll'}})
                .then(function (r) {
                    if (!r.ok) throw new Error(r.status);
                    return r.text();
                })
                .then(function (html) {
                    var doc = new DOMParser().parseFromString(html, 'text/html');
                    var bars = doc.querySelectorAll(BAR);
                    var newBar = bars[index] || bars[bars.length - 1] || null;
                    var newItems = newBar ? itemsFor(newBar, doc) : null;
                    var added = [];
                    if (newItems) {
                        Array.prototype.slice.call(newItems.children).forEach(function (el) {
                            // A list that changes while it is read (new submissions) may repeat a row.
                            if (el.id && document.getElementById(el.id)) return;
                            added.push(document.importNode(el, true));
                        });
                    }
                    added.forEach(function (el) { items.appendChild(el); });
                    next = nextUrl(newBar);
                    loading = false;
                    status.textContent = '';
                    refresh(items, added);
                    if (!next || !added.length) finish();
                    else check();
                })
                .catch(function () {
                    loading = false;
                    status.innerHTML = '';
                    var retry = document.createElement('a');
                    retry.href = '#';
                    retry.className = 'infinite-retry';
                    retry.textContent = RETRY[(document.documentElement.lang || 'ru').slice(0, 2)] || RETRY.ru;
                    retry.addEventListener('click', function (e) { e.preventDefault(); load(); });
                    status.appendChild(retry);
                });
        }

        function check() {
            if (loading || !next) return;
            var rect = status.getBoundingClientRect();
            if (rect.top < window.innerHeight + 900) load();
        }

        if ('IntersectionObserver' in window) {
            observer = new IntersectionObserver(function (entries) {
                if (entries.some(function (e) { return e.isIntersecting; })) load();
            }, {rootMargin: '0px 0px 900px 0px'});
            observer.observe(status);
        } else {
            window.addEventListener('scroll', check, {passive: true});
        }
        check();
    }

    // Bring the new rows to life like the ones that came with the page.
    function refresh(items, added) {
        if (!added.length) return;
        var $ = window.jQuery;
        if ($) {
            var $added = $(added);
            if (typeof window.register_time === 'function') {
                window.register_time($added.find('.time-with-rel').addBack('.time-with-rel'));
            }
            if ($.fn.unveil) $added.find('img[data-src]').unveil(200);
            var $table = $(items).closest('table');
            if ($table.length && $table[0].config) $table.trigger('update');
        }
        document.dispatchEvent(new CustomEvent('infinite-scroll:loaded', {detail: {items: items, added: added}}));
    }

    function start() {
        var style = document.createElement('style');
        style.textContent = '.infinite-on { display: none !important; }' +
            '.infinite-status { text-align: center; min-height: 1px; margin: 12px 0; color: #888; }' +
            '.infinite-retry { text-decoration: underline; }';
        document.head.appendChild(style);
        Array.prototype.forEach.call(document.querySelectorAll(BAR), setup);
    }

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
    else start();
})();
