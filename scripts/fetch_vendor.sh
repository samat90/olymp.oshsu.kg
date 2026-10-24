#!/bin/bash
# Downloads front-end libraries that are too big to keep in git into resources/vendor/.
# Run once after checkout and on every deploy (it is a no-op when the version is already there).
set -e
cd "$(dirname "$0")/.."
# fetch <npm package> <version> <dest dir> <path inside package>...
fetch() {
    local pkg=$1 version=$2 dest=$3
    shift 3
    if [ -f "$dest/VERSION" ] && [ "$(cat "$dest/VERSION")" = "$version" ]; then
        echo "$pkg $version already present"
        return
    fi
    local tmp
    tmp=$(mktemp -d)
    curl -fsSL "https://registry.npmjs.org/$pkg/-/$(basename "$pkg")-$version.tgz" -o "$tmp/pkg.tgz"
    tar xzf "$tmp/pkg.tgz" -C "$tmp"
    rm -rf "$dest"
    mkdir -p "$dest"
    for path in "$@"; do
        cp -r "$tmp/package/$path" "$dest/"
    done
    echo "$version" > "$dest/VERSION"
    rm -rf "$tmp"
    echo "$pkg $version installed into $dest"
}

fetch monaco-editor 0.52.0 resources/vendor/monaco min/vs
fetch @xterm/xterm 5.5.0 resources/vendor/xterm lib/xterm.js css/xterm.css
fetch @xterm/addon-fit 0.10.0 resources/vendor/xterm-fit lib/addon-fit.js
