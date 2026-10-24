#!/bin/bash
# Installs the compilers on the judge machine: Node.js 22, Go 1.25, Kotlin 2.2, Free Pascal,
# Java 21, C# and F# (.NET 10) and Scratch 3 (scratch-run).
# Run as root on judge.oshsu.kg. Afterwards add the printed lines to the runtime: section of
# every judge config (~admin/judge-config/judge.yml, judge2.yml) and restart the judges.
set -euo pipefail

NODE_VERSION=22.11.0
GO_VERSION=1.25.2
KOTLIN_VERSION=2.2.20
SCRATCH_RUN_VERSION=0.1.7
HERE=$(cd "$(dirname "$0")" && pwd)
JUDGE_SERVER=${JUDGE_SERVER:-/home/admin/judge-server}

apt-get update
apt-get install -y fpc unzip curl clang-format dotnet-sdk-10.0 openjdk-21-jdk-headless

# .NET executors (C# and F#) and Scratch; Mono stays only for old submissions.
cp "$HERE/CSHARP.py" "$HERE/FSHARP.py" "$HERE/SB3.py" "$JUDGE_SERVER/dmoj/executors/"

fetch() {  # url file
    curl -fsSL --retry 3 "$1" -o "$2"
}

if [ ! -x /opt/node22/bin/node ]; then
    fetch "https://nodejs.org/dist/v$NODE_VERSION/node-v$NODE_VERSION-linux-x64.tar.xz" /tmp/node.tar.xz
    mkdir -p /opt/node22
    tar xJf /tmp/node.tar.xz -C /opt/node22 --strip-components=1
fi

if [ ! -x "/opt/go$GO_VERSION/bin/go" ]; then
    fetch "https://go.dev/dl/go$GO_VERSION.linux-amd64.tar.gz" /tmp/go.tar.gz
    mkdir -p "/opt/go$GO_VERSION"
    tar xzf /tmp/go.tar.gz -C "/opt/go$GO_VERSION" --strip-components=1
fi

if [ ! -x "/opt/kotlinc-$KOTLIN_VERSION/bin/kotlinc" ]; then
    fetch "https://github.com/JetBrains/kotlin/releases/download/v$KOTLIN_VERSION/kotlin-compiler-$KOTLIN_VERSION.zip" \
        /tmp/kotlin.zip
    rm -rf /tmp/kotlinc && unzip -q -o /tmp/kotlin.zip -d /tmp
    rm -rf "/opt/kotlinc-$KOTLIN_VERSION" && mv /tmp/kotlinc "/opt/kotlinc-$KOTLIN_VERSION"
fi

if [ ! -x /usr/local/bin/scratch-run ]; then
    fetch "https://github.com/VNOI-Admin/scratch-run/releases/download/$SCRATCH_RUN_VERSION/scratch-run_${SCRATCH_RUN_VERSION}_linux_amd64.zip" \
        /tmp/scratch-run.zip
    unzip -q -o /tmp/scratch-run.zip -d /tmp/scratch-run
    install -m 755 /tmp/scratch-run/scratch-run /usr/local/bin/scratch-run
fi

bash "$HERE/build_pch.sh"

JAVA21=/usr/lib/jvm/java-21-openjdk-amd64/bin

cat <<RUNTIME

Add these lines under "runtime:" in each judge config (replace a line with the same name):

  g++14: $(command -v g++)
  g++17: $(command -v g++)
  g++20: $(command -v g++)
  node: /opt/node22/bin/node
  go: /opt/go$GO_VERSION/bin/go
  fpc: $(command -v fpc)
  kotlinc: /opt/kotlinc-$KOTLIN_VERSION/bin/kotlinc
  kotlin_vm: $JAVA21/java
  java: $JAVA21/java
  javac: $JAVA21/javac
  dotnet: $(command -v dotnet)
  scratch-run: /usr/local/bin/scratch-run

Keep the existing java8/javac8 lines: Java 8 stays for old submissions.
Then: systemctl restart olymp-judge olymp-judge2 olymp-runner
Check: cd $JUDGE_SERVER && venv/bin/python $HERE/test_new_executors.py ~admin/judge-config/judge.yml
RUNTIME
