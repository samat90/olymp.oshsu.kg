#!/usr/bin/env bash
set -euo pipefail
# CPython source and checksum from the official 3.14.7 release page.
version=3.14.7
prefix=/opt/python/$version
build=/var/tmp/olymp-python-$version
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y --no-install-recommends build-essential pkg-config curl ca-certificates \
    libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev libffi-dev \
    liblzma-dev libzstd-dev uuid-dev libgdbm-dev libncurses-dev
mkdir -p "$build"
cd "$build"
python3 - <<'PY'
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib
import urllib.request

url = 'https://www.python.org/ftp/python/3.14.7/Python-3.14.7.tar.xz'
sha = '3b48dac8fb59f62eaa67ac83c1eb12bda1b7a08406dd286e252c11a66be27f81'
target = Path('source.tar.xz')
if not target.exists() or hashlib.sha256(target.read_bytes()).hexdigest() != sha:
    size = 24053924
    ranges = [(start, min(start + 1048576, size) - 1) for start in range(0, size, 1048576)]
    def fetch(bounds):
        start, end = bounds
        request = urllib.request.Request(url, headers={'Range': f'bytes={start}-{end}'})
        with urllib.request.urlopen(request, timeout=180) as response:
            assert response.status == 206
            assert response.headers['Content-Range'] == f'bytes {start}-{end}/{size}'
            data = response.read()
            assert len(data) == end - start + 1
            return data
    with ThreadPoolExecutor(max_workers=8) as pool:
        data = b''.join(pool.map(fetch, ranges))
    assert hashlib.sha256(data).hexdigest() == sha
    target.write_bytes(data)
print('Official CPython source verified', flush=True)
PY
echo '3b48dac8fb59f62eaa67ac83c1eb12bda1b7a08406dd286e252c11a66be27f81  source.tar.xz' | sha256sum --check
tar -xf source.tar.xz
cd "Python-$version"
./configure --prefix="$prefix" --with-ensurepip=no
make -j2
make altinstall -j2
"$prefix/bin/python3.14" -c 'import sys, ssl, sqlite3, bz2, lzma, ctypes, decimal, compression.zstd; assert sys.version_info[:3] == (3, 14, 7); print(sys.version)'
