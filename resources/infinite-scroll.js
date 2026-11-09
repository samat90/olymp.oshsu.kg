/* Lists without page numbers: the next page is fetched over plain HTTP (no WebSocket, the university
 * proxy blocks it) when the reader nears the bottom, and its rows are appended to the list.
 *
 * Markup: a pager element with data-infinite="<selector of the list container>" holding a link
 * a[rel=next]. Without JavaScript the pager stays visible and works as before.
 * Django admin change lists (p.paginator) are handled too, see admin_pager(). */
(function () {
    'use strict';
    if (!window.fetch || !window.DOMParser || !document.querySelector) return;

    function admin_next(pager) {
        var cur = pager.querySelector('.this-page');
        var a = cur && cur.nextElementSibling;
        return a && a.tagName === 'A' && !a.classList.contains('showall') ? a : null;
    }

    function next_link(pager) {
        return pager.querySelector('a[rel~="next"]') || (pager.classList.contains('paginator') ? admin_next(pager) : null);
    }

    function after_append(list, nodes) {
        var $ = window.jQuery;
        if ($) {
            var $nodes = $(nodes);
            if (window.register_time) window.register_time($nodes.find('.time-with-rel').addBack('.time-with-rel'));
            if ($.fn.unveil) $nodes.find('img.unveil').unveil(200);
            if ($.fn.tablesorter) $(list).closest('table').trigger('update');
        }
        var toggle = document.getElementById('action-toggle');
        if (toggle && toggle.checked) nodes.forEach(function (n) {
            var box = n.querySelector && n.querySelector('input.action-select');
            if (box) { box.checked = true; n.classList.add('selected'); }
        });
        document.dispatchEvent(new CustomEvent('infinite:append', {detail: {list: list, nodes: nodes}}));
    }

    function setup(pager, selector) {
        var list = document.querySelector(selector);
        var link = next_link(pager);
        if (!list || !link) return;
        var url = new URL(link.getAttribute('href'), location.href).href;
        var pager_index = Array.prototype.indexOf.call(document.querySelectorAll(pager_query(pager)), pager);

        pager.classList.add(pager.hasAttribute('data-infinite') ? 'inf-hidden' : 'inf-admin');
        var box = document.createElement('div');
        box.className = 'inf-more';
        box.innerHTML = '<span class="inf-spin" aria-hidden="true"></span>';
        pager.parentNode.insertBefore(box, pager.nextSibling);

        var busy = false;
        var observer;

        function finish() {
            if (observer) observer.disconnect();
            box.parentNode && box.parentNode.removeChild(box);
        }

        function fail() {
            busy = false;
            box.classList.remove('inf-loading');
            box.innerHTML = '<button type="button" class="inf-retry" aria-label="&#8635;">&#8635;</button>';
            box.firstChild.addEventListener('click', function () {
                box.innerHTML = '<span class="inf-spin" aria-hidden="true"></span>';
                load();
            });
        }

        function load() {
            if (busy || !url) return;
            busy = true;
            box.classList.add('inf-loading');
            fetch(url, {credentials: 'same-origin'}).then(function (r) {
                if (!r.ok) throw new Error(r.status);
                return r.text();
            }).then(function (html) {
                var doc = new DOMParser().parseFromString(html, 'text/html');
                var src = doc.querySelector(selector);
                var nodes = [];
                if (src) Array.prototype.slice.call(src.children).forEach(function (n) {
                    // A list that changes while reading (new submissions on top) shifts the pages:
                    // rows already shown are not added twice.
                    if (n.id && document.getElementById(n.id)) return;
                    n = document.adoptNode(n);
                    list.appendChild(n);
                    nodes.push(n);
                });
                if (nodes.length) after_append(list, nodes);
                var pagers = doc.querySelectorAll(pager_query(pager));
                var next = pagers.length ? next_link(pagers[Math.min(pager_index, pagers.length - 1)]) : null;
                var base = url;
                url = next ? new URL(next.getAttribute('href'), base).href : null;
                busy = false;
                box.classList.remove('inf-loading');
                if (!url || !src) return finish();
                // Short pages: keep loading until the screen is filled.
                if (box.getBoundingClientRect().top < window.innerHeight + 600) setTimeout(load, 50);
            }).catch(fail);
        }

        if ('IntersectionObserver' in window) {
            observer = new IntersectionObserver(function (entries) {
                if (entries[0].isIntersecting) load();
            }, {rootMargin: '0px 0px 600px 0px'});
            observer.observe(box);
        } else {
            window.addEventListener('scroll', function () {
                if (box.getBoundingClientRect().top < window.innerHeight + 600) load();
            }, {passive: true});
            load();
        }
    }

    function pager_query(pager) {
        return pager.hasAttribute('data-infinite') ? '[data-infinite]' : 'p.paginator';
    }

    function add_style() {
        var css = '.inf-hidden{display:none!important}' +
            '.inf-admin>a:not(.showall),.inf-admin>.this-page{display:none!important}' +
            '.inf-more{display:flex;justify-content:center;padding:14px 0;min-height:24px}' +
            '.inf-spin{width:22px;height:22px;border-radius:50%;border:3px solid rgba(127,127,127,.25);' +
            'border-top-color:currentColor;opacity:0;animation:inf-rot .8s linear infinite}' +
            '.inf-loading .inf-spin{opacity:.7}' +
            '.inf-retry{font-size:20px;line-height:1;padding:4px 14px;cursor:pointer;border-radius:8px;' +
            'border:1px solid rgba(127,127,127,.4);background:none;color:inherit}' +
            '@keyframes inf-rot{to{transform:rotate(360deg)}}';
        var el = document.createElement('style');
        el.textContent = css;
        document.head.appendChild(el);
    }

    function init() {
        add_style();
        Array.prototype.forEach.call(document.querySelectorAll('[data-infinite]'), function (pager) {
            setup(pager, pager.getAttribute('data-infinite'));
        });
        // Django admin: not for editable lists, their form counts the rows it was rendered with.
        var admin = document.querySelector('#changelist p.paginator');
        if (admin && document.querySelector('#result_list tbody') &&
            !document.querySelector('#changelist-form input[name$="TOTAL_FORMS"]')) {
            setup(admin, '#result_list tbody');
            Array.prototype.forEach.call(admin.childNodes, function (n) {
                if (n.nodeType === 3 && /…|\.\.\./.test(n.nodeValue)) n.nodeValue = n.nodeValue.replace(/…|\.\.\./g, '');
            });
        }
    }

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
    else init();
})();
