/* Courses: lesson tree on phones, confirmation of dangerous buttons. No WebSocket, no polling. */
(function () {
    'use strict';
    document.addEventListener('click', function (e) {
        var toggle = e.target.closest('[data-co-tree]');
        if (toggle) {
            var tree = document.querySelector('.co-tree');
            if (tree) tree.classList.toggle('co-collapsed');
        }
        // The site disables every submit button when a form is submitted, which drops the name and value
        // of the pressed button: keep them in a hidden field instead.
        var button = e.target.closest('button[name], input[type=submit][name]');
        if (button && button.form && (button.type === 'submit')) {
            var old = button.form.querySelectorAll('input.co-submitter');
            for (var i = 0; i < old.length; i++) old[i].remove();
            var field = document.createElement('input');
            field.type = 'hidden';
            field.className = 'co-submitter';
            field.name = button.name;
            field.value = button.value;
            button.form.appendChild(field);
        }
    });
    // Capture phase: a cancelled confirmation must stop before the site's handler disables the buttons.
    document.addEventListener('submit', function (e) {
        var message = e.target.getAttribute('data-confirm') ||
            (e.submitter && e.submitter.getAttribute('data-confirm'));
        if (message && !window.confirm(message)) {
            e.preventDefault();
            e.stopPropagation();
        }
    }, true);
    var tree = document.querySelector('.co-tree');
    if (tree && window.matchMedia('(max-width: 900px)').matches) tree.classList.add('co-collapsed');
    var current = document.querySelector('.co-tree .co-current');
    if (current && current.scrollIntoView && !window.matchMedia('(max-width: 900px)').matches) {
        var box = current.closest('.co-tree');
        if (box) box.scrollTop = Math.max(0, current.offsetTop - box.clientHeight / 2);
    }
})();
