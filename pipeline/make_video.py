#!/usr/bin/env python3
"""雑学動画ジェネレーター v2
1つの台本(script.json)から、横動画(本編)と、その一部を切り出した縦ショートを作る。
- 画面の動き: 背景の泡が流れる / 見出しスライドイン / 絵文字ポップ＋ゆらゆら / 字幕ふわっと表示 / 進行バー
- BGM: 毎回シードを変えて自動作曲(著作権フリー)、ナレーション中は自動で音量を下げる
usage: python3 make_video.py script.json outdir [--frames]
"""
import json, os, sys, ssl, asyncio, subprocess, hashlib, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import edge_tts, edge_tts.communicate as ec

CA = os.path.expanduser("~/.ccr/ca-bundle.crt")
if os.path.exists(CA):
    ec._SSL_CTX = ssl.create_default_context(cafile=CA)

FONT_B = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
FONT_M = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
FPS = 30
INK = (40, 30, 60)
THEMES = [((255, 214, 165), (255, 173, 173)), ((189, 224, 254), (205, 180, 219)),
          ((202, 255, 191), (155, 246, 255)), ((255, 238, 173), (255, 198, 255)),
          ((253, 255, 182), (255, 214, 165)), ((160, 196, 255), (189, 178, 255))]

_fc = {}
def font(path, size):
    k = (path, size)
    if k not in _fc:
        f = None
        for i in range(10):
            try:
                g = ImageFont.truetype(path, size, index=i)
            except OSError:
                break
            if "JP" in g.getname()[0]:
                f = g; break
        _fc[k] = f or ImageFont.truetype(path, size)
    return _fc[k]

def emoji_img(ch, size):
    f = ImageFont.truetype(EMOJI, 109)
    im = Image.new("RGBA", (160, 140), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((4, 4), ch, font=f, embedded_color=True)
    im = im.crop(im.getbbox())
    r = size / max(im.size)
    return im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)

_probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
def wrap_ja(text, f, maxw):
    lines, cur = [], ""
    for ch in text:
        if _probe.textlength(cur + ch, font=f) > maxw and cur:
            if ch in "、。！？」』）ーゃゅょっャュョッぁぃぅぇぉァィゥェォ…":
                cur += ch; lines.append(cur); cur = ""; continue
            lines.append(cur); cur = ch
        else:
            cur += ch
    if cur: lines.append(cur)
    # 最終行が1〜2文字だけになるのを防ぐ
    if len(lines) >= 2 and len(lines[-1]) <= 2:
        k = 2
        while k < len(lines[-2]) - 1 and lines[-2][-k] in "、。！？」』）ーゃゅょっャュョッぁぃぅぇぉァィゥェォ…":
            k += 1
        lines[-2], lines[-1] = lines[-2][:-k], lines[-2][-k:] + lines[-1]
    return lines

def text_block(lines, f, lh, align="center", color=INK, width=None):
    w = width or int(max(_probe.textlength(l, font=f) for l in lines)) + 8
    im = Image.new("RGBA", (w, lh * len(lines) + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, l in enumerate(lines):
        if align == "center":
            d.text((w // 2, lh // 2 + i * lh + 6), l, font=f, fill=color, anchor="mm")
        else:
            d.text((0, lh // 2 + i * lh + 6), l, font=f, fill=color, anchor="lm")
    return im

def caption_box(text, f, lh, maxw, pad=36):
    lines = wrap_ja(text, f, maxw)
    t = text_block(lines, f, lh)
    W, H = t.width + pad * 2 + 20, t.height + pad * 2
    box = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([6, 10, W - 6, H - 2], 36, fill=(60, 30, 80, 60))
    box.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    ImageDraw.Draw(box).rounded_rectangle([0, 0, W - 8, H - 10], 36, fill=(255, 255, 255, 240))
    box.alpha_composite(t, ((W - 8 - t.width) // 2, (H - 10 - t.height) // 2))
    return box

def pill(text, f, h):
    w = int(_probe.textlength(text, font=f)) + h
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], h // 2, fill=INK)
    d.text((w // 2, h // 2), text, font=f, fill=(255, 255, 255), anchor="mm")
    return im

def make_bg(W, H, theme, seed):
    """グラデーション＋ゆっくり流れる泡(縦に2画面分)"""
    c1, c2 = theme
    g = np.linspace(0, 1, H)[:, None]
    arr = (np.array(c1)[None, None] * (1 - g[..., None]) + np.array(c2)[None, None] * g[..., None])
    base = Image.fromarray(np.repeat(arr, W, axis=1).astype(np.uint8), "RGB").convert("RGBA")
    rnd = random.Random(seed)
    bub = Image.new("RGBA", (W, H * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(bub)
    for _ in range(18):
        r = rnd.randint(30, 160); x = rnd.randint(-50, W + 50); y = rnd.randint(0, H * 2)
        a = rnd.randint(35, 80)
        for yy in (y, y - H * 2, y + H * 2):
            d.ellipse([x - r, yy - r, x + r, yy + r], fill=(255, 255, 255, a))
    bub = bub.filter(ImageFilter.GaussianBlur(4))
    return base, bub

def ease_out(t):
    t = max(0.0, min(1.0, t)); return 1 - (1 - t) ** 3

def back_out(t):
    t = max(0.0, min(1.0, t)); s = 1.9
    return 1 + (s + 1) * (t - 1) ** 3 + s * (t - 1) ** 2

def with_alpha(im, a):
    if a >= 0.999: return im
    im = im.copy(); al = im.getchannel("A").point(lambda v: int(v * a)); im.putalpha(al); return im

def paste(base, im, x, y, a=1.0):
    if a <= 0.01: return
    im = with_alpha(im, a)
    x, y = int(x), int(y)
    sx, sy = max(0, -x), max(0, -y)
    if sx or sy: im = im.crop((sx, sy, im.width, im.height)); x += sx; y += sy
    if x >= base.width or y >= base.height: return
    im = im.crop((0, 0, min(im.width, base.width - x), min(im.height, base.height - y)))
    base.alpha_composite(im, (x, y))

# ---------- レイアウト ----------
def build_layers(sc, fmt, channel):
    L = {}
    if fmt == "short":
        L["chan"] = text_block([channel], font(FONT_M, 40), 56)
        L["tag"] = pill(sc["tag"], font(FONT_B, 44), 84) if sc.get("tag") else None
        L["head"] = text_block(wrap_ja(sc.get("heading", ""), font(FONT_B, 84), 940), font(FONT_B, 84), 110)
        L["emoji"] = emoji_img(sc["emoji"], 400) if sc.get("emoji") else None
        L["cap"] = caption_box(sc["caption"], font(FONT_B, 60), 88, 860)
    else:
        L["chan"] = text_block([channel], font(FONT_M, 34), 48, align="left")
        L["tag"] = pill(sc["tag"], font(FONT_B, 44), 84) if sc.get("tag") else None
        L["head"] = text_block(wrap_ja(sc.get("heading", ""), font(FONT_B, 80), 1050), font(FONT_B, 80), 105, align="left")
        L["emoji"] = emoji_img(sc["emoji"], 420) if sc.get("emoji") else None
        L["cap"] = caption_box(sc["caption"], font(FONT_B, 54), 80, 1600)
    return L

def render_frame(base_bg, bub, L, fmt, t, T, prog, new_head, new_emoji):
    W, H = base_bg.size
    fr = base_bg.copy()
    off = int((t * 40 + prog * 3000) % H)  # 泡がゆっくり上へ
    fr.alpha_composite(bub.crop((0, off, W, off + H)))
    hk = ease_out(t / 0.45) if new_head else 1.0
    if fmt == "short":
        paste(fr, L["chan"], (W - L["chan"].width) // 2, 140)
        y = 230
        if L["tag"]:
            paste(fr, L["tag"], (W - L["tag"].width) // 2, y, hk); y += 110
        paste(fr, L["head"], (W - L["head"].width) // 2 - (1 - hk) * 120, y, hk)
        ecx, ecy = W // 2, 860
        cap_y = 1220
    else:
        paste(fr, L["chan"], 60, 40)
        if L["tag"]:
            paste(fr, L["tag"], 60 - (1 - hk) * 200, 120, hk)
        paste(fr, L["head"], 60 - (1 - hk) * 200, 240, hk)
        ecx, ecy = 1480, 400
        cap_y = H - 90 - L["cap"].height + 10
    if L["emoji"]:
        s = back_out(t / 0.5) if new_emoji else 1.0
        bob = math.sin(t * 2 * math.pi / 2.6) * 14
        ang = math.sin(t * 2 * math.pi / 3.4) * 4
        e = L["emoji"]
        if s < 0.999:
            e = e.resize((max(1, int(e.width * s)), max(1, int(e.height * s))), Image.BILINEAR)
        e = e.rotate(ang, resample=Image.BICUBIC, expand=True)
        paste(fr, e, ecx - e.width // 2, ecy - e.height // 2 + bob)
    ck = ease_out(t / 0.3)
    paste(fr, L["cap"], (W - L["cap"].width) // 2, cap_y + (1 - ck) * 40, ck)
    # 進行バー
    d = ImageDraw.Draw(fr)
    by = 0 if fmt == "short" else H - 12
    d.rectangle([0, by, W, by + 12], fill=(255, 255, 255, 120))
    d.rectangle([0, by, int(W * prog), by + 12], fill=INK)
    return fr.convert("RGB")

# ---------- 音声 ----------
def run(cmd):
    r = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    if r.returncode: raise RuntimeError(r.stderr.decode()[-2000:])

def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", p]).strip())

def tts_cached(text, voice, rate, cache):
    h = hashlib.md5(f"{voice}|{rate}|{text}".encode()).hexdigest()[:12]
    wav = f"{cache}/{h}.wav"
    if not os.path.exists(wav):
        mp3 = f"{cache}/{h}.mp3"
        for attempt in range(3):
            try:
                asyncio.run(edge_tts.Communicate(text, voice, rate=rate).save(mp3)); break
            except Exception:
                if attempt == 2: raise
        run(["ffmpeg", "-y", "-i", mp3, "-af", "apad=pad_dur=0.4", "-ar", "48000", "-ac", "2", wav])
    return wav

def make_bgm(seconds, seed, out):
    """ゆったりしたローファイ風BGMを合成(毎回コード進行・テンポ・音色が変わる)"""
    rnd = random.Random(seed); sr = 48000
    progs = [[0, 9, 5, 7], [5, 7, 4, 9], [0, 4, 9, 5], [9, 5, 0, 7], [2, 7, 0, 9]]
    prog = rnd.choice(progs); key = rnd.choice([0, 2, 3, 5, 7])
    bpm = rnd.choice([78, 84, 88, 92]); beat = 60 / bpm; bar = beat * 4
    n = int(seconds * sr) + sr; t = np.arange(n) / sr
    y = np.zeros(n)
    def note(f, start, length, amp, harm=(1, .5, .25)):
        i0 = int(start * sr); i1 = min(n, i0 + int(length * sr))
        if i0 >= n: return
        tt = np.arange(i1 - i0) / sr
        env = np.exp(-tt * 2.2) * np.minimum(1, tt * 60)
        w = sum(a * np.sin(2 * np.pi * f * k * tt + rnd.random()) for k, a in enumerate(harm, 1))
        y[i0:i1] += amp * env * w
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)
    nbars = int(seconds / bar) + 2
    for b in range(nbars):
        root = 48 + key + prog[b % 4]
        minor = prog[b % 4] in (9, 2, 4)
        chord = [0, 3 if minor else 4, 7, 10 if minor else 11, 14]
        for k, iv in enumerate(chord):  # 少しずらして弾くエレピ風
            note(hz(root + 12 + iv), b * bar + k * 0.03, bar * 0.95, 0.07)
        note(hz(root - 12), b * bar, bar * 0.9, 0.16, (1, .3))
        for q in range(4):
            st = b * bar + q * beat
            if q in (0, 2):  # キック
                i0 = int(st * sr); L = int(0.25 * sr)
                if i0 + L < n:
                    tt = np.arange(L) / sr
                    y[i0:i0 + L] += 0.35 * np.sin(2 * np.pi * (50 + 80 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 14)
            hs = int((st + beat / 2) * sr); L = int(0.05 * sr)  # ハイハット
            if hs + L < n:
                y[hs:hs + L] += 0.04 * np.random.default_rng(seed + b * 4 + q).standard_normal(L) * np.exp(-np.arange(L) / sr * 80)
            if rnd.random() < 0.35:  # メロディの合いの手
                note(hz(root + 24 + rnd.choice([0, 3 if minor else 4, 7, 12])), st + beat / 2, beat, 0.035, (1, .2))
    y = y / (np.abs(y).max() + 1e-9) * 0.8
    raw = out + ".raw"
    np.stack([y, y], 1).astype(np.float32).tofile(raw)
    run(["ffmpeg", "-y", "-f", "f32le", "-ar", str(sr), "-ac", "2", "-i", raw,
         "-af", f"lowpass=f=5200,atrim=0:{seconds:.2f},afade=t=in:d=1.5,afade=t=out:st={max(0, seconds - 2.5):.2f}:d=2.5",
         "-ar", "48000", out])
    os.remove(raw)

# ---------- 書き出し ----------
def render_video(scenes, fmt, s, outdir, name, seed, frames_only=False):
    W, H = (1080, 1920) if fmt == "short" else (1920, 1080)
    work = f"{outdir}/work_{name}"; cache = f"{outdir}/tts"
    os.makedirs(work, exist_ok=True); os.makedirs(cache, exist_ok=True)
    voice, rate = s.get("voice", "ja-JP-NanamiNeural"), s.get("rate", "+10%")
    if frames_only:
        durs = [6.0] * len(scenes); wavs = []
    else:
        wavs = [tts_cached(sc["say"], voice, rate, cache) for sc in scenes]
        durs = [dur(w) for w in wavs]
    total = sum(durs); elapsed = 0; parts = []; prev = {}
    for i, (sc, D) in enumerate(zip(scenes, durs)):
        theme = THEMES[sc.get("theme", i) % len(THEMES)]
        bg, bub = make_bg(W, H, theme, seed + sc.get("theme", i))
        L = build_layers(sc, fmt, s["channel"])
        new_head = sc.get("heading") != prev.get("heading") or sc.get("tag") != prev.get("tag")
        new_emoji = sc.get("emoji") != prev.get("emoji")
        prev = sc
        nfr = int(round(D * FPS))
        if frames_only:
            for tt in (0.15, 2.0):
                render_frame(bg, bub, L, fmt, tt, D, (elapsed + tt) / total, new_head, new_emoji).save(f"{work}/f{i:02d}_{tt}.jpg", quality=90)
            elapsed += D; continue
        tmp, mp4 = f"{work}/v{i:02d}.tmp.mp4", f"{work}/v{i:02d}.mp4"
        p = subprocess.Popen(["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                              "-i", "-", "-c:v", "libx264", "-crf", "20", "-preset", "veryfast", "-pix_fmt", "yuv420p",
                              tmp], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for k in range(nfr):
            tt = k / FPS
            p.stdin.write(render_frame(bg, bub, L, fmt, tt, D, (elapsed + tt) / total, new_head, new_emoji).tobytes())
        p.stdin.close()
        if p.wait(): raise RuntimeError(f"encode failed scene {i}")
        os.replace(tmp, mp4); parts.append(mp4); elapsed += nfr / FPS
    if frames_only: return
    with open(f"{work}/v.txt", "w") as f: f.writelines(f"file '{os.path.abspath(x)}'\n" for x in parts)
    with open(f"{work}/a.txt", "w") as f: f.writelines(f"file '{os.path.abspath(x)}'\n" for x in wavs)
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", f"{work}/v.txt", "-c", "copy", f"{work}/video.mp4"])
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", f"{work}/a.txt", "-c:a", "pcm_s16le", f"{work}/voice.wav"])
    vlen = dur(f"{work}/video.mp4")
    make_bgm(vlen, seed, f"{work}/bgm.wav")
    # BGMはナレーションに合わせて自動で下げる(サイドチェイン)
    run(["ffmpeg", "-y", "-i", f"{work}/voice.wav", "-i", f"{work}/bgm.wav", "-filter_complex",
         "[1:a]volume=0.22[b];[0:a]asplit[v1][v2];[b][v1]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=400[bd];"
         "[v2][bd]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.95[m]",
         "-map", "[m]", "-c:a", "pcm_s16le", f"{work}/mix.wav"])
    final = f"{outdir}/{s['slug']}_{name}.mp4"
    run(["ffmpeg", "-y", "-i", f"{work}/video.mp4", "-i", f"{work}/mix.wav", "-map", "0:v", "-map", "1:a",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", final + ".tmp.mp4"])
    os.replace(final + ".tmp.mp4", final)
    print(final, round(dur(final), 1), "sec")

def draw_thumb(s, outdir):
    t = s["thumbnail"]; W, H = 1280, 720
    bg, bub = make_bg(W, H, THEMES[0], 7)
    fr = bg.copy(); fr.alpha_composite(bub.crop((0, 0, W, H)))
    f = font(FONT_B, 92)
    lines = wrap_ja(t["text"], f, 760)
    d = ImageDraw.Draw(fr)
    y = 120
    if t.get("tag"):
        paste(fr, pill(t["tag"], font(FONT_B, 40), 76), 60, 40)
    for l in lines:
        for dx, dy in [(-5, 0), (5, 0), (0, -5), (0, 5), (-4, -4), (4, 4), (-4, 4), (4, -4)]:
            d.text((60 + dx, y + dy), l, font=f, fill=(255, 255, 255), anchor="lt")
        d.text((60, y), l, font=f, fill=INK, anchor="lt"); y += 118
    if t.get("sub"):
        paste(fr, caption_box(t["sub"], font(FONT_B, 46), 64, 700), 50, H - 180)
    e = emoji_img(t["emoji"], 380)
    paste(fr, e.rotate(-8, expand=True, resample=Image.BICUBIC), 860, 170)
    fr.convert("RGB").save(f"{outdir}/{s['slug']}_thumb.png")

def main(path, outdir, frames_only=False):
    s = json.load(open(path)); os.makedirs(outdir, exist_ok=True)
    seed = int(hashlib.md5(s["slug"].encode()).hexdigest()[:6], 16)
    for sc in s["scenes"]: sc.setdefault("caption", sc["say"])
    # 本編(横)
    if not SHORT_ONLY: render_video(s["scenes"], "long", s, outdir, "long", seed, frames_only)
    # ショート(縦) = 本編の1パートを切り出し＋冒頭フック＋本編への誘導
    sh = s["short"]
    seg = [dict(sc, tag=sh.get("tag", "今日の雑学"), say=sc.get("say_short", sc["say"]),
                caption=sc.get("caption_short", sc.get("say_short", sc["caption"])))
           for sc in s["scenes"] if sc.get("tag") == sh["segment"]]
    sscenes = [dict(sh["hook"], tag=sh.get("tag", "今日の雑学"), theme=seg[0].get("theme", 0))] + seg + \
              [dict(sh["outro"], tag=sh.get("tag", "今日の雑学"), theme=seg[0].get("theme", 0))]
    for sc in sscenes: sc.setdefault("caption", sc["say"])
    render_video(sscenes, "short", s, outdir, "short", seed + 1, frames_only)
    if frames_only: return
    draw_thumb(s, outdir)
    meta = {"long": {k: s[k] for k in ("title", "description", "tags")},
            "short": {k: sh[k] for k in ("title", "description", "tags")}}
    json.dump(meta, open(f"{outdir}/{s['slug']}_meta.json", "w"), ensure_ascii=False, indent=2)

SHORT_ONLY = "--short-only" in sys.argv
if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], frames_only="--frames" in sys.argv)
