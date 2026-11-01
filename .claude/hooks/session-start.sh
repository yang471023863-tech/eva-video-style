#!/bin/bash
# 每次打开新会话时自动装好「AI 剪辑课」：eva-video-style 引擎 + ai-video-course 技能 + 依赖。
# 已经装好的步骤会跳过，所以重复运行很快。
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

REPO="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
SK="$HOME/.claude/skills"
EVA="$SK/eva-video-style"
MAGS="$SK/ai-video-course"
mkdir -p "$SK"

# 1. 引擎：把仓库（去掉 .git / .claude / course）同步成 eva-video-style 技能，保留已装的 node_modules
mkdir -p "$EVA"
tar -C "$REPO" --exclude=./.git --exclude=./.claude --exclude=./course --exclude=./node_modules -cf - . | tar -C "$EVA" -xf -

# 2. 课程技能：仓库里的 course/ai-video-course（含字体）
rm -rf "$MAGS"
cp -r "$REPO/course/ai-video-course" "$MAGS"
chmod +x "$MAGS"/scripts/* "$EVA"/scripts/*.sh 2>/dev/null || true

# 3. ffmpeg（要带 libass 字幕）
if ! ffmpeg -hide_banner -filters 2>/dev/null | grep -c " subtitles " >/dev/null; then
  apt-get update
  DEBIAN_FRONTEND=noninteractive apt-get install -y -o Dpkg::Options::=--force-confold ffmpeg
fi

# 4. Playwright，配套云端预装的 Chromium（只在本脚本改动后或 node_modules 丢失时重装）
hashes="$EVA/node_modules/.session-start.sha256"
if ! sha256sum --check --status "$hashes" 2>/dev/null; then
  rm -f "$hashes"
  (cd "$EVA" && npm install --no-save --no-audit --no-fund playwright@1.63.0)
  sha256sum "$REPO/.claude/hooks/session-start.sh" > "$hashes"
fi

# 5. Python 依赖（版本锁死：av 不能用 19）
if ! python3 -c "import faster_whisper, av, numpy, sys; sys.exit(0 if av.__version__ == '15.1.0' and faster_whisper.__version__ == '1.2.1' else 1)" 2>/dev/null; then
  python3 -m pip install -q "faster-whisper==1.2.1" "av==15.1.0" numpy \
    || python3 -m pip install -q --break-system-packages "faster-whisper==1.2.1" "av==15.1.0" numpy
fi

echo "AI 剪辑课已就绪：$EVA 和 $MAGS"
