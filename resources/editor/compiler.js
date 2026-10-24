/* The Compiler section: files and folders, tabs, Monaco, and a console. */
document.addEventListener('DOMContentLoaded', function () {
    'use strict';

    var W = window.OLYMP_WORKSPACE;
    var E = window.OlympEditor;
    var S = E.T;
    var cfg = window.OLYMP_EDITOR;
    var $ = function (sel) { return document.querySelector(sel); };
    var api = W.api;   // .../api/files/

    var HELLO = {
        C: '#include <stdio.h>\n\nint main() {\n    printf("Hello, World!\\n");\n    return 0;\n}\n',
        CPP17: '#include <iostream>\nusing namespace std;\n\nint main() {\n    cout << "Hello, World!" << endl;\n    return 0;\n}\n',
        CPP20: '#include <iostream>\nusing namespace std;\n\nint main() {\n    cout << "Hello, World!" << endl;\n    return 0;\n}\n',
        PY3: 'print("Hello, World!")\n',
        JAVA8: 'public class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello, World!");\n    }\n}\n',
        JAVA: 'public class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello, World!");\n    }\n}\n',
        CSHARP: 'using System;\n\nclass Program {\n    static void Main() {\n        Console.WriteLine("Hello, World!");\n    }\n}\n',
        MONOCS: 'using System;\n\nclass Program {\n    static void Main() {\n        Console.WriteLine("Hello, World!");\n    }\n}\n',
        NODEJS: 'console.log("Hello, World!");\n',
        GO: 'package main\n\nimport "fmt"\n\nfunc main() {\n\tfmt.Println("Hello, World!")\n}\n',
        KOTLIN: 'fun main() {\n    println("Hello, World!")\n}\n',
        PAS: 'program Hello;\nbegin\n  writeln(\'Hello, World!\');\nend.\n'
    };
    var MAIN_NAME = {JAVA8: 'Main.java', JAVA: 'Main.java'};

    var files = {};          // id -> file
    var models = {};         // id -> monaco model
    var tabs = [];           // open file ids, in order
    var active = null;
    var editor = null;
    var expanded = loadJSON('ws-expanded', {});
    var saveTimers = {};
    var dirty = {};
    var runner = W.runnerEnabled ? new E.Runner({}) : null;
    var langByKey = {};
    W.languages.forEach(function (l) { langByKey[l.key] = l; });

    function storageGet(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
    function storageSet(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* ignore */ } }
    function loadJSON(k, d) { try { return JSON.parse(storageGet(k) || 'null') || d; } catch (e) { return d; } }

    function request(url, body) {
        var opts = {credentials: 'same-origin', headers: {'X-CSRFToken': cfg.csrf}};
        if (body !== undefined) {
            opts.method = 'POST';
            opts.headers['Content-Type'] = 'application/json';
            opts.body = JSON.stringify(body);
        }
        return fetch(url, opts).then(function (r) {
            return r.json().catch(function () { return {ok: false, error: S.serverError + ' (' + r.status + ')'}; });
        }).then(function (data) {
            if (!data.ok) throw new Error(data.error || S.error);
            return data;
        });
    }

    var statusTimer = null;
    function setStatus(text, sticky) {
        $('#cc-status').textContent = text || '';
        clearTimeout(statusTimer);
        if (text && !sticky) statusTimer = setTimeout(function () { $('#cc-status').textContent = ''; }, 3000);
    }
    function fail(err) { setStatus(''); alert(err.message || err); }

    /* ======================= file tree ======================= */

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

    var tree = $('#ws-tree');

    function render() {
        tree.innerHTML = '';
        var count = Object.keys(files).length;
        if (!count) tree.innerHTML = '<div class="ws-empty">' + E.escape(S.noFiles) + '</div>';
        (function walk(parentId, depth) {
            children(parentId).forEach(function (f) {
                var row = document.createElement('div');
                row.className = 'ws-item' + (f.id === active ? ' ws-current' : '');
                row.style.paddingLeft = (12 + depth * 14) + 'px';
                row.dataset.id = f.id;
                row.draggable = true;
                row.setAttribute('role', 'treeitem');
                row.innerHTML = '<i class="fa ' + icon(f) + '"></i><span class="ws-name"></span>' +
                    '<button type="button" class="ws-del"><i class="fa fa-trash-o"></i></button>';
                row.querySelector('.ws-name').textContent = f.name;
                row.querySelector('.ws-del').title = S.delete;
                tree.appendChild(row);
                if (f.folder && expanded[f.id]) walk(f.id, depth + 1);
            });
        })(null, 0);
        $('#ws-foot').textContent = S.files + ': ' + count + ' / ' + W.maxFiles;
        renderTabs();
    }

    tree.addEventListener('click', function (e) {
        var row = e.target.closest('.ws-item');
        if (!row || row.querySelector('input')) return;
        var f = files[row.dataset.id];
        if (e.target.closest('.ws-del')) { e.stopPropagation(); remove(f); return; }
        if (f.folder) {
            expanded[f.id] = !expanded[f.id];
            storageSet('ws-expanded', JSON.stringify(expanded));
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

    var dragged = null;
    tree.addEventListener('dragstart', function (e) {
        var row = e.target.closest('.ws-item');
        dragged = row ? files[row.dataset.id] : null;
    });
    tree.addEventListener('dragover', function (e) {
        e.preventDefault();
        tree.querySelectorAll('.ws-drop').forEach(function (r) { r.classList.remove('ws-drop'); });
        var row = e.target.closest('.ws-item');
        if (row && files[row.dataset.id].folder) row.classList.add('ws-drop');
    });
    tree.addEventListener('drop', function (e) {
        e.preventDefault();
        tree.querySelectorAll('.ws-drop').forEach(function (r) { r.classList.remove('ws-drop'); });
        var row = e.target.closest('.ws-item');
        var target = row ? files[row.dataset.id] : null;
        var parent = target ? (target.folder ? target.id : target.parent) : null;
        if (e.dataTransfer && e.dataTransfer.files && e.dataTransfer.files.length && !dragged) {
            upload(e.dataTransfer.files, parent);
            return;
        }
        var item = dragged;
        dragged = null;
        if (!item || (item.parent || null) === (parent || null) || item.id === parent) return;
        request(api + item.id + '/move/', {parent: parent}).then(function (data) {
            files[item.id] = Object.assign(files[item.id], data.file);
            if (parent) expanded[parent] = true;
            render();
        }).catch(fail);
    });

    function closeMenu() {
        document.querySelectorAll('.ws-menu').forEach(function (m) { m.remove(); });
    }
    document.addEventListener('click', closeMenu);

    function popup(x, y, items) {
        closeMenu();
        var menu = document.createElement('div');
        menu.className = 'ws-menu';
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

    function showMenu(x, y, file) {
        var folderId = file ? (file.folder ? file.id : file.parent) : null;
        var items = [
            [S.newFile, function () { startCreate(folderId, false); }],
            [S.newFolder, function () { startCreate(folderId, true); }],
            [S.uploadHere, function () { uploadTarget = folderId; $('#ws-upload-input').click(); }]
        ];
        if (file) {
            items.push([S.rename, function () { startRename(file); }]);
            if (file.folder) {
                items.push([S.downloadZip, function () { location.href = W.downloadUrl + '?folder=' + file.id; }]);
            } else {
                items.push([S.download, function () { downloadFile(file.id); }]);
            }
            if (file.parent) items.push([S.moveToRoot, function () {
                request(api + file.id + '/move/', {parent: null}).then(function (d) {
                    files[file.id] = Object.assign(files[file.id], d.file); render();
                }).catch(fail);
            }]);
            items.push([S.delete, function () { remove(file); }, 'ws-danger']);
        }
        popup(x, y, items);
    }

    function nameInput(row, value, onDone) {
        var span = row.querySelector('.ws-name');
        var input = document.createElement('input');
        input.value = value;
        input.className = 'ws-name-input';
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

    function currentLanguage() {
        return langSelect.value || storageGet('ws-last-lang') || 'CPP17';
    }

    function mainName(langKey) {
        var lang = langByKey[langKey] || W.languages[0];
        return MAIN_NAME[lang.key] || ('main.' + (lang ? lang.ext : 'txt'));
    }

    function uniqueName(parentId, name, except) {
        var taken = {};
        children(parentId).forEach(function (f) { if (f.id !== except) taken[f.name] = true; });
        if (!taken[name]) return name;
        var dot = name.lastIndexOf('.');
        var base = dot > 0 ? name.slice(0, dot) : name;
        var ext = dot > 0 ? name.slice(dot) : '';
        for (var i = 2; i < 1000; i++) {
            if (!taken[base + i + ext]) return base + i + ext;
        }
        return name;
    }

    function createFile(parentId, name, content, langKey) {
        var body = {parent: parentId, name: name, folder: false};
        if (langKey) body.language = langKey;
        if (typeof content === 'string') body.content = content;
        return request(api + 'new/', body).then(function (data) {
            files[data.file.id] = data.file;
            if (parentId) expanded[parentId] = true;
            render();
            return data.file;
        });
    }

    function createMain(langKey) {
        return createFile(null, uniqueName(null, mainName(langKey)), HELLO[langKey] || '', langKey).then(function (f) {
            return openFile(f.id, f);
        });
    }

    function startCreate(parentId, folder) {
        if (parentId) { expanded[parentId] = true; storageSet('ws-expanded', JSON.stringify(expanded)); }
        render();
        var row = document.createElement('div');
        row.className = 'ws-item';
        var depth = 0;
        for (var p = parentId; p; p = files[p] && files[p].parent) depth++;
        row.style.paddingLeft = (12 + depth * 14) + 'px';
        row.innerHTML = '<i class="fa ' + (folder ? 'fa-folder-o' : 'fa-file-code-o') + '"></i><span class="ws-name"></span>';
        var anchor = parentId ? tree.querySelector('.ws-item[data-id="' + parentId + '"]') : null;
        if (anchor) anchor.after(row); else tree.prepend(row);
        var empty = tree.querySelector('.ws-empty');
        if (empty) empty.remove();
        nameInput(row, uniqueName(parentId, folder ? S.newFolder : mainName(currentLanguage())), function (name) {
            if (!name) { render(); return; }
            if (folder) {
                request(api + 'new/', {parent: parentId, name: name, folder: true}).then(function (data) {
                    files[data.file.id] = data.file;
                    expanded[data.file.id] = true;
                    render();
                }).catch(function (err) { render(); fail(err); });
                return;
            }
            var ext = name.split('.').pop();
            var lang = W.languages.filter(function (l) { return l.ext === ext; })[0];
            var key = lang ? (langByKey[currentLanguage()] && langByKey[currentLanguage()].ext === ext ? currentLanguage() : lang.key) : null;
            createFile(parentId, name, key ? (HELLO[key] || '') : '', key).then(function (f) {
                openFile(f.id, f);
            }).catch(function (err) { render(); fail(err); });
        });
    }

    function applyRename(file, data) {
        files[file.id] = Object.assign(files[file.id], data.file);
        if (models[file.id]) {
            var lang = langByKey[data.file.language];
            window.monaco.editor.setModelLanguage(models[file.id], E.monacoLanguage(lang ? lang.ace : 'text'));
        }
        render();
        if (active === file.id) showFileInfo();
    }

    function startRename(file) {
        var row = tree.querySelector('.ws-item[data-id="' + file.id + '"]');
        if (!row) return;
        nameInput(row, file.name, function (name) {
            if (!name || name === file.name) { render(); return; }
            request(api + file.id + '/rename/', {name: name}).then(function (data) {
                applyRename(file, data);
            }).catch(function (err) { render(); fail(err); });
        });
    }

    function remove(file) {
        if (!confirm(S.deleteConfirm.replace('%s', file.name))) return;
        request(api + file.id + '/delete/', {}).then(function () {
            var gone = {};
            (function mark(id) {
                gone[id] = true;
                children(id).forEach(function (c) { mark(c.id); });
            })(file.id);
            Object.keys(gone).forEach(function (id) {
                delete files[id];
                if (models[id]) { models[id].dispose(); delete models[id]; }
                var i = tabs.indexOf(Number(id));
                if (i >= 0) tabs.splice(i, 1);
            });
            if (active && gone[active]) activate(tabs.length ? tabs[tabs.length - 1] : null);
            render();
        }).catch(fail);
    }

    function currentFolder() {
        return active && files[active] ? files[active].parent : null;
    }

    $('#ws-new-file').addEventListener('click', function () { startCreate(currentFolder(), false); });
    $('#tb-new').addEventListener('click', function () { startCreate(currentFolder(), false); });
    $('#ws-new-folder').addEventListener('click', function () { startCreate(currentFolder(), true); });
    $('#ws-zip').addEventListener('click', function () { location.href = W.downloadUrl; });

    /* ---- upload / download ---- */

    var uploadTarget = null;
    $('#ws-upload').addEventListener('click', function () { uploadTarget = currentFolder(); $('#ws-upload-input').click(); });
    $('#ws-upload-input').addEventListener('change', function () {
        upload(this.files, uploadTarget);
        this.value = '';
    });

    function upload(list, parentId) {
        var chain = Promise.resolve();
        var last = null;
        Array.prototype.forEach.call(list, function (file) {
            chain = chain.then(function () {
                if (file.size > 65536) {
                    setStatus(S.tooBig.replace('%s', file.name), true);
                    return;
                }
                return file.text().then(function (text) {
                    return createFile(parentId, uniqueName(parentId, file.name), text);
                }).then(function (f) { last = f; });
            });
        });
        chain.then(function () {
            setStatus(S.uploaded);
            if (last && last.language) openFile(last.id, last);
        }).catch(fail);
    }

    function downloadFile(id) {
        var f = files[id];
        var text = models[id] ? models[id].getValue() : f.content;
        var send = function (content) {
            var a = document.createElement('a');
            a.href = URL.createObjectURL(new Blob([content], {type: 'text/plain;charset=utf-8'}));
            a.download = f.name;
            document.body.appendChild(a);
            a.click();
            setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 1000);
        };
        if (typeof text === 'string') send(text);
        else request(api + id + '/').then(function (d) { send(d.file.content); }).catch(fail);
    }
    $('#cc-download').addEventListener('click', function () { if (active) downloadFile(active); });

    /* ======================= tabs and editor ======================= */

    var langSelect = $('#cc-language');
    W.languages.forEach(function (l) {
        var o = document.createElement('option');
        o.value = l.key;
        o.textContent = l.name;
        langSelect.appendChild(o);
    });
    var lastLang = storageGet('ws-last-lang');
    if (lastLang && langByKey[lastLang]) langSelect.value = lastLang;
    else if (langByKey.CPP17) langSelect.value = 'CPP17';

    function renderTabs() {
        var bar = $('#cc-tabs');
        bar.innerHTML = '';
        tabs.forEach(function (id) {
            var f = files[id];
            if (!f) return;
            var tab = document.createElement('div');
            tab.className = 'gdb-tab' + (id === active ? ' gdb-tab-active' : '');
            tab.dataset.id = id;
            tab.innerHTML = '<span class="gdb-tab-name"></span><span class="gdb-tab-dirty"></span>' +
                '<button type="button" class="gdb-tab-close">×</button>';
            tab.querySelector('.gdb-tab-name').textContent = f.name;
            tab.querySelector('.gdb-tab-close').title = S.close;
            if (dirty[id]) tab.querySelector('.gdb-tab-dirty').textContent = '●';
            bar.appendChild(tab);
        });
    }

    $('#cc-tabs').addEventListener('click', function (e) {
        var tab = e.target.closest('.gdb-tab');
        if (!tab) return;
        var id = Number(tab.dataset.id);
        if (e.target.classList.contains('gdb-tab-close')) {
            flush(id);
            var i = tabs.indexOf(id);
            tabs.splice(i, 1);
            if (active === id) activate(tabs[Math.min(i, tabs.length - 1)] || null);
            renderTabs();
            storageSet('cc-tabs', JSON.stringify(tabs));
            return;
        }
        activate(id);
    });

    function ensureEditor() {
        if (editor) return Promise.resolve(editor);
        var holder = $('#ws-editor');
        holder.innerHTML = '';
        return E.create(holder, {value: '', onRun: run, onSave: function () { save(); }}).then(function (ed) {
            editor = ed;
            return ed;
        });
    }

    function attachModel(id, file) {
        var lang = langByKey[file.language];
        var model = window.monaco.editor.createModel(file.content || '', E.monacoLanguage(lang ? lang.ace : 'text'));
        model.onDidChangeContent(function () {
            dirty[id] = true;
            renderTabs();
            clearTimeout(saveTimers[id]);
            saveTimers[id] = setTimeout(function () { flush(id); }, 900);
        });
        models[id] = model;
    }

    function openFile(id, preloaded) {
        id = Number(id);
        if (tabs.indexOf(id) < 0) tabs.push(id);
        storageSet('cc-tabs', JSON.stringify(tabs));
        if (models[id]) { activate(id); return Promise.resolve(); }
        var load = preloaded && 'content' in preloaded ? Promise.resolve({file: preloaded}) : request(api + id + '/');
        return Promise.all([load, ensureEditor()]).then(function (res) {
            files[id] = Object.assign(files[id] || {}, res[0].file);
            if (!models[id]) attachModel(id, files[id]);
            activate(id);
        }).catch(fail);
    }

    var fileButtons = ['#cc-run', '#cc-format', '#cc-share', '#cc-download', '#cc-save'];

    function activate(id) {
        active = id;
        storageSet('ws-open', id || '');
        if (!editor) { render(); return; }
        if (!id) {
            editor.editor.setModel(null);
            fileButtons.forEach(function (s) { if ($(s)) $(s).disabled = true; });
            $('#ws-stdin').disabled = true;
            render();
            return;
        }
        editor.editor.setModel(models[id]);
        editor.focus();
        fileButtons.forEach(function (s) { if ($(s)) $(s).disabled = !W.runnerEnabled && (s === '#cc-run' || s === '#cc-format'); });
        langSelect.disabled = false;
        $('#ws-stdin').disabled = false;
        $('#ws-stdin').value = files[id].stdin || '';
        showFileInfo();
        render();
    }

    function showFileInfo() {
        var f = files[active];
        if (!f) return;
        if (f.language) langSelect.value = f.language;
        $('#cc-args').value = storageGet('cc-args:' + active) || '';
    }

    function flush(id) {
        clearTimeout(saveTimers[id]);
        if (!id || !dirty[id] || !models[id]) return Promise.resolve();
        var content = models[id].getValue();
        dirty[id] = false;
        renderTabs();
        return request(api + id + '/save/', {content: content}).then(function () {
            if (files[id]) files[id].content = content;
        }).catch(function (err) {
            dirty[id] = true;
            renderTabs();
            setStatus(S.notSaved + ': ' + err.message, true);
            throw err;
        });
    }

    function flushAll() {
        return Promise.all(tabs.map(function (id) { return flush(id).catch(function () {}); }));
    }

    function save() {
        if (!active) return;
        flush(active).then(function () { setStatus(S.saved); }).catch(function () {});
    }
    $('#cc-save').addEventListener('click', save);

    function isTemplate(text) {
        var t = (text || '').trim();
        if (!t) return true;
        return Object.keys(HELLO).some(function (k) { return HELLO[k].trim() === t; });
    }

    /* Switching the language: an untouched Hello World becomes Hello World in the new
     * language (and main.cpp becomes main.py), otherwise only the highlighting changes. */
    langSelect.addEventListener('change', function () {
        var key = langSelect.value;
        storageSet('ws-last-lang', key);
        if (!active) { createMain(key).catch(fail); return; }
        var id = active;
        var file = files[id];
        var lang = langByKey[key];
        var model = models[id];
        if (model && isTemplate(model.getValue())) {
            model.setValue(HELLO[key] || '');
            var name = uniqueName(file.parent, mainName(key), id);
            if (name !== file.name) {
                flush(id).then(function () {
                    return request(api + id + '/rename/', {name: name});
                }).then(function (data) {
                    applyRename(file, data);
                    return request(api + id + '/save/', {language: key});
                }).then(function (d) { files[id].language = d.file.language; }).catch(fail);
                return;
            }
        }
        if (model && lang) window.monaco.editor.setModelLanguage(model, E.monacoLanguage(lang.ace));
        request(api + id + '/save/', {language: key}).then(function (d) {
            files[id].language = d.file.language;
        }).catch(fail);
    });

    $('#cc-args').addEventListener('input', function () { if (active) storageSet('cc-args:' + active, this.value); });

    var stdinTimer = null;
    $('#ws-stdin').addEventListener('input', function () {
        if (!active) return;
        var id = active;
        var value = $('#ws-stdin').value;
        clearTimeout(stdinTimer);
        stdinTimer = setTimeout(function () {
            request(api + id + '/save/', {stdin: value}).then(function () { files[id].stdin = value; }).catch(fail);
        }, 900);
    });

    $('#cc-settings').addEventListener('click', E.openSettings);

    /* ---- beautify ---- */

    $('#cc-format').addEventListener('click', function () {
        if (!active || !runner) return;
        var f = files[active];
        var model = models[active];
        runner.getToken().then(function (token) {
            return fetch(runner.url + '/format', {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({token: token, language: f.language, source: model.getValue(),
                                      indent: model.getOptions().tabSize})
            }).then(function (r) { return r.json(); });
        }).then(function (res) {
            if (res.status === 'ok') {
                editor.editor.pushUndoStop();
                editor.editor.executeEdits('format', [{range: model.getFullModelRange(), text: res.source}]);
                editor.editor.pushUndoStop();
                setStatus(S.formatted);
            } else if (res.status === 'unsupported') {
                var action = editor.editor.getAction('editor.action.formatDocument');
                if (action && action.isSupported()) action.run();
                else setStatus(S.noFormat);
            } else {
                setStatus(res.message || S.error);
            }
        }).catch(fail);
    });

    /* ---- share ---- */

    if ($('#cc-share')) $('#cc-share').addEventListener('click', function () {
        if (!active) return;
        var file = files[active];
        flush(active).then(function () {
            return request(api + file.id + '/share/', {on: true});
        }).then(function (d) {
            files[file.id] = Object.assign(files[file.id], d.file);
            var link = W.shareBase + d.file.share_key + '/';
            if (navigator.clipboard) navigator.clipboard.writeText(link).catch(function () {});
            prompt(S.shareCopied, link);
        }).catch(fail);
    });

    /* ======================= console ======================= */

    var term = null;
    var fit = null;
    function termTheme() {
        var dark = document.documentElement.getAttribute('data-theme') === 'dark' ||
            (document.documentElement.getAttribute('data-theme') !== 'light' &&
             window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);
        return dark ? {background: '#1e1e1e', foreground: '#e3e6ea', cursor: '#e3e6ea'}
                    : {background: '#ffffff', foreground: '#1b2430', cursor: '#1b2430', selectionBackground: '#cfe0f5'};
    }
    function refit() { if (fit) setTimeout(function () { try { fit.fit(); } catch (e) { /* hidden */ } }, 0); }
    if (window.Terminal) {
        term = new window.Terminal({
            fontFamily: "'JetBrains Mono', Consolas, 'Courier New', monospace",
            fontSize: 14, convertEol: true, cursorBlink: true, scrollback: 5000, theme: termTheme()
        });
        fit = new window.FitAddon.FitAddon();
        term.loadAddon(fit);
        term.open($('#cc-terminal'));
        refit();
        window.addEventListener('resize', refit);
        var paint = function () { $('.gdb-console-body').style.background = termTheme().background; };
        paint();
        new MutationObserver(function () { term.options.theme = termTheme(); paint(); })
            .observe(document.documentElement, {attributes: true, attributeFilter: ['data-theme']});
    }

    var session = null;     // {socket, line}

    function termPrint(text, style) {
        if (!term) return;
        var codes = {dim: '\x1b[2m', red: '\x1b[31m', green: '\x1b[32m', yellow: '\x1b[33m', bold: '\x1b[1m'};
        term.write((style ? codes[style] : '') + text + (style ? '\x1b[0m' : ''));
    }
    function nl(text) { return String(text || '').replace(/\r?\n/g, '\r\n'); }

    if (term) term.onData(function (data) {
        if (!session || !session.running) return;
        for (var i = 0; i < data.length; i++) {
            var ch = data[i];
            if (ch === '\r' || ch === '\n') {
                term.write('\r\n');
                sendInput(session.line + '\n');
                session.line = '';
            } else if (ch === '\x7f' || ch === '\b') {
                if (session.line.length) {
                    session.line = Array.from(session.line).slice(0, -1).join('');
                    term.write('\b \b');
                }
            } else if (ch === '\x03') {
                term.write('^C\r\n');
                stop();
                return;
            } else if (ch === '\x04') {
                if (session.line) { sendInput(session.line); session.line = ''; }
                send({type: 'eof'});
            } else if (ch === '\x1b') {
                // Arrow keys and other escape sequences are ignored.
                var m = /^\x1b\[[0-9;]*[A-Za-z~]/.exec(data.slice(i));
                if (m) i += m[0].length - 1;
            } else if (ch >= ' ' || ch === '\t') {
                session.line += ch;
                term.write(ch);
            }
        }
    });

    function send(message) {
        if (session && session.socket.readyState === 1) session.socket.send(JSON.stringify(message));
    }
    function sendInput(text) { send({type: 'in', data: text}); }

    function setRunning(on) {
        $('#cc-run').disabled = on || !active;
        $('#cc-stop').disabled = !on;
    }

    function siblingFiles() {
        var main = files[active];
        var others = children(main.parent).filter(function (f) { return !f.folder && f.id !== main.id; });
        return Promise.all(others.map(function (f) {
            if (models[f.id]) return Promise.resolve([f.name, models[f.id].getValue()]);
            if (typeof f.content === 'string') return Promise.resolve([f.name, f.content]);
            return request(api + f.id + '/').then(function (d) {
                files[f.id] = Object.assign(files[f.id], d.file);
                return [f.name, d.file.content];
            });
        })).then(function (pairs) {
            var out = {};
            pairs.forEach(function (p) { out[p[0]] = p[1]; });
            return out;
        });
    }

    function parseArgs(text) {
        var out = [];
        var re = /"([^"]*)"|'([^']*)'|(\S+)/g;
        var m;
        while ((m = re.exec(text))) out.push(m[1] !== undefined ? m[1] : m[2] !== undefined ? m[2] : m[3]);
        return out;
    }

    function mode() {
        return document.querySelector('input[name=cc-mode]:checked').value;
    }

    function run() {
        if (!runner || !active || (session && session.running)) return;
        var file = files[active];
        if (!file.language) { alert(S.pickLanguage); return; }
        var source = models[active].getValue();
        var args = parseArgs($('#cc-args').value);
        flushAll();
        openConsole();
        if (term) { term.reset(); }
        siblingFiles().then(function (extra) {
            if (mode() === 'text') return runPrepared(file, source, extra, args);
            return runInteractive(file, source, extra, args);
        }).catch(fail);
    }

    function verdictText(verdict, wall) {
        return {TLE: wall ? S.tleWait : S.tle, MLE: S.mle, OLE: S.ole, RTE: S.rte}[verdict] || verdict;
    }

    function printExit(verdict, code, time, memory, wall) {
        var tail = ' (' + (time || 0).toFixed(2) + ' ' + S.sec + ', ' + Math.round((memory || 0) / 1024) + ' ' + S.mb + ')';
        if (verdict && verdict !== 'OK' && !(verdict === 'RTE' && code)) {
            termPrint('\r\n...' + verdictText(verdict, wall) + '\r\n', 'red');
        }
        termPrint('\r\n...' + S.finished + ' ' + (code || 0), code ? 'red' : 'green');
        termPrint(tail + '\r\n', 'dim');
    }

    function runPrepared(file, source, extra, args) {
        setRunning(true);
        termPrint(S.running + '\r\n', 'dim');
        runner.run(file.language, source, $('#ws-stdin').value, function () {
            termPrint(S.queued + '\r\n', 'dim');
        }, {main: file.name, files: extra, args: args}).then(function (r) {
            if (term) term.reset();
            if (r.status === 'compile_error') {
                termPrint(S.compileError + '\r\n', 'red');
                termPrint(nl(r.compile_output));
            } else if (r.status !== 'ok') {
                termPrint(nl(r.message || S.error) + '\r\n', 'red');
            } else {
                termPrint(nl(r.stdout));
                if (r.stderr) termPrint(nl(r.stderr), 'red');
                printExit(r.verdict, r.exit_code, r.time, r.memory, false);
            }
        }).catch(function (err) {
            termPrint(nl(err.message || S.network) + '\r\n', 'red');
        }).then(function () { setRunning(false); });
    }

    function socketUrl() {
        var base = runner.url;
        if (/^https?:/.test(base)) return base.replace(/^http/, 'ws') + '/session';
        return location.origin.replace(/^http/, 'ws') + base + '/session';
    }

    function runInteractive(file, source, extra, args) {
        refit();
        setRunning(true);
        runner.getToken().then(function (token) {
            var socket = new WebSocket(socketUrl());
            session = {socket: socket, line: '', running: true, started: Date.now()};
            var current = session;
            socket.onopen = function () {
                socket.send(JSON.stringify({token: token, language: file.language, source: source,
                                            main: file.name, files: extra, args: args}));
            };
            socket.onmessage = function (event) {
                var m = JSON.parse(event.data);
                if (m.type === 'status') {
                    termPrint((m.text === 'queued' ? S.queued : S.compiling) + '\r\n', 'dim');
                } else if (m.type === 'compile_error') {
                    termPrint(S.compileError + '\r\n', 'red');
                    termPrint(nl(m.output));
                } else if (m.type === 'started') {
                    if (term) term.reset();
                    if (m.warning && m.warning.trim()) termPrint(nl(m.warning), 'yellow');
                    if (term) term.focus();
                } else if (m.type === 'out') termPrint(m.data);
                else if (m.type === 'err') termPrint(m.data, 'red');
                else if (m.type === 'exit') printExit(m.verdict, m.exit_code, m.time, m.memory, m.wall);
            };
            socket.onerror = function () { termPrint('\r\n' + S.network + '\r\n', 'red'); };
            socket.onclose = function () {
                current.running = false;
                if (session === current) session = null;
                setRunning(false);
            };
        }).catch(function (err) {
            termPrint('\r\n' + nl(err.message || S.network) + '\r\n', 'red');
            setRunning(false);
        });
    }

    function stop() {
        if (!session) return;
        send({type: 'kill'});
        var s = session;
        setTimeout(function () { try { s.socket.close(); } catch (e) { /* ignore */ } }, 500);
    }

    $('#cc-run').addEventListener('click', run);
    $('#cc-stop').addEventListener('click', stop);
    $('#cc-clear').addEventListener('click', function () { if (term) term.reset(); });

    function setMode(value) {
        var radio = document.querySelector('input[name=cc-mode][value="' + value + '"]');
        if (radio) radio.checked = true;
        storageSet('cc-mode', value);
        $('#ws-stdin').hidden = value !== 'text';
        refit();
    }
    document.querySelectorAll('input[name=cc-mode]').forEach(function (r) {
        r.addEventListener('change', function () { setMode(mode()); });
    });
    setMode(storageGet('cc-mode') || 'terminal');

    $('#cc-run-menu').addEventListener('click', function (e) {
        e.stopPropagation();
        var rect = this.getBoundingClientRect();
        popup(rect.left, rect.bottom + 4, [
            [S.runInteractive, function () { setMode('terminal'); run(); }],
            [S.runText, function () { setMode('text'); run(); }]
        ]);
    });

    /* ---- console panel: resize, collapse, expand ---- */

    var panel = $('#ws-panel');
    var main = document.querySelector('.gdb-main');
    var h = storageGet('ws-panel-h');
    if (h) panel.style.flexBasis = h + 'px';

    function openConsole() {
        if (panel.classList.contains('gdb-collapsed')) toggleCollapse();
    }
    function toggleCollapse() {
        var collapsed = panel.classList.toggle('gdb-collapsed');
        main.classList.remove('gdb-console-max');
        $('#cc-toggle').title = collapsed ? S.expand : S.collapse;
        $('#cc-toggle i').className = 'fa ' + (collapsed ? 'fa-chevron-up' : 'fa-chevron-down');
        refit();
    }
    $('#cc-toggle').title = S.collapse;
    $('#cc-toggle').addEventListener('click', toggleCollapse);
    $('#cc-maximize').addEventListener('click', function () {
        panel.classList.remove('gdb-collapsed');
        var max = main.classList.toggle('gdb-console-max');
        $('#cc-maximize i').className = 'fa ' + (max ? 'fa-compress' : 'fa-expand');
        $('#cc-maximize').title = max ? S.collapse : S.expand;
        refit();
    });
    $('#cc-maximize').title = S.expand;

    $('#ws-hsplit').addEventListener('mousedown', function (e) {
        e.preventDefault();
        var handle = e.target;
        handle.classList.add('gdb-dragging');
        panel.classList.remove('gdb-collapsed');
        main.classList.remove('gdb-console-max');
        function move(ev) {
            var work = main.getBoundingClientRect();
            var height = Math.min(Math.max(work.bottom - ev.clientY, 90), work.height - 160);
            panel.style.flexBasis = height + 'px';
            storageSet('ws-panel-h', Math.round(height));
            refit();
        }
        function up() {
            handle.classList.remove('gdb-dragging');
            document.removeEventListener('mousemove', move);
            document.removeEventListener('mouseup', up);
        }
        document.addEventListener('mousemove', move);
        document.addEventListener('mouseup', up);
    });

    // Interface language: save the files, switch, and reload the page.
    $('.gdb-lang').addEventListener('submit', function (e) {
        e.preventDefault();
        var form = this;
        var data = new FormData(form);
        if (e.submitter) data.append('language', e.submitter.value);
        flushAll().then(function () {
            return fetch(form.action, {method: 'POST', body: data, credentials: 'same-origin'});
        }).then(function () { location.reload(); });
    });

    window.addEventListener('beforeunload', function (e) {
        var pending = Object.keys(dirty).some(function (k) { return dirty[k]; });
        if (pending) { flushAll(); e.preventDefault(); e.returnValue = ''; }
    });

    document.addEventListener('keydown', function (e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter' && !(editor && editor.editor.hasTextFocus())) {
            e.preventDefault();
            run();
        }
        if ((e.ctrlKey || e.metaKey) && (e.key === 's' || e.key === 'S')) {
            e.preventDefault();
            save();
        }
    });

    /* ---- start: reopen the last tabs, or make main.cpp on the first visit ---- */

    request(api).then(function (data) {
        data.files.forEach(function (f) { files[f.id] = f; });
        render();
        var saved = loadJSON('cc-tabs', []).filter(function (id) { return files[id] && !files[id].folder; });
        var last = Number(storageGet('ws-open'));
        if (!saved.length && last && files[last] && !files[last].folder) saved = [last];
        if (!saved.length) {
            var first = children(null).filter(function (f) { return !f.folder; })[0];
            if (first) saved = [first.id];
        }
        if (!saved.length) return createMain(currentLanguage());
        var chain = Promise.resolve();
        saved.forEach(function (id) { chain = chain.then(function () { return openFile(id); }); });
        return chain.then(function () { if (last && models[last]) activate(last); });
    }).catch(fail);
});
