#!/usr/bin/env python3
"""用真实音效样本混音效轨：cues.json（render.mjs --cues 导出）→ wav。
用法：python3 sfxmix.py cues.json 总秒数 输出.wav 音效目录
音效目录放 pop1/pop2/whoosh/whoosh2/ding/glow.wav（从飞书「剪辑素材库」下载）；impact、click 程序合成。
cue 第 4 项可带 {"rate": 变调倍数, "len": 截取秒数}。
"""
import json, sys, subprocess, numpy as np, wave
cues, dur, out, sdir = json.load(open(sys.argv[1])), float(sys.argv[2]), sys.argv[3], sys.argv[4]
SR = 48000
def load(name, maxlen):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', f'{sdir}/{name}.wav', '-ac', '2', '-ar', str(SR), '-t', str(maxlen), '-f', 'f32le', '-'], capture_output=True).stdout
    x = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
    n = len(x); fade = min(n, int(SR * .06)); x[-fade:] *= np.linspace(1, 0, fade)[:, None]   # 尾巴淡出
    return x / (np.abs(x).max() + 1e-9) * .7
def impact():
    t = np.arange(int(SR * .7)) / SR
    s = np.sin(2 * np.pi * (45 + 70 * np.exp(-t * 18)) * t) * np.exp(-t * 6) + np.random.default_rng(1).standard_normal(len(t)) * np.exp(-t * 40) * .15
    s = s / np.abs(s).max() * .7; return np.stack([s, s], 1)
def click():
    t = np.arange(int(SR * .05)) / SR; r = np.random.default_rng(3).standard_normal(len(t))
    s = (r * np.exp(-t * 260) * .6 + np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 180) * .5); s = s / np.abs(s).max() * .7; return np.stack([s, s], 1)
def vary(x, rate=1.0, length=None):
    if rate != 1.0:
        n = int(len(x) / rate); idx = np.linspace(0, len(x) - 1, n); x = np.stack([np.interp(idx, np.arange(len(x)), x[:, c]) for c in range(2)], 1)
    if length:
        n = min(len(x), int(length * SR)); x = x[:n].copy(); f = min(n, int(SR * .08)); x[-f:] *= np.linspace(1, 0, f)[:, None]
    return x
LIB = {'click': click(), 'whoosh2': load('whoosh2', .35), 'pop1': load('pop1', .35), 'pop2': load('pop2', .35), 'whoosh': load('whoosh', .6), 'ding': load('ding', .8), 'glow': load('glow', .9), 'impact': impact()}
buf = np.zeros((int(SR * (dur + 1)), 2), np.float32)
for kind, t, g, *rest in cues:
    a = rest[0] if rest else {}
    s = LIB.get(kind)
    if s is not None: s = vary(s, a.get('rate', 1.0), a.get('len'))
    if s is None: print('跳过', kind); continue
    i = int(t * SR); j = min(len(buf), i + len(s)); buf[i:j] += s[:j - i] * g
buf = buf[:int(SR * dur)]; buf /= max(1, np.abs(buf).max() / .95)
w = wave.open(out, 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((buf * 32767).astype('<i2').tobytes()); w.close()
print(out, len(cues), '个音效点')
