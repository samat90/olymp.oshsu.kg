/* Quiz editor: question list with drag-and-drop, a form per question type, autosave, preview, import. */
(function () {
    'use strict';

    var C = window.QUIZ_EDITOR;
    if (!C) return;

    var OPTION_LIMITS = {single: [2, 4], truefalse: [2, 2], multi: [2, 6], order: [3, 6], code: [2, 4], poll: [2, 6]};
    var NEW_OPTIONS = {single: 4, multi: 4, order: 4, poll: 3, code: 4};
    var DATA_DEFAULTS = {
        word: {word: ''}, text: {answers: [], tolerance: 0}, code: {input: false},
        slider: {min: 0, max: 100, step: 1, answer: 50, tolerance: 5, unit: ''}, pin: {x: 50, y: 50, r: 10}
    };
    var TIMES = [5, 10, 20, 30, 60, 90, 120, 240];
    var SAVE_DELAY = 800;
    var TYPES = {};
    C.types.forEach(function (t) { TYPES[t.code] = t; });

    var quiz = C.quiz;
    var questions = C.questions;
    var currentId = questions.length ? questions[0].id : null;
    var showPreview = false;
    var pending = 0;
    var failed = '';

    var $ = function (sel, root) { return (root || document).querySelector(sel); };

    function esc(s) {
        return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
            return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c];
        });
    }

    function el(tag, attrs, children) {
        var node = document.createElement(tag);
        if (attrs) {
            Object.keys(attrs).forEach(function (k) {
                var v = attrs[k];
                if (v == null || v === false) return;
                if (k === 'class') node.className = v;
                else if (k === 'html') node.innerHTML = v;
                else if (k === 'text') node.textContent = v;
                else if (k.slice(0, 2) === 'on') node.addEventListener(k.slice(2), v);
                else if (k in node && k !== 'list' && k !== 'type' && k !== 'spellcheck' && k.indexOf('-') < 0) node[k] = v;
                else node.setAttribute(k, v === true ? '' : v);
            });
        }
        (children || []).forEach(function (c) {
            if (c == null || c === false) return;
            node.appendChild(typeof c === 'string' ? document.createTextNode(c) : c);
        });
        return node;
    }

    function icon(name) { return el('i', {'class': 'fa ' + name, 'aria-hidden': 'true'}); }

    function shapeMark(i) {
        var mark = el('span', {'class': 'qe-mark qz-c' + (i % 6)});
        mark.innerHTML = window.QuizFx && QuizFx.shape ? QuizFx.shape(i) : String(i + 1);
        return mark;
    }

    function csrf() {
        var m = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
        return m ? decodeURIComponent(m[1]) : C.csrf;
    }

    /* ---------------- network ---------------- */

    function api(path, opts) {
        opts = opts || {};
        var init = {method: opts.method || 'GET', credentials: 'same-origin', headers: {'X-CSRFToken': csrf()}};
        if (opts.json !== undefined) {
            init.method = 'POST';
            init.headers['Content-Type'] = 'application/json';
            init.body = JSON.stringify(opts.json);
        } else if (opts.form) {
            init.method = 'POST';
            init.body = opts.form;
        } else if (opts.post) {
            init.method = 'POST';
        }
        return fetch(C.urls.api + path, init).then(function (r) {
            return r.json().catch(function () { return {error: 'Ошибка сервера (' + r.status + ')'}; }).then(function (data) {
                if (!r.ok || data.error) {
                    var err = new Error(data.error || 'Ошибка ' + r.status);
                    err.field = data.field || '';
                    throw err;
                }
                return data;
            });
        }, function () {
            throw new Error('Нет связи с сервером');
        });
    }

    function setStatus() {
        var box = $('#qe-status');
        box.className = 'qe-status';
        if (failed) {
            box.textContent = 'Ошибка: ' + failed;
            box.classList.add('qe-err');
        } else if (pending > 0) {
            box.textContent = 'Сохраняю…';
        } else {
            box.textContent = 'Сохранено';
            box.classList.add('qe-ok');
        }
    }

    function track(promise) {
        pending++;
        setStatus();
        return promise.then(function (v) {
            pending--;
            failed = '';
            setStatus();
            return v;
        }, function (e) {
            pending--;
            failed = e.message;
            setStatus();
            throw e;
        });
    }

    function alertError(e) { window.alert(e.message); }

    function noop() {}

    /* ---------------- autosave of questions ---------------- */

    var timers = {};
    var chains = {};

    function byId(id) {
        for (var i = 0; i < questions.length; i++) if (questions[i].id === id) return questions[i];
        return null;
    }

    function payload(q) {
        return {
            type: q.type, text: q.text, code: q.code, code_language: q.code_language, time_limit: q.time_limit,
            weight: q.weight, explanation: q.explanation, data: q.data,
            options: q.options.map(function (o) { return {id: o.id || null, text: o.text, is_correct: o.is_correct, image: o.image}; })
        };
    }

    function changed(q, now) {
        clearTimeout(timers[q.id]);
        failed = '';
        pending += timers[q.id] ? 0 : 1;
        timers[q.id] = setTimeout(function () { flush(q).catch(noop); }, now ? 0 : SAVE_DELAY);
        setStatus();
    }

    function flush(q) {
        if (timers[q.id]) {
            clearTimeout(timers[q.id]);
            delete timers[q.id];
            pending--;
            var sent = q.options.slice();
            var body = payload(q);
            chains[q.id] = (chains[q.id] || Promise.resolve()).catch(function () {}).then(function () {
                return track(api('question/' + q.id + '/', {json: body})).then(function (data) {
                    var s = data.question;
                    sent.forEach(function (o, i) {
                        if (s.options[i]) { o.id = s.options[i].id; o.image = s.options[i].image; }
                    });
                    q.problems = s.problems;
                    renderList();
                    if (q.id === currentId) {
                        renderProblems(q);
                        clearFieldError();
                        if (showPreview) loadPreview();
                    }
                }, function (e) {
                    if (q.id === currentId) markFieldError(e.field);
                    throw e;
                });
            });
        }
        return chains[q.id] || Promise.resolve();
    }

    function flushAll() {
        return Promise.all(questions.map(flush));
    }

    function markFieldError(field) {
        clearFieldError();
        var input = field && $('[data-field="' + field + '"]', $('#qe-form'));
        if (input) input.classList.add('qe-field-error');
    }

    function clearFieldError() {
        Array.prototype.forEach.call(document.querySelectorAll('.qe-field-error'), function (n) {
            n.classList.remove('qe-field-error');
        });
    }

    window.addEventListener('beforeunload', function (e) {
        if (pending > 0 || Object.keys(timers).length) {
            questions.forEach(function (q) { flush(q).catch(noop); });
            e.preventDefault();
            e.returnValue = '';
        }
    });

    /* ---------------- question list ---------------- */

    var dragId = null;

    function excerpt(q) {
        var text = (q.text || '').replace(/[`*_#>$\\]/g, '').replace(/\s+/g, ' ').trim();
        return text || (q.image ? '(картинка)' : q.code ? '(код)' : '');
    }

    function renderList() {
        var list = $('#qe-list');
        list.innerHTML = '';
        $('#qe-count').textContent = questions.length + ' / ' + C.maxQuestions;
        if (!questions.length) {
            list.appendChild(el('li', {'class': 'qe-empty-list', text: 'Вопросов пока нет. Нажмите «+ Вопрос» или загрузите Excel.'}));
        }
        questions.forEach(function (q, i) {
            var text = excerpt(q);
            var item = el('li', {
                'class': 'qe-item' + (q.id === currentId ? ' qe-sel' : ''), draggable: 'true', 'data-id': q.id,
                title: TYPES[q.type].name,
                onclick: function () { select(q.id); }
            }, [
                el('span', {'class': 'qe-handle', 'aria-hidden': 'true', html: '&#8942;&#8942;'}),
                el('span', {'class': 'qe-num', text: String(i + 1)}),
                icon(TYPES[q.type].icon),
                el('span', {'class': 'qe-item-text' + (text ? '' : ' qe-empty'), text: text || 'Без текста'}),
                q.problems && q.problems.length ? el('span', {'class': 'qe-dot', title: q.problems.join('\n')}) : null,
                el('span', {'class': 'qe-moves'}, [
                    el('button', {type: 'button', title: 'Выше', 'aria-label': 'Выше', disabled: i === 0,
                        onclick: function (e) { e.stopPropagation(); move(i, i - 1); }}, [icon('fa-chevron-up')]),
                    el('button', {type: 'button', title: 'Ниже', 'aria-label': 'Ниже', disabled: i === questions.length - 1,
                        onclick: function (e) { e.stopPropagation(); move(i, i + 1); }}, [icon('fa-chevron-down')])
                ])
            ]);
            item.addEventListener('dragstart', function (e) {
                dragId = q.id;
                item.classList.add('qe-drag');
                e.dataTransfer.effectAllowed = 'move';
                try { e.dataTransfer.setData('text/plain', String(q.id)); } catch (err) { /* old browsers */ }
            });
            item.addEventListener('dragend', function () {
                dragId = null;
                item.classList.remove('qe-drag');
                clearDrop();
            });
            item.addEventListener('dragover', function (e) {
                if (dragId === null || dragId === q.id) return;
                e.preventDefault();
                var rect = item.getBoundingClientRect();
                var after = e.clientY > rect.top + rect.height / 2;
                clearDrop();
                item.classList.add(after ? 'qe-drop-after' : 'qe-drop-before');
            });
            item.addEventListener('drop', function (e) {
                if (dragId === null) return;
                e.preventDefault();
                var rect = item.getBoundingClientRect();
                var after = e.clientY > rect.top + rect.height / 2;
                var from = questions.indexOf(byId(dragId));
                var to = questions.indexOf(q) + (after ? 1 : 0);
                if (from < to) to--;
                clearDrop();
                move(from, to);
            });
            list.appendChild(item);
        });
    }

    function clearDrop() {
        Array.prototype.forEach.call(document.querySelectorAll('.qe-drop-before, .qe-drop-after'), function (n) {
            n.classList.remove('qe-drop-before', 'qe-drop-after');
        });
    }

    function move(from, to) {
        if (from < 0 || to < 0 || to >= questions.length || from === to) return;
        var q = questions.splice(from, 1)[0];
        questions.splice(to, 0, q);
        renderList();
        if (byId(currentId)) renderHead(byId(currentId));
        var ids = questions.map(function (x) { return x.id; });
        track(api('reorder/', {json: {ids: ids}})).catch(alertError);
    }

    function applyOrder(ids) {
        questions.sort(function (a, b) { return ids.indexOf(a.id) - ids.indexOf(b.id); });
    }

    function select(id) {
        var old = byId(currentId);
        if (old) flush(old).catch(noop);
        currentId = id;
        renderList();
        renderForm();
        if (showPreview) loadPreview();
    }

    /* ---------------- adding, duplicating, deleting ---------------- */

    function openPicker() {
        if (questions.length >= C.maxQuestions) {
            window.alert('Не больше ' + C.maxQuestions + ' вопросов в викторине');
            return;
        }
        $('#qe-picker').hidden = false;
        var first = $('.qe-type', $('#qe-picker'));
        if (first) first.focus();
    }

    function closePicker() { $('#qe-picker').hidden = true; }

    function addQuestion(type) {
        closePicker();
        var after = currentId;
        var cur = byId(currentId);
        (cur ? flush(cur) : Promise.resolve()).catch(function () {}).then(function () {
            return track(api('question/', {json: {type: type, after: after}}));
        }).then(function (data) {
            questions.push(data.question);
            applyOrder(data.order);
            currentId = data.question.id;
            renderList();
            renderForm();
            var text = $('#qe-text');
            if (text) text.focus();
        }).catch(alertError);
    }

    function duplicateQuestion(q) {
        flush(q).then(function () {
            return track(api('question/' + q.id + '/duplicate/', {post: true}));
        }).then(function (data) {
            questions.push(data.question);
            applyOrder(data.order);
            select(data.question.id);
        }).catch(alertError);
    }

    function deleteQuestion(q) {
        if (!window.confirm('Удалить вопрос?')) return;
        if (timers[q.id]) { clearTimeout(timers[q.id]); delete timers[q.id]; pending--; }
        var index = questions.indexOf(q);
        (chains[q.id] || Promise.resolve()).catch(function () {}).then(function () {
            return track(api('question/' + q.id + '/delete/', {post: true}));
        }).then(function (data) {
            questions.splice(questions.indexOf(q), 1);
            applyOrder(data.order);
            var next = questions[Math.min(index, questions.length - 1)];
            currentId = next ? next.id : null;
            renderList();
            renderForm();
            if (showPreview) loadPreview();
        }).catch(alertError);
    }

    /* ---------------- question form ---------------- */

    function hasOptions(q) {
        if (q.type === 'code') return !q.data.input;
        return !!OPTION_LIMITS[q.type];
    }

    function changeType(q, type) {
        var oldOptions = q.options.length ? q.options : (q._stash || []);
        q.type = type;
        var data = JSON.parse(JSON.stringify(DATA_DEFAULTS[type] || {}));
        if ((type === 'text' || type === 'code') && q.data.answers) {
            data.answers = q.data.answers.slice();
            data.tolerance = q.data.tolerance || 0;
        }
        if (type === 'word' && q.data.word) data.word = q.data.word;
        q.data = data;
        if (!hasOptions(q)) {
            if (q.options.length) q._stash = q.options.map(function (o) { return {text: o.text, is_correct: o.is_correct}; });
            q.options = [];
        } else if (type === 'truefalse') {
            var correctFirst = !oldOptions.length || oldOptions[0].is_correct || !(oldOptions[1] && oldOptions[1].is_correct);
            q.options = [
                {id: q.options[0] && q.options[0].id, text: 'Верно', is_correct: correctFirst, image: ''},
                {id: q.options[1] && q.options[1].id, text: 'Неверно', is_correct: !correctFirst, image: ''}
            ];
        } else {
            var opts = oldOptions.map(function (o) { return {id: o.id || null, text: o.text, is_correct: o.is_correct, image: o.image || ''}; });
            if (q.options === oldOptions && oldOptions.length && oldOptions[0].text === 'Верно' && oldOptions.length === 2) {
                opts.forEach(function (o) { o.text = ''; o.is_correct = false; });
            }
            var max = OPTION_LIMITS[type][1];
            opts = opts.slice(0, max);
            while (opts.length < (NEW_OPTIONS[type] || 2)) opts.push({id: null, text: '', is_correct: false, image: ''});
            if (type === 'poll' || type === 'order') opts.forEach(function (o) { o.is_correct = false; });
            if (type === 'single' || type === 'code') {
                var seen = false;
                opts.forEach(function (o) { o.is_correct = o.is_correct && !seen; seen = seen || o.is_correct; });
            }
            q.options = opts;
            delete q._stash;
        }
        if (type === 'code' && !q.code_language) q.code_language = 'python';
        changed(q, true);
        renderList();
        renderForm();
    }

    function field(label, control, hint) {
        return el('div', {'class': 'qe-field'}, [
            label ? el('label', {text: label}) : null, control, hint ? el('div', {'class': 'qe-hint', html: hint}) : null
        ]);
    }

    function input(q, attrs, get, set) {
        attrs = Object.assign({type: 'text', value: get()}, attrs);
        attrs.oninput = function (e) { set(e.target.value); changed(q); };
        return el('input', attrs);
    }

    function numberInput(q, key, label, attrs) {
        return field(label, input(q, Object.assign({type: 'number', step: 'any', 'data-field': key}, attrs || {}),
            function () { return q.data[key]; },
            function (v) { q.data[key] = v === '' ? '' : Number(v); if (q.type === 'slider') renderSliderPreview(q); }));
    }

    function textarea(q, attrs, key) {
        attrs = Object.assign({value: q[key] || '', 'data-field': key}, attrs);
        attrs.oninput = function (e) { q[key] = e.target.value; changed(q); if (key === 'text') renderList(); };
        var node = el('textarea', attrs);
        node.value = q[key] || '';
        return node;
    }

    function renderHead(q) {
        var head = $('#qe-form-head');
        if (!head) return;
        $('.qe-qnum', head).textContent = 'Вопрос ' + (questions.indexOf(q) + 1);
    }

    function renderProblems(q) {
        var box = $('#qe-problems');
        if (!box) return;
        box.innerHTML = '';
        (q.problems || []).forEach(function (p) { box.appendChild(el('div', {text: p})); });
        box.hidden = !(q.problems && q.problems.length);
    }

    function renderForm() {
        var form = $('#qe-form');
        form.innerHTML = '';
        var q = byId(currentId);
        if (!q) {
            form.appendChild(el('div', {'class': 'qe-panel'}, [
                el('p', {text: 'Добавьте первый вопрос: нажмите «+ Вопрос» слева или импортируйте вопросы из Excel.'}),
                el('button', {type: 'button', 'class': 'qe-btn qe-primary', onclick: openPicker}, [icon('fa-plus'), ' Вопрос'])
            ]));
            return;
        }
        var typeSelect = el('select', {'aria-label': 'Тип вопроса', onchange: function (e) { changeType(q, e.target.value); }},
            C.types.map(function (t) { return el('option', {value: t.code, text: t.name, selected: t.code === q.type}); }));
        form.appendChild(el('div', {'class': 'qe-form-head', id: 'qe-form-head'}, [
            el('span', {'class': 'qe-qnum', text: 'Вопрос ' + (questions.indexOf(q) + 1)}),
            typeSelect,
            el('span', {'class': 'qe-spacer'}),
            el('button', {type: 'button', 'class': 'qe-btn qe-small' + (showPreview ? ' qe-on' : ''), onclick: togglePreview},
                [icon('fa-mobile'), ' Предпросмотр']),
            el('button', {type: 'button', 'class': 'qe-btn qe-small', title: 'Дублировать', onclick: function () { duplicateQuestion(q); }},
                [icon('fa-clone'), el('span', {text: ' Копия'})]),
            el('button', {type: 'button', 'class': 'qe-btn qe-small qe-danger', title: 'Удалить вопрос', onclick: function () { deleteQuestion(q); }},
                [icon('fa-trash')])
        ]));
        form.appendChild(el('div', {'class': 'qe-problems', id: 'qe-problems'}));
        renderProblems(q);

        var main = el('div', {'class': 'qe-panel'});
        main.appendChild(field('Текст вопроса', textarea(q, {id: 'qe-text', rows: 3, maxLength: 2000,
            placeholder: q.type === 'truefalse' ? 'Утверждение, например: «Вода кипит при 100 °C»' : 'Например: Сколько байт в килобайте?'}, 'text'),
            'Можно **жирный**, *курсив*, `код` и формулы в $...$'));
        main.appendChild(codeBlock(q));
        main.appendChild(imageBlock(q));
        form.appendChild(main);

        var answer = answerBlock(q);
        if (answer) form.appendChild(answer);

        var timeInput = el('input', {type: 'number', min: 5, max: 240, step: 1, value: q.time_limit, 'data-field': 'time_limit',
            'aria-label': 'Секунд',
            oninput: function (e) {
                var v = parseInt(e.target.value, 10);
                if (v >= 5 && v <= 240) { q.time_limit = v; markChips(); changed(q); }
            }});
        var chips = el('span', {'class': 'qe-chips'}, TIMES.map(function (t) {
            return el('button', {type: 'button', 'class': 'qe-chip', 'data-t': t, text: t < 60 ? t + ' с' : (t / 60) + ' мин',
                onclick: function () { q.time_limit = t; timeInput.value = t; markChips(); changed(q); }});
        }));
        function markChips() {
            Array.prototype.forEach.call(chips.children, function (c) { c.classList.toggle('qe-on', +c.getAttribute('data-t') === q.time_limit); });
        }
        markChips();
        var settings = el('div', {'class': 'qe-panel'}, [
            field('Время на ответ', el('div', {'class': 'qe-time'}, [chips, timeInput, el('span', {text: 'с'})]))
        ]);
        if (TYPES[q.type].scored) {
            var seg = el('div', {'class': 'qe-seg', role: 'group', 'aria-label': 'Очки'}, C.weights.map(function (w) {
                return el('button', {type: 'button', 'class': q.weight === w[0] ? 'qe-on' : '', text: w[1],
                    onclick: function () {
                        q.weight = w[0];
                        Array.prototype.forEach.call(seg.children, function (b) { b.classList.remove('qe-on'); });
                        this.classList.add('qe-on');
                        changed(q);
                    }});
            }));
            settings.appendChild(field('Очки', seg));
        }
        settings.appendChild(field('Пояснение после ответа', textarea(q, {rows: 2, maxLength: 2000,
            placeholder: 'Необязательно: почему ответ именно такой'}, 'explanation')));
        form.appendChild(settings);
    }

    function codeBlock(q) {
        var need = q.type === 'code';
        var box = el('div', {'class': 'qe-field'});
        if (!need && !q.code && !q._showCode) {
            box.appendChild(el('button', {type: 'button', 'class': 'qe-btn qe-small', onclick: function () { q._showCode = true; renderForm(); }},
                [icon('fa-code'), ' Добавить код']));
            return box;
        }
        var lang = el('select', {'aria-label': 'Язык', style: 'width:auto', onchange: function (e) { q.code_language = e.target.value; changed(q); }},
            [el('option', {value: '', text: 'Язык…'})].concat(C.languages.map(function (l) {
                return el('option', {value: l[0], text: l[1], selected: l[0] === q.code_language});
            })));
        var area = textarea(q, {rows: 6, maxLength: 4000, 'class': 'qe-code', spellcheck: 'false',
            placeholder: need ? 'Программа, вывод которой нужно угадать' : 'Фрагмент кода к вопросу'}, 'code');
        area.addEventListener('keydown', function (e) {
            if (e.key === 'Tab' && !e.shiftKey) {
                e.preventDefault();
                var s = area.selectionStart;
                area.value = area.value.slice(0, s) + '    ' + area.value.slice(area.selectionEnd);
                area.selectionStart = area.selectionEnd = s + 4;
                q.code = area.value;
                changed(q);
            }
        });
        box.appendChild(el('div', {'class': 'qe-row', style: 'margin-bottom:5px'}, [
            el('span', {'class': 'qe-label', style: 'margin:0', text: 'Код'}), lang,
            !need ? el('button', {type: 'button', 'class': 'qe-btn qe-small qe-danger', onclick: function () {
                q.code = ''; q._showCode = false; changed(q); renderForm();
            }}, [icon('fa-times'), ' Убрать код']) : null
        ]));
        box.appendChild(area);
        return box;
    }

    function pickFile(accept, onFile) {
        var picker = $('#qe-file');
        picker.accept = accept;
        picker.value = '';
        picker.onchange = function () { if (picker.files[0]) onFile(picker.files[0]); };
        picker.click();
    }

    function uploadImage(q, optionIndex, file, remove) {
        var start = optionIndex == null ? flush(q) : flush(q).then(function () {
            if (!q.options[optionIndex].id) { changed(q, true); return flush(q); }
        });
        return start.then(function () {
            var form = new FormData();
            if (optionIndex != null) form.append('option', q.options[optionIndex].id);
            if (remove) form.append('remove', '1');
            else form.append('image', file);
            return track(api('question/' + q.id + '/image/', {form: form}));
        }).then(function (data) {
            var s = data.question;
            q.image = s.image;
            q.problems = s.problems;
            q.options.forEach(function (o) {
                s.options.forEach(function (so) { if (so.id === o.id) o.image = so.image; });
            });
            if (q.id === currentId) renderForm();
            renderList();
            if (showPreview) loadPreview();
        }).catch(alertError);
    }

    function imageBlock(q) {
        var box = el('div', {'class': 'qe-field'}, [el('span', {'class': 'qe-label', text: q.type === 'pin' ? 'Картинка (обязательно)' : 'Картинка'})]);
        var row = el('div', {'class': 'qe-image-box'});
        if (q.image && q.type !== 'pin') row.appendChild(el('img', {src: q.image, alt: ''}));
        row.appendChild(el('button', {type: 'button', 'class': 'qe-btn qe-small', onclick: function () {
            pickFile('image/jpeg,image/png,image/gif,image/webp', function (f) { uploadImage(q, null, f); });
        }}, [icon('fa-picture-o'), q.image ? ' Заменить' : ' Загрузить']));
        if (q.image) {
            row.appendChild(el('button', {type: 'button', 'class': 'qe-btn qe-small qe-danger', onclick: function () {
                uploadImage(q, null, null, true);
            }}, [icon('fa-times'), ' Убрать']));
        }
        box.appendChild(row);
        box.appendChild(el('div', {'class': 'qe-hint', text: 'JPEG, PNG, GIF или WebP до 5 МБ. Картинка уменьшится до 1280 пикселей.'}));
        return box;
    }

    /* ---------------- answers by type ---------------- */

    function answerBlock(q) {
        var panel = el('div', {'class': 'qe-panel'});
        var t = q.type;
        if (t === 'code') {
            var seg = el('div', {'class': 'qe-seg'}, [
                el('button', {type: 'button', 'class': q.data.input ? '' : 'qe-on', text: 'Варианты ответа',
                    onclick: function () { if (q.data.input) { switchCodeMode(q, false); } }}),
                el('button', {type: 'button', 'class': q.data.input ? 'qe-on' : '', text: 'Ввод ответа',
                    onclick: function () { if (!q.data.input) { switchCodeMode(q, true); } }})
            ]);
            panel.appendChild(field('Как отвечают', seg));
            if (q.data.input) {
                panel.appendChild(answersEditor(q, 'Верный вывод программы'));
                return panel;
            }
        }
        if (hasOptions(q)) {
            panel.appendChild(optionsEditor(q));
            return panel;
        }
        if (t === 'word') {
            panel.appendChild(field('Слово', input(q, {maxLength: 24, 'data-field': 'word', style: 'text-transform:uppercase;font-weight:700;letter-spacing:.08em',
                placeholder: 'Например: АЛГОРИТМ'}, function () { return q.data.word || ''; }, function (v) { q.data.word = v; }),
                'Игроки получат буквы вперемешку. До 24 букв, регистр не важен.'));
            return panel;
        }
        if (t === 'text') {
            panel.appendChild(answersEditor(q, 'Допустимые ответы'));
            return panel;
        }
        if (t === 'slider') return sliderEditor(q, panel);
        if (t === 'pin') return pinEditor(q, panel);
        var notes = {
            cloud: 'Игроки пишут слово или короткую фразу (до 30 символов). Ответы складываются в облако слов. Очков нет.',
            open: 'Игроки пишут свободный ответ (до 300 символов). Ведущий показывает выбранные ответы на экране. Очков нет.'
        };
        panel.appendChild(el('p', {style: 'margin:0', text: notes[t] || ''}));
        return panel;
    }

    function switchCodeMode(q, typed) {
        if (typed) {
            q._stash = q.options.map(function (o) { return {text: o.text, is_correct: o.is_correct}; });
            q.options = [];
            q.data = {input: true, answers: q.data.answers || [], tolerance: q.data.tolerance || 0};
        } else {
            q.data = {input: false};
            q.options = (q._stash && q._stash.length ? q._stash : [{}, {}, {}, {}]).slice(0, 4).map(function (o) {
                return {id: null, text: o.text || '', is_correct: !!o.is_correct, image: ''};
            });
        }
        changed(q, true);
        renderForm();
    }

    function optionsEditor(q) {
        var t = q.type;
        var limits = OPTION_LIMITS[t];
        var box = el('div');
        var titles = {order: 'Пункты в верном порядке', poll: 'Варианты (без верного)', truefalse: 'Верный ответ'};
        var hints = {
            order: 'Запишите пункты сверху вниз в правильном порядке. Игроки получат их перемешанными.',
            single: 'Отметьте один верный вариант.', code: 'Отметьте один верный вариант.',
            multi: 'Отметьте все верные варианты. Очки — за долю верно отмеченных.',
            poll: 'Опрос без очков: игроки увидят, как распределились голоса.'
        };
        box.appendChild(el('div', {'class': 'qe-label', text: titles[t] || 'Варианты ответа'}));
        var list = el('div', {'class': 'qe-options', 'data-field': 'options'});
        q.options.forEach(function (o, i) {
            list.appendChild(optionRow(q, o, i));
        });
        box.appendChild(list);
        if (t !== 'truefalse') {
            box.appendChild(el('div', {'class': 'qe-row', style: 'margin-top:8px'}, [
                q.options.length < limits[1] ? el('button', {type: 'button', 'class': 'qe-btn qe-small', onclick: function () {
                    q.options.push({id: null, text: '', is_correct: false, image: ''});
                    changed(q);
                    renderForm();
                    var inputs = document.querySelectorAll('.qe-opt input[type=text]');
                    if (inputs.length) inputs[inputs.length - 1].focus();
                }}, [icon('fa-plus'), t === 'order' ? ' Пункт' : ' Вариант']) : null,
                el('span', {'class': 'qe-hint', style: 'margin:0', text: hints[t] + ' От ' + limits[0] + ' до ' + limits[1] + '.'})
            ]));
        }
        return box;
    }

    function optionRow(q, o, i) {
        var t = q.type;
        var row = el('div', {'class': 'qe-opt' + (o.is_correct && t !== 'poll' && t !== 'order' ? ' qe-right' : '')});
        if (t === 'order') row.appendChild(el('span', {'class': 'qe-mark qe-plain', text: String(i + 1)}));
        else row.appendChild(shapeMark(i));
        if (t === 'truefalse') {
            row.appendChild(el('span', {'class': 'qe-tf-label', text: o.text}));
        } else {
            row.appendChild(input(q, {maxLength: 300, placeholder: o.image ? 'Подпись (необязательно)' : (t === 'order' ? 'Пункт ' : 'Вариант ') + (i + 1),
                'aria-label': 'Вариант ' + (i + 1)}, function () { return o.text; }, function (v) { o.text = v; }));
            if (o.image) {
                row.appendChild(el('span', {'class': 'qe-opt-img'}, [
                    el('img', {src: o.image, alt: ''}),
                    el('button', {type: 'button', 'class': 'qe-x', title: 'Убрать картинку', html: '&times;',
                        onclick: function () { uploadImage(q, i, null, true); }})
                ]));
            } else {
                row.appendChild(el('button', {type: 'button', 'class': 'qe-btn qe-icon', title: 'Картинка к варианту',
                    'aria-label': 'Картинка к варианту', onclick: function () {
                        pickFile('image/jpeg,image/png,image/gif,image/webp', function (f) { uploadImage(q, i, f); });
                    }}, [icon('fa-picture-o')]));
            }
        }
        if (t !== 'order' && t !== 'poll') {
            row.appendChild(el('button', {type: 'button', 'class': 'qe-correct' + (o.is_correct ? ' qe-on' : ''),
                'aria-pressed': o.is_correct ? 'true' : 'false',
                onclick: function () {
                    if (t === 'multi') o.is_correct = !o.is_correct;
                    else q.options.forEach(function (x) { x.is_correct = x === o; });
                    changed(q);
                    renderForm();
                }}, [icon(o.is_correct ? 'fa-check' : 'fa-circle-thin'), ' верный']));
        }
        if (t === 'order') {
            row.appendChild(el('button', {type: 'button', 'class': 'qe-btn qe-icon', title: 'Выше', disabled: i === 0,
                onclick: function () { swapOptions(q, i, i - 1); }}, [icon('fa-chevron-up')]));
            row.appendChild(el('button', {type: 'button', 'class': 'qe-btn qe-icon', title: 'Ниже', disabled: i === q.options.length - 1,
                onclick: function () { swapOptions(q, i, i + 1); }}, [icon('fa-chevron-down')]));
        }
        if (t !== 'truefalse' && q.options.length > OPTION_LIMITS[t][0]) {
            row.appendChild(el('button', {type: 'button', 'class': 'qe-btn qe-icon qe-danger', title: 'Удалить вариант',
                'aria-label': 'Удалить вариант', onclick: function () {
                    q.options.splice(i, 1);
                    changed(q);
                    renderForm();
                }}, [icon('fa-trash-o')]));
        }
        return row;
    }

    function swapOptions(q, a, b) {
        var tmp = q.options[a];
        q.options[a] = q.options[b];
        q.options[b] = tmp;
        changed(q);
        renderForm();
    }

    function answersEditor(q, label) {
        var box = el('div');
        var chips = el('div', {'class': 'qe-chips', style: 'margin-bottom:8px'});
        function draw() {
            chips.innerHTML = '';
            (q.data.answers || []).forEach(function (a, i) {
                chips.appendChild(el('button', {type: 'button', 'class': 'qe-chip', title: 'Убрать', onclick: function () {
                    q.data.answers.splice(i, 1);
                    changed(q);
                    draw();
                }}, [a + ' ', el('span', {html: '&times;', 'aria-hidden': 'true'})]));
            });
            if (!(q.data.answers || []).length) chips.appendChild(el('span', {'class': 'qe-hint', style: 'margin:0', text: 'Пока нет ответов'}));
        }
        draw();
        var entry = el('input', {type: 'text', maxLength: 100, 'data-field': 'answers', placeholder: 'Ответ и Enter'});
        function add() {
            var v = entry.value.trim();
            if (!v) return;
            q.data.answers = q.data.answers || [];
            if (q.data.answers.indexOf(v) < 0 && q.data.answers.length < 20) q.data.answers.push(v);
            entry.value = '';
            changed(q);
            draw();
            entry.focus();
        }
        entry.addEventListener('keydown', function (e) { if (e.key === 'Enter') { e.preventDefault(); add(); } });
        box.appendChild(field(label, el('div', {}, [chips, el('div', {'class': 'qe-row'}, [
            el('div', {style: 'flex:1;min-width:160px'}, [entry]),
            el('button', {type: 'button', 'class': 'qe-btn', onclick: add}, [icon('fa-plus'), ' Добавить'])
        ])]), 'Регистр, «ё/е» и лишние пробелы не важны. Числа сравниваются как числа.'));
        box.appendChild(el('div', {style: 'max-width:220px'}, [numberInput(q, 'tolerance', 'Допуск для чисел', {min: 0})]));
        return box;
    }

    function sliderEditor(q, panel) {
        var grid = el('div', {'class': 'qe-grid2'}, [
            numberInput(q, 'min', 'Минимум'), numberInput(q, 'max', 'Максимум'),
            numberInput(q, 'step', 'Шаг', {min: 0}), numberInput(q, 'answer', 'Верный ответ'),
            numberInput(q, 'tolerance', 'Допуск (±)', {min: 0}),
            field('Единица', input(q, {maxLength: 12, placeholder: 'км, °C, %…', 'data-field': 'unit'},
                function () { return q.data.unit || ''; }, function (v) { q.data.unit = v; }))
        ]);
        panel.appendChild(grid);
        panel.appendChild(el('div', {id: 'qe-slider-view', 'class': 'qe-hint'}));
        renderSliderPreview(q);
        return panel;
    }

    function renderSliderPreview(q) {
        var view = $('#qe-slider-view');
        if (!view) return;
        var d = q.data;
        var ok = Number(d.min) < Number(d.max) && Number(d.step) > 0;
        view.textContent = ok ? 'Шкала от ' + d.min + ' до ' + d.max + ' с шагом ' + d.step + '. Полные очки за ' + d.answer +
            (d.tolerance ? ' ± ' + d.tolerance : '') + ' ' + (d.unit || '') + ', дальше — меньше.' : 'Минимум должен быть меньше максимума, шаг больше 0.';
    }

    function pinEditor(q, panel) {
        if (!q.image) {
            panel.appendChild(el('p', {style: 'margin:0', text: 'Загрузите картинку выше, затем нажмите на неё, чтобы отметить верное место.'}));
            return panel;
        }
        var area = el('div', {'class': 'qe-pin-area'});
        var dot = el('div', {'class': 'qe-pin-dot'});
        var img = el('img', {src: q.image, alt: '', draggable: 'false'});
        var wrap = el('div', {'class': 'qe-pin'}, [img, area, dot]);
        function draw() {
            var d = q.data;
            area.style.left = dot.style.left = d.x + '%';
            area.style.top = dot.style.top = d.y + '%';
            area.style.width = (2 * d.r) + '%';
            area.style.height = (2 * d.r) + '%';
        }
        function place(e) {
            var rect = img.getBoundingClientRect();
            var p = e.touches ? e.touches[0] : e;
            q.data.x = Math.round(Math.min(Math.max((p.clientX - rect.left) / rect.width * 100, 0), 100) * 10) / 10;
            q.data.y = Math.round(Math.min(Math.max((p.clientY - rect.top) / rect.height * 100, 0), 100) * 10) / 10;
            draw();
            changed(q);
        }
        wrap.addEventListener('click', place);
        draw();
        var label = el('span', {text: q.data.r + '%'});
        var range = el('input', {type: 'range', 'class': 'qe-range', min: 1, max: 50, step: 1, value: q.data.r, 'data-field': 'r',
            oninput: function (e) { q.data.r = Number(e.target.value); label.textContent = q.data.r + '%'; draw(); changed(q); }});
        panel.appendChild(field('Верное место', wrap, 'Нажмите на картинку, чтобы перенести точку. Ответ засчитывается внутри зелёной области.'));
        panel.appendChild(field('Размер области', el('div', {'class': 'qe-row'}, [range, label])));
        return panel;
    }

    /* ---------------- preview ---------------- */

    function togglePreview() {
        showPreview = !showPreview;
        $('#qe-main').classList.toggle('qe-with-preview', showPreview);
        $('#qe-preview').hidden = !showPreview;
        renderForm();
        if (showPreview) loadPreview();
    }

    var previewSeq = 0;

    function loadPreview() {
        var q = byId(currentId);
        var screen = $('#qe-phone');
        if (!q) { screen.innerHTML = ''; return; }
        var seq = ++previewSeq;
        flush(q).then(function () {
            return api('question/' + q.id + '/preview/');
        }).then(function (data) {
            if (seq === previewSeq) renderPhone(data.question, data.theme);
        }).catch(function (e) {
            if (seq === previewSeq) screen.innerHTML = '<div class="qe-ph-scroll"><div class="qe-ph-card">' + esc(e.message) + '</div></div>';
        });
    }

    function renderPhone(p, theme) {
        var phone = $('#qe-phone');
        phone.className = 'qe-phone qz-theme-' + theme;
        var h = '<div class="qe-ph-scroll"><div class="qe-ph-top"><span>' + (p.i + 1) + ' / ' + p.n + ' · ' + esc(p.type_name) +
            '</span><span><i class="fa fa-clock-o"></i> ' + p.time + ' с' + (p.weight === 2 ? ' · x2' : '') + '</span></div>';
        if (p.text) h += '<div class="qe-ph-card">' + p.text + '</div>';
        if (p.code) h += '<pre class="qe-ph-code">' + esc(p.code) + '</pre>';
        if (p.image && p.type !== 'pin') h += '<img class="qe-ph-img" src="' + esc(p.image) + '" alt="">';
        var t = p.type;
        if (p.letters) {
            h += '<div class="qe-ph-letters">' + p.letters.map(function (l) { return '<span>' + esc(l) + '</span>'; }).join('') + '</div>';
            h += '<div class="qe-ph-btn">Ответить</div>';
        } else if (p.input) {
            h += '<div class="qe-ph-input">' + (t === 'open' ? 'Ваш ответ…' : t === 'cloud' ? 'Слово…' : 'Ответ…') + '</div><div class="qe-ph-btn">Ответить</div>';
        } else if (p.slider) {
            var mid = p.slider.min + Math.round((p.slider.max - p.slider.min) / 2 / p.slider.step) * p.slider.step;
            h += '<div class="qe-ph-card qe-ph-slider">' + esc(mid) + ' ' + esc(p.slider.unit) +
                '<input type="range" disabled min="' + esc(p.slider.min) + '" max="' + esc(p.slider.max) + '" value="' + esc(mid) + '">' +
                '<div class="qe-ph-note">' + esc(p.slider.min) + ' … ' + esc(p.slider.max) + '</div></div><div class="qe-ph-btn">Ответить</div>';
        } else if (t === 'pin') {
            h += p.image ? '<img class="qe-ph-img" style="max-height:260px" src="' + esc(p.image) + '" alt="">' : '';
            h += '<div class="qe-ph-note">Нажмите на картинку</div>';
        } else if (t === 'order') {
            h += '<div class="qe-ph-opts qe-one-col">' + p.options.map(function (o) {
                return '<div class="qe-ph-opt qe-ph-row"><i class="fa fa-bars"></i> ' + optionInner(o) + '</div>';
            }).join('') + '</div><div class="qe-ph-btn">Готово</div>';
        } else {
            var oneCol = t === 'truefalse' ? '' : p.options.some(function (o) { return (o.text || '').length > 28; }) ? ' qe-one-col' : '';
            h += '<div class="qe-ph-opts' + oneCol + '">' + p.options.map(function (o, i) {
                var shape = window.QuizFx && QuizFx.shape ? QuizFx.shape(i) : '';
                return '<div class="qe-ph-opt qz-c' + (i % 6) + '">' + shape + optionInner(o) +
                    (t === 'multi' ? '<span class="qe-check"></span>' : '') + '</div>';
            }).join('') + '</div>';
            if (t === 'multi') h += '<div class="qe-ph-btn">Ответить</div>';
        }
        h += '</div>';
        phone.innerHTML = h;
    }

    function optionInner(o) {
        return (o.image ? '<img src="' + esc(o.image) + '" alt="">' : '') + '<span>' + esc(o.text) + '</span>';
    }

    /* ---------------- quiz settings, cover, import ---------------- */

    var settingsTimer = null;

    function saveSettings(now) {
        clearTimeout(settingsTimer);
        settingsTimer = setTimeout(function () {
            settingsTimer = null;
            var body = {
                title: $('#qe-title').value, description: $('#qe-description').value, subject: $('#qe-subject').value,
                theme: quiz.theme, access: quiz.access
            };
            track(api('settings/', {json: body})).then(function (data) {
                quiz = data.quiz;
            }).catch(function () {});
        }, now ? 0 : SAVE_DELAY);
    }

    function initSettings() {
        $('#qe-title').addEventListener('input', function () { saveSettings(); });
        $('#qe-description').addEventListener('input', function () { saveSettings(); });
        $('#qe-subject').addEventListener('input', function () { saveSettings(); });
        Array.prototype.forEach.call(document.querySelectorAll('.qe-theme'), function (b) {
            b.addEventListener('click', function () {
                quiz.theme = b.getAttribute('data-theme');
                markSettings();
                saveSettings(true);
                if (showPreview) loadPreview();
            });
        });
        Array.prototype.forEach.call(document.querySelectorAll('[data-access]'), function (b) {
            b.addEventListener('click', function () {
                quiz.access = b.getAttribute('data-access');
                markSettings();
                saveSettings(true);
            });
        });
        $('#qe-cover-upload').addEventListener('click', function () {
            pickFile('image/jpeg,image/png,image/gif,image/webp', function (f) {
                var form = new FormData();
                form.append('image', f);
                track(api('cover/', {form: form})).then(function (data) { quiz = data.quiz; markSettings(); }).catch(alertError);
            });
        });
        $('#qe-cover-remove').addEventListener('click', function () {
            var form = new FormData();
            form.append('remove', '1');
            track(api('cover/', {form: form})).then(function (data) { quiz = data.quiz; markSettings(); }).catch(alertError);
        });
        $('#qe-settings-btn').addEventListener('click', function () {
            var panel = $('#qe-settings');
            panel.hidden = !panel.hidden;
            this.classList.toggle('qe-on', !panel.hidden);
        });
        $('#qe-delete-form').addEventListener('submit', function (e) {
            if (!window.confirm('Удалить викторину «' + quiz.title + '» со всеми вопросами? Это нельзя отменить.')) e.preventDefault();
        });
        markSettings();
    }

    function markSettings() {
        Array.prototype.forEach.call(document.querySelectorAll('.qe-theme'), function (b) {
            b.classList.toggle('qe-on', b.getAttribute('data-theme') === quiz.theme);
        });
        Array.prototype.forEach.call(document.querySelectorAll('[data-access]'), function (b) {
            b.classList.toggle('qe-on', b.getAttribute('data-access') === quiz.access);
        });
        var img = $('#qe-cover-img');
        img.hidden = !quiz.cover;
        if (quiz.cover) img.src = quiz.cover;
        $('#qe-cover-remove').hidden = !quiz.cover;
        $('#qe-cover-upload').lastChild.textContent = quiz.cover ? ' Заменить' : ' Загрузить';
    }

    function initImport() {
        $('#qe-import-btn').addEventListener('click', function () {
            var panel = $('#qe-import');
            panel.hidden = !panel.hidden;
            this.classList.toggle('qe-on', !panel.hidden);
        });
        $('#qe-import-file').addEventListener('click', function () {
            pickFile('.xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', function (f) {
                var result = $('#qe-import-result');
                result.textContent = 'Загружаю…';
                var form = new FormData();
                form.append('file', f);
                flushAll().catch(function () {}).then(function () {
                    return track(api('import/', {form: form}));
                }).then(function (data) {
                    questions = data.questions;
                    var before = currentId;
                    if (!byId(before) && questions.length) currentId = questions[0].id;
                    renderList();
                    renderForm();
                    result.innerHTML = '';
                    result.appendChild(el('b', {text: 'Добавлено вопросов: ' + data.added}));
                    if (data.errors.length) {
                        result.appendChild(el('ul', {}, data.errors.map(function (e) {
                            return el('li', {text: 'Строка ' + e.row + ': ' + e.error});
                        })));
                    }
                }).catch(function (e) {
                    result.innerHTML = '';
                    result.appendChild(el('span', {style: 'color:var(--qe-bad);font-weight:600', text: e.message}));
                });
            });
        });
    }

    function initPicker() {
        var grid = $('#qe-types');
        C.types.forEach(function (t) {
            grid.appendChild(el('button', {type: 'button', 'class': 'qe-type', onclick: function () { addQuestion(t.code); }}, [
                icon(t.icon), el('span', {}, [el('b', {text: t.name}), el('small', {text: t.hint})])
            ]));
        });
        $('#qe-add').addEventListener('click', openPicker);
        $('#qe-picker-close').addEventListener('click', closePicker);
        $('#qe-picker').addEventListener('click', function (e) { if (e.target === this) closePicker(); });
        $('#qe-preview-close').addEventListener('click', togglePreview);
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                if (!$('#qe-picker').hidden) closePicker();
                else if (showPreview && window.innerWidth <= 1100) togglePreview();
            }
        });
    }

    function start() {
        initSettings();
        initImport();
        initPicker();
        renderList();
        renderForm();
        $('#qe-status').textContent = '';
    }

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
    else start();
})();
