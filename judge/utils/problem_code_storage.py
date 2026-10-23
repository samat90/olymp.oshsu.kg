"""Filesystem checks shared by the website and the separate judge host."""
import hashlib
import json
import os
from pathlib import Path


def directory_digest(directory):
    directory = Path(directory)
    if directory.is_symlink():
        raise ValueError('Problem directory must not be a symlink: %s' % directory.name)
    if not directory.exists():
        return None
    result = hashlib.sha256()
    for file in sorted(directory.rglob('*')):
        if file.is_symlink():
            raise ValueError('Unexpected symlink in problem data: %s' % file.name)
        if file.is_file():
            result.update(file.relative_to(directory).as_posix().encode())
            result.update(b'\0')
            with file.open('rb') as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                    result.update(chunk)
            result.update(b'\0')
    return result.hexdigest()


def data_path(root, code):
    root = Path(root).resolve()
    path = root / code
    if not code or Path(code).name != code or not path.resolve().is_relative_to(root):
        raise ValueError('Unsafe problem data path')
    return path


def check_storage(rows, root, rollback=False):
    for row in rows:
        source = data_path(root, row['new_code'] if rollback else row['old_code'])
        target = data_path(root, row['old_code'] if rollback else row['new_code'])
        if source == target:
            if directory_digest(source) != row['digest']:
                raise ValueError('Problem data changed: %s' % source.name)
            continue
        if source.exists() and target.exists():
            raise ValueError('Both source and destination exist: %s' % source.name)
        actual = directory_digest(source if source.exists() else target)
        if actual != row['digest']:
            raise ValueError('Problem data changed or missing: %s' % source.name)


def log_move(journal, source, target):
    if journal is not None:
        descriptor = os.open(journal, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
        with os.fdopen(descriptor, 'a', encoding='utf-8') as stream:
            stream.write(json.dumps({'from': str(source), 'to': str(target)}) + '\n')
            stream.flush()
            os.fsync(stream.fileno())


def rename_storage(rows, root, rollback=False, journal=None):
    check_storage(rows, root, rollback)
    moved = []
    try:
        for row in rows:
            source = data_path(root, row['new_code'] if rollback else row['old_code'])
            target = data_path(root, row['old_code'] if rollback else row['new_code'])
            if source != target and source.exists():
                source.rename(target)
                moved.append((source, target))
                log_move(journal, source, target)
    except Exception:
        for source, target in reversed(moved):
            target.rename(source)
            log_move(journal, target, source)
        raise
    return moved
