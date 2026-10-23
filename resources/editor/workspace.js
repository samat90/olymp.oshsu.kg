/* Sandbox: personal files and folders with the online editor. */
document.addEventListener('DOMContentLoaded', function () {
    'use strict';

    var W = window.OLYMP_WORKSPACE;
    var E = window.OlympEditor;
    var cfg = window.OLYMP_EDITOR;
    var $ = function (sel) { return document.querySelector(sel); };
    var api = W.api;   // .../api/files/

    var files = {};          // id -> file
    var open = null;         // current file id
    var editor = null;
    var models = {};         // id -> monaco model
    var expanded = loadExpanded();
    var saveTimer = null;
    var dirty = false;
    var runner = W.runnerEnabled ? new E.Runner({}) : null;
    var busy = false;

    var langByKey = {};
    W.languages.forEach(function (l) { langByKey[l.key] = l; });

    function storageGet(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
    function storageSet(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* ignore */ } }
    function loadExpanded() {
        try { return JSON.parse(storageGet('ws-expanded') || '{}') || {}; } catch (e) { return {}; }
    }
    function saveExpanded() { storageSet('ws-expanded', JSON.stringify(expanded)); }

    function request(url, body) {
        var opts = {credentials: 'same-origin', headers: {'X-CSRFToken': cfg.csrf}};
        if (body !== undefined) {
            opts.method = 'POST';
            opts.headers['Content-Type'] = 'application/json';
            opts.body = JSON.stringify(body);
        }
        return fetch(url, opts).then(function (r) {
            return r.json().catch(function () { return {ok: false, error: 'Ошибка сервера (' + r.status + ')'}; });
        }).then(function (data) {
            if (!data.ok) throw new Error(data.error || 'Ошибка');
            return data;
        });
    }

    function setStatus(text) { $('#ws-status').textContent = text || ''; }
    function fail(err) { setStatus(''); alert(err.message || err); }

    /* ---- tree ---- */

    function children(parentId) {
        return Object.keys(files).map(function (id) { return files[id]; }).filter(function (f) {
            return (f.parent || null) === (parentId || null);
        }).sort(function (a, b) {
            if (a.folder !== b.folder) return a.folder ? -1 : 1;
            return a.name.localeCompare(b.name, 'ru', {numeric: true});
        });
    }

    function icon(file) {
        if (file.folder) return expanded[file.id] ? 'fa-folder-open-o' : 'fa-folder-o';
        return 'fa-file-code-o';
    }

    function render() {
        var tree = $('#ws-tree');
        tree.innerHTML = '';
        var count = Object.keys(files).length;
        if (!count) {
            tree.innerHTML = '<div class="ws-empty">Пока нет файлов. Создайте первый файл кнопкой сверху.</div>';
        }
        (function walk(parentId, depth) {
            children(parentId).forEach(function (f) {
                var row = document.createElement('div');
                row.className = 'ws-item' + (f.id === open ? ' ws-current' : '');
                row.style.paddingLeft = (8 + depth * 14) + 'px';
                row.dataset.id = f.id;
                row.draggable = true;
                row.setAttribute('role', 'treeitem');
                row.innerHTML = '<i class="fa ' + icon(f) + '"></i><span class="ws-name"></span>';
                row.querySelector('.ws-name').textContent = f.name;
                tree.appendChild(row);
                if (f.folder && expanded[f.id]) walk(f.id, depth + 1);
            });
        })(null, 0);
        $('#ws-foot').textContent = 'Файлов: ' + count + ' из ' + W.maxFiles;
    }

    var tree = $('#ws-tree');
    tree.addEventListener('click', function (e) {
        var row = e.target.closest('.ws-item');
        if (!row || row.querySelector('input')) return;
        var f = files[row.dataset.id];
        if (f.folder) {
            expanded[f.id] = !expanded[f.id];
            saveExpanded();
            render();
        } else {
            openFile(f.id);
        }
    });
    tree.addEventListener('dblclick', function (e) {
        var row = e.target.closest('.ws-item');
        if (row) startRename(files[row.dataset.id]);
    });
    tree.addEventListener('contextmenu', function (e) {
        var row = e.target.closest('.ws-item');
        e.preventDefault();
        showMenu(e.clientX, e.clientY, row ? files[row.dataset.id] : null);
    });

    /* drag and drop into folders */
    var dragged = null;
    tree.addEventListener('dragstart', function (e) {
        var row = e.target.closest('.ws-item');
        dragged = row ? files[row.dataset.id] : null;
        if (e.dataTransfer) e.dataTransfer.effectAllowed = 'move';
    });
    tree.addEventListener('dragover', function (e) {
        if (!dragged) return;
        e.preventDefault();
        tree.querySelectorAll('.ws-drop').forEach(function (r) { r.classList.remove('ws-drop'); });
        var row = e.target.closest('.ws-item');
        if (row && files[row.dataset.id].folder) row.classList.add('ws-drop');
    });
    tree.addEventListener('drop', function (e) {
        e.preventDefault();
        tree.querySelectorAll('.ws-drop').forEach(function (r) { r.classList.remove('ws-drop'); });
        if (!dragged) return;
        var row = e.target.closest('.ws-item');
        var target = row ? files[row.dataset.id] : null;
        var parent = target ? (target.folder ? target.id : target.parent) : null;
        var item = dragged;
        dragged = null;
        if ((item.parent || null) === (parent || null) || item.id === parent) return;
        request(api + item.id + '/move/', {parent: parent}).then(function (data) {
            files[item.id] = data.file;
            if (parent) expanded[parent] = true;
            render();
        }).catch(fail);
    });

    /* context menu */
    function closeMenu() {
        var m = document.querySelector('.ws-menu');
        if (m) m.remove();
    }
    document.addEventListener('click', closeMenu);
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeMenu(); });

    function showMenu(x, y, file) {
        closeMenu();
        var menu = document.createElement('div');
        menu.className = 'ws-menu';
        var items = [];
        var folderId = file ? (file.folder ? file.id : file.parent) : null;
        items.push(['Новый файл', function () { startCreate(folderId, false); }]);
        items.push(['Новая папка', function () { startCreate(folderId, true); }]);
        if (file) {
            items.push(['Переименовать', function () { startRename(file); }]);
            if (file.parent) items.push(['Переместить в корень', function () {
                request(api + file.id + '/move/', {parent: null}).then(function (d) { files[file.id] = d.file; render(); }).catch(fail);
            }]);
            items.push(['Удалить', function () { remove(file); }, 'ws-danger']);
        }
        items.forEach(function (it) {
            var b = document.createElement('button');
            b.type = 'button';
            b.textContent = it[0];
            if (it[2]) b.className = it[2];
            b.addEventListener('click', function (e) { e.stopPropagation(); closeMenu(); it[1](); });
            menu.appendChild(b);
        });
        document.body.appendChild(menu);
        var rect = menu.getBoundingClientRect();
        menu.style.left = Math.min(x, window.innerWidth - rect.width - 8) + 'px';
        menu.style.top = Math.min(y, window.innerHeight - rect.height - 8) + 'px';
    }

    /* inline name input */
    function nameInput(row, value, onDone) {
        var span = row.querySelector('.ws-name');
        var input = document.createElement('input');
        input.value = value;
        input.style.cssText = 'flex:1;min-width:0;font:inherit;padding:1px 4px;border:1px solid var(--oe-primary);' +
            'border-radius:4px;background:var(--oe-bg);color:var(--oe-text)';
        span.replaceWith(input);
        input.focus();
        var dot = value.lastIndexOf('.');
        input.setSelectionRange(0, dot > 0 ? dot : value.length);
        var finished = false;
        function finish(ok) {
            if (finished) return;
            finished = true;
            onDone(ok ? input.value.trim() : null);
        }
        input.addEventListener('keydown', function (e) {
            if (e.key === 'Enter') { e.preventDefault(); finish(true); }
            if (e.key === 'Escape') { e.preventDefault(); finish(false); }
            e.stopPropagation();
        });
        input.addEventListener('blur', function () { finish(true); });
        input.addEventListener('click', function (e) { e.stopPropagation(); });
    }

    function defaultName(folder) {
        if (folder) return 'Новая папка';
        var lang = langByKey[storageGet('ws-last-lang')] || langByKey.CPP17 || W.languages[0];
        return 'main.' + (lang ? lang.ext : 'txt');
    }

    function startCreate(parentId, folder) {
        if (parentId) { expanded[parentId] = true; saveExpanded(); }
        render();
        var row = document.createElement('div');
        row.className = 'ws-item';
        var depth = 0;
        for (var p = parentId; p; p = files[p] && files[p].parent) depth++;
        row.style.paddingLeft = (8 + depth * 14) + 'px';
        row.innerHTML = '<i class="fa ' + (folder ? 'fa-folder-o' : 'fa-file-code-o') + '"></i><span class="ws-name"></span>';
        var anchor = parentId ? tree.querySelector('.ws-item[data-id="' + parentId + '"]') : null;
        if (anchor) anchor.after(row); else tree.prepend(row);
        var empty = tree.querySelector('.ws-empty');
        if (empty) empty.remove();
        nameInput(row, defaultName(folder), function (name) {
            if (!name) { render(); return; }
            request(api + 'new/', {parent: parentId, name: name, folder: folder}).then(function (data) {
                files[data.file.id] = data.file;
                render();
                if (!folder) openFile(data.file.id, data.file);
            }).catch(function (err) { render(); fail(err); });
        });
    }

    function startRename(file) {
        var row = tree.querySelector('.ws-item[data-id="' + file.id + '"]');
        if (!row) return;
        nameInput(row, file.name, function (name) {
            if (!name || name === file.name) { render(); return; }
            request(api + file.id + '/rename/', {name: name}).then(function (data) {
                files[file.id] = data.file;
                render();
                if (open === file.id) showFileInfo(data.file);
            }).catch(function (err) { render(); fail(err); });
        });
    }

    function remove(file) {
        var what = file.folder ? 'папку «' + file.name + '» со всем содержимым' : 'файл «' + file.name + '»';
        if (!confirm('Удалить ' + what + '? Это нельзя отменить.')) return;
        request(api + file.id + '/delete/', {}).then(function () {
            var gone = {};
            (function mark(id) {
                gone[id] = true;
                children(id).forEach(function (c) { mark(c.id); });
            })(file.id);
            Object.keys(gone).forEach(function (id) {
                delete files[id];
                if (models[id]) { models[id].dispose(); delete models[id]; }
            });
            if (open && gone[open]) closeFile();
            render();
        }).catch(fail);
    }

    $('#ws-new-file').addEventListener('click', function () { startCreate(currentFolder(), false); });
    $('#ws-new-folder').addEventListener('click', function () { startCreate(currentFolder(), true); });
    $('#ws-welcome-file').addEventListener('click', function () { startCreate(null, false); });

    function currentFolder() {
        return open && files[open] ? files[open].parent : null;
    }

    /* ---- editor ---- */

    var langSelect = $('#ws-language');
    W.languages.forEach(function (l) {
        var o = document.createElement('option');
        o.value = l.key;
        o.textContent = l.name;
        langSelect.appendChild(o);
    });

    function showFileInfo(file) {
        $('#ws-filename').textContent = file.name;
        $('#ws-filename').title = file.name;
        langSelect.value = file.language || '';
        $('#ws-share').innerHTML = '<i class="fa fa-link"></i> ' + (file.shared ? 'Ссылка' : 'Поделиться');
    }

    function ensureEditor() {
        if (editor) return Promise.resolve(editor);
        var holder = $('#ws-editor');
        holder.innerHTML = '';
        return E.create(holder, {
            value: '',
            onRun: run,
            onSave: function () { flush(); }
        }).then(function (ed) {
            editor = ed;
            ed.editor.onDidChangeModelContent(function () {
                if (!open) return;
                dirty = true;
                setStatus('Изменено');
                clearTimeout(saveTimer);
                saveTimer = setTimeout(flush, 900);
            });
            return ed;
        });
    }

    function flush() {
        clearTimeout(saveTimer);
        if (!open || !dirty || !editor) return Promise.resolve();
        var id = open;
        var content = models[id].getValue();
        dirty = false;
        setStatus('Сохранение…');
        return request(api + id + '/save/', {content: content}).then(function () {
            if (files[id]) files[id].content = content;
            setStatus('Сохранено');
        }).catch(function (err) {
            dirty = true;
            setStatus('Не сохранено: ' + err.message);
        });
    }

    function openFile(id, preloaded) {
        if (open === id) return;
        flush();
        var load = preloaded && 'content' in preloaded ? Promise.resolve({file: preloaded}) : request(api + id + '/');
        Promise.all([load, ensureEditor()]).then(function (res) {
            var file = res[0].file;
            files[id] = Object.assign(files[id] || {}, file);
            var monaco = window.monaco;
            if (!models[id]) {
                var lang = langByKey[file.language];
                models[id] = monaco.editor.createModel(file.content || '', E.monacoLanguage(lang ? lang.ace : 'text'));
            }
            open = id;
            dirty = false;
            editor.editor.setModel(models[id]);
            editor.focus();
            $('#ws-stdin').value = file.stdin || '';
            $('#ws-stdin').disabled = false;
            langSelect.disabled = false;
            $('#ws-share').disabled = false;
            var runBtn = $('#ws-run');
            if (runBtn) runBtn.disabled = false;
            showFileInfo(file);
            storageSet('ws-open', id);
            render();
            setStatus('');
        }).catch(fail);
    }

    function closeFile() {
        open = null;
        if (editor) editor.editor.setModel(null);
        $('#ws-filename').textContent = 'Песочница';
        $('#ws-stdin').value = '';
        $('#ws-stdin').disabled = true;
        langSelect.disabled = true;
        $('#ws-share').disabled = true;
        var runBtn = $('#ws-run');
        if (runBtn) runBtn.disabled = true;
    }

    langSelect.addEventListener('change', function () {
        if (!open) return;
        var id = open;
        var lang = langByKey[langSelect.value];
        storageSet('ws-last-lang', langSelect.value);
        if (models[id] && lang) window.monaco.editor.setModelLanguage(models[id], E.monacoLanguage(lang.ace));
        request(api + id + '/save/', {language: langSelect.value}).then(function (d) {
            files[id].language = d.file.language;
        }).catch(fail);
    });

    var stdinTimer = null;
    $('#ws-stdin').addEventListener('input', function () {
        if (!open) return;
        var id = open;
        var value = $('#ws-stdin').value;
        clearTimeout(stdinTimer);
        stdinTimer = setTimeout(function () {
            request(api + id + '/save/', {stdin: value}).then(function () { files[id].stdin = value; }).catch(fail);
        }, 900);
    });
    $('#ws-stdin').addEventListener('keydown', function (e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') { e.preventDefault(); run(); }
    });

    $('#ws-settings').addEventListener('click', E.openSettings);

    $('#ws-share').addEventListener('click', function () {
        if (!open) return;
        var file = files[open];
        var share = function (f) {
            var link = W.shareBase + f.share_key + '/';
            var msg = 'Ссылка только для чтения. Любой, у кого она есть, увидит этот файл.\n\n' + link +
                '\n\nНажмите «Отмена», чтобы закрыть доступ по ссылке.';
            if (navigator.clipboard) navigator.clipboard.writeText(link).catch(function () {});
            if (!confirm(msg)) {
                request(api + f.id + '/share/', {on: false}).then(function (d) {
                    files[f.id] = Object.assign(files[f.id], d.file);
                    showFileInfo(files[f.id]);
                }).catch(fail);
            }
        };
        request(api + file.id + '/share/', {on: true}).then(function (d) {
            files[file.id] = Object.assign(files[file.id], d.file);
            showFileInfo(files[file.id]);
            share(d.file);
        }).catch(fail);
    });

    /* ---- run ---- */

    function showPane(name) {
        document.querySelectorAll('.oe-tab').forEach(function (t) { t.classList.toggle('oe-active', t.dataset.pane === name); });
        document.querySelectorAll('.oe-pane').forEach(function (p) { p.classList.toggle('oe-active', p.dataset.pane === name); });
    }
    document.querySelectorAll('.oe-tab').forEach(function (t) {
        t.addEventListener('click', function () { showPane(t.dataset.pane); });
    });

    function run() {
        if (!runner || busy || !open || !editor) return;
        var file = files[open];
        if (!file.language) { alert('Выберите язык программирования для этого файла.'); return; }
        flush();
        busy = true;
        $('#ws-run').disabled = true;
        showPane('result');
        var out = $('#ws-result');
        out.innerHTML = '<div class="oe-placeholder">' + E.T.running + '</div>';
        runner.run(file.language, models[open].getValue(), $('#ws-stdin').value).then(function (result) {
            out.innerHTML = E.renderResult(result);
        }).catch(function (err) {
            out.innerHTML = E.renderResult({status: 'error', message: err.message});
        }).then(function () {
            busy = false;
            $('#ws-run').disabled = false;
        });
    }
    if ($('#ws-run')) $('#ws-run').addEventListener('click', run);

    window.addEventListener('beforeunload', function (e) {
        if (dirty) { flush(); e.preventDefault(); e.returnValue = ''; }
    });

    /* ---- panel resize ---- */
    var panel = $('#ws-panel');
    var h = storageGet('ws-panel-h');
    if (h) panel.style.flexBasis = h + 'px';
    $('#ws-hsplit').addEventListener('mousedown', function (e) {
        e.preventDefault();
        var handle = e.target;
        handle.classList.add('oe-dragging');
        function move(ev) {
            var work = panel.parentNode.getBoundingClientRect();
            var height = Math.min(Math.max(work.bottom - ev.clientY, 90), work.height - 160);
            panel.style.flexBasis = height + 'px';
            storageSet('ws-panel-h', Math.round(height));
        }
        function up() {
            handle.classList.remove('oe-dragging');
            document.removeEventListener('mousemove', move);
            document.removeEventListener('mouseup', up);
        }
        document.addEventListener('mousemove', move);
        document.addEventListener('mouseup', up);
    });

    /* ---- start ---- */
    request(api).then(function (data) {
        data.files.forEach(function (f) { files[f.id] = f; });
        render();
        var last = storageGet('ws-open');
        if (last && files[last] && !files[last].folder) openFile(Number(last));
    }).catch(fail);
});
