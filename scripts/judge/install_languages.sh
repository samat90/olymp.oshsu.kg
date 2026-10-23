#!/bin/bash
# Installs the compilers for JavaScript (Node.js 22), Go, Kotlin and Free Pascal on the judge machine.
# Run as root on judge.oshsu.kg. Afterwards add the printed lines to the runtime: section of
# every judge config (~admin/judge-config/judge.yml, judge2.yml) and restart the judges.
set -euo pipefail

NODE_VERSION=22.11.0
KOTLIN_VERSION=2.0.21

apt-get update
apt-get install -y golang-go fpc unzip curl

if [ ! -x /opt/node22/bin/node ]; then
    curl -fsSL "https://nodejs.org/dist/v$NODE_VERSION/node-v$NODE_VERSION-linux-x64.tar.xz" -o /tmp/node.tar.xz
    mkdir -p /opt/node22
    tar xJf /tmp/node.tar.xz -C /opt/node22 --strip-components=1
fi

if [ ! -x /opt/kotlinc/bin/kotlinc ]; then
    curl -fsSL "https://github.com/JetBrains/kotlin/releases/download/v$KOTLIN_VERSION/kotlin-compiler-$KOTLIN_VERSION.zip" \
        -o /tmp/kotlin.zip
    unzip -q -o /tmp/kotlin.zip -d /opt
    ln -sf /opt/kotlinc/bin/kotlinc /usr/local/bin/kotlinc
fi

JAVA=$(readlink -f "$(command -v java)")

cat <<RUNTIME

Add these lines under "runtime:" in each judge config:

  node: /opt/node22/bin/node
  go: $(command -v go)
  fpc: $(command -v fpc)
  kotlinc: /opt/kotlinc/bin/kotlinc
  kotlin_vm: $JAVA

Then: systemctl restart olymp-judge olymp-judge2 olymp-runner
RUNTIME
