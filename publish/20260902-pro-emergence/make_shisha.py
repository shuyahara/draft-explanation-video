"""試写室ページ生成: レンダ出力を3パートに軽量エンコードし、base64 埋め込みの HTML を作る。

  .venv\\Scripts\\python.exe publish/20260902-pro-emergence/make_shisha.py --build pro-emergence-v3 --label v3
  （--links で公開後の各パートURLをカンマ区切りで渡すとナビが本物のリンクになる）
"""
from __future__ import annotations

import argparse
import base64
import html
import json
import subprocess
from pathlib import Path

S2V = Path(r"C:\Users\shuya\Projects\script-to-video")
OUT = Path(__file__).resolve().parent / "shisha"
TITLE = "なぜ将棋やスポーツには「プロ」が生まれるのか"
# パート分割（シーン番号の範囲）と短い章名
PARTS = [
    ("パート1", (1, 5), "フック〜フットボールのプロ容認"),
    ("パート2", (6, 9), "アマチュアリズムの正体〜楽譜と著作権"),
    ("パート3", (10, 14), "ローゼン〜払う仕組みの起源・結論"),
]
SCENE_LABELS = {
    1: "フック（深夜の配信者）", 2: "問題提起（三つの説）", 3: "将棋のプロは、誰が作ったのか",
    4: "断絶と再生（幕府→新聞）", 5: "スポーツでも、同じことが起きたのか", 6: "反転（アマチュアリズムの正体）",
    7: "説②の検討（ウィレンスキー）", 8: "音楽家は、いつ使用人でなくなったのか", 9: "楽譜・著作権・画商",
    10: "説③の検討（ローゼンとアドラー）", 11: "反証と留保（コスト病）", 12: "三つの説の、どれが正しいのか",
    13: "払う仕組みは、なぜ生まれるのか", 14: "結論（冒頭の配信者へ戻る）",
}


def mmss(sec: float) -> str:
    sec = int(sec)
    return f"{sec // 60}:{sec % 60:02d}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", required=True, help="build ディレクトリ名（例 pro-emergence-v3）")
    ap.add_argument("--label", required=True, help="表示用バージョン（例 v3）")
    ap.add_argument("--links", default="", help="公開後の各パートURL（カンマ区切り、3件）")
    ap.add_argument("--date", default="2026-09-03")
    ap.add_argument("--note", default="")
    args = ap.parse_args()

    bdir = S2V / "build" / args.build
    mp4 = bdir / f"{args.build}.mp4"
    assert mp4.exists(), mp4
    tl = json.loads((bdir / "timeline.json").read_text(encoding="utf-8"))
    scenes = {int(e["scene_id"]): (float(e["start"]), float(e["end"])) for e in tl["entries"] if e.get("kind") == "scene"}
    total = float(tl["total_duration"])
    links = [s.strip() for s in args.links.split(",")] if args.links else ["", "", ""]
    OUT.mkdir(exist_ok=True)

    for idx, (pname, (s0, s1), pdesc) in enumerate(PARTS):
        start = scenes[s0][0]
        end = total if s1 == max(scenes) else scenes[s1 + 1][0]
        clip = OUT / f"{args.build}-part{idx + 1}.mp4"
        subprocess.run([
            "ffmpeg", "-v", "error", "-y", "-ss", f"{start:.3f}", "-i", str(mp4), "-t", f"{end - start:.3f}",
            "-vf", "scale=640:360", "-r", "24", "-c:v", "libx264", "-preset", "veryfast", "-crf", "30",
            "-c:a", "aac", "-b:a", "48k", "-ac", "1", "-movflags", "+faststart", str(clip),
        ], check=True)
        b64 = base64.b64encode(clip.read_bytes()).decode("ascii")
        toc = "".join(
            f'<li><button type="button" data-t="{scenes[i][0] - start:.2f}"><span class="t">{mmss(scenes[i][0] - start)}</span>'
            f'<span class="n">シーン{i}</span>{html.escape(SCENE_LABELS[i])}</button></li>'
            for i in range(s0, s1 + 1)
        )
        nav = "".join(
            (f'<span class="here">{PARTS[j][0]}（{html.escape(PARTS[j][2])}）</span>' if j == idx else
             (f'<a href="{links[j]}">{PARTS[j][0]}（{html.escape(PARTS[j][2])}）</a>' if links[j] else
              f'<span class="soon">{PARTS[j][0]}（{html.escape(PARTS[j][2])}）</span>'))
            for j in range(3)
        )
        note = f'<p class="lead">{html.escape(args.note)}</p>' if args.note else ""
        page = f"""<title>プロ発生論 試写室 {pname}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{{--bg:#14161A;--panel:#1D2025;--ink:#ECE9E2;--ink2:#B9B4A8;--muted:#807A6E;--rule:#2C3036;--accent:#C2A970;--sans:"Noto Sans JP","Hiragino Sans",sans-serif;--mono:"IBM Plex Mono",Consolas,monospace}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);font-size:15px;line-height:1.75}}
.wrap{{max-width:900px;margin:0 auto;padding:32px 20px 70px}}
.grad{{height:3px;background:linear-gradient(90deg,var(--accent) 0 45%,#4B6F90 55% 100%);margin-bottom:22px}}
.eyebrow{{font-size:11.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin:0 0 10px;font-family:var(--mono)}}
h1{{font-weight:600;font-size:clamp(22px,3vw,30px);line-height:1.4;margin:0 0 6px;text-wrap:balance}}
.sub{{color:var(--ink2);margin:0 0 18px;font-size:14px}}
.nav{{display:flex;flex-wrap:wrap;gap:8px 18px;font-size:13px;margin:0 0 20px}}
.nav a{{color:var(--accent);text-decoration:none;border-bottom:1px solid transparent}}
.nav a:hover,.nav a:focus-visible{{border-bottom-color:var(--accent);outline:none}}
.nav .here{{color:var(--ink);border-bottom:2px solid var(--accent)}}
.nav .soon{{color:var(--muted)}}
dl.meta{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px 22px;padding:16px 0;border-top:1px solid var(--rule);border-bottom:1px solid var(--rule);font-size:13px;margin:0 0 26px}}
dl.meta dt{{color:var(--muted);font-size:11px;letter-spacing:.1em;text-transform:uppercase}}
dl.meta dd{{margin:0;overflow-wrap:anywhere;font-variant-numeric:tabular-nums}}
h2{{font-weight:600;font-size:18px;margin:32px 0 10px}}
.lead{{color:var(--ink2);font-size:13.5px;margin:0 0 16px;max-width:70ch}}
video{{width:100%;max-width:820px;background:#000;display:block;border-radius:4px}}
.toc{{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:8px}}
.toc button{{all:unset;cursor:pointer;display:flex;align-items:baseline;gap:12px;width:100%;padding:10px 14px;background:var(--panel);border:1px solid var(--rule);font-size:13.5px;color:var(--ink)}}
.toc button:hover,.toc button:focus-visible{{border-color:var(--accent);color:var(--accent)}}
.toc .t{{font-family:var(--mono);color:var(--muted);font-size:12px;min-width:3.5em;font-variant-numeric:tabular-nums}}
.toc .n{{color:var(--muted);font-size:12px;min-width:5em}}
.fb{{margin-top:34px;padding:16px 18px;border:1px solid var(--rule);background:var(--panel);font-size:13.5px;color:var(--ink2)}}
.fb b{{color:var(--ink);font-weight:600}}
</style>
<div class="wrap">
<div class="grad"></div>
<p class="eyebrow">試写 ／ {html.escape(args.build)} ／ {pname} ／ {html.escape(args.date)}</p>
<h1>{html.escape(TITLE)}</h1>
<p class="sub">{pname}（全編 {mmss(start)}〜{mmss(end)} ・ このパート {mmss(end - start)}）</p>
<nav class="nav">{nav}</nav>
<p class="lead">全編 {mmss(total)} を3パートに分割しています。このページはシーン{s0}〜{s1}（{html.escape(pdesc)}）。</p>
{note}
<dl class="meta">
<div><dt>範囲</dt><dd>{mmss(start)}〜{mmss(end)}（全編中）</dd></div>
<div><dt>版</dt><dd>{html.escape(args.label)}</dd></div>
<div><dt>仕様</dt><dd>640×360・24fps・CRF30・音声AAC 48kbps モノラル（表示用の軽量エンコード。本編は1920×1080）</dd></div>
</dl>
<video controls preload="metadata" playsinline src="data:video/mp4;base64,{b64}"></video>
<h2>このパートの目次</h2>
<p class="lead">クリックでこのパート内の該当箇所へシークします。</p>
<ul class="toc">{toc}</ul>
<div class="fb"><b>フィードバックの書き方</b>: 「シーン番号＋パート内の時刻」で指摘してもらえると、該当ビートを特定して直せます（例: シーン6 の 2:10、字幕が早い）。</div>
<nav class="nav">{nav}</nav>
</div>
<script>
document.querySelectorAll('.toc button').forEach(function(b){{b.addEventListener('click',function(){{var v=document.querySelector('video');v.currentTime=parseFloat(b.dataset.t);v.play();}});}});
</script>
"""
        (OUT / f"shisha-part{idx + 1}.html").write_text(page, encoding="utf-8")
        print(f"{pname}: {mmss(start)}-{mmss(end)} clip={clip.stat().st_size / 1048576:.1f}MiB html={(OUT / f'shisha-part{idx + 1}.html').stat().st_size / 1048576:.1f}MiB")


if __name__ == "__main__":
    main()
