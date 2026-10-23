#!/bin/bash
# Downloads front-end libraries that are too big to keep in git into resources/vendor/.
# Run once after checkout and on every deploy (it is a no-op when the version is already there).
set -e
cd "$(dirname "$0")/.."
MONACO_VERSION=0.52.0
DEST=resources/vendor/monaco
if [ -f "$DEST/VERSION" ] && [ "$(cat $DEST/VERSION)" = "$MONACO_VERSION" ]; then
    echo "monaco $MONACO_VERSION already present"
    exit 0
fi
TMP=$(mktemp -d)
curl -fsSL "https://registry.npmjs.org/monaco-editor/-/monaco-editor-$MONACO_VERSION.tgz" -o "$TMP/monaco.tgz"
tar xzf "$TMP/monaco.tgz" -C "$TMP"
rm -rf "$DEST"
mkdir -p "$DEST"
cp -r "$TMP/package/min/vs" "$DEST/vs"
echo "$MONACO_VERSION" > "$DEST/VERSION"
rm -rf "$TMP"
echo "monaco $MONACO_VERSION installed into $DEST"
