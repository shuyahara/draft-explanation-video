#!/usr/bin/env python3
"""対話形式の台本 Markdown（めたん×ずんだもん）を script-to-video の
紙芝居モードのシーン YAML に変換する。

変換対象: narration（読み上げ・話者・表情・pause_after）／ readings（v5 YAML から
同じシーン番号のものを転記）／ chapter_title ／ characters 定義。
ビート（beats。貼り写真・テロップ）は今回は作らない（別工程で人が置く）。

使い方:
    python tools/kamishibai_md_to_yaml.py <台本md> --v5-yaml <v5のyaml> --out <出力yaml>
"""
from __future__ import annotations

import argparse

PAUSE_PRESETS = {
    "1.0": {"speaker_change": 0.4, "sentence": 0.35, "scene_end": 1.0, "explicit_scale": 1.0},
    "1.1": {"speaker_change": 0.45, "sentence": 0.35, "scene_end": 1.2, "explicit_scale": 1.0},
}
PAUSES = PAUSE_PRESETS["1.0"]
import re
import sys
from pathlib import Path

import yaml

SPEAKERS = ("めたん", "ずんだもん")

SCENE_HEADER_RE = re.compile(r"^##\s*シーン(\d+):\s*(.+?)\s*$")
SOURCE_LIST_RE = re.compile(r"^##\s*出典リスト")
DIALOGUE_RE = re.compile(r"^\*\*(めたん|ずんだもん)\*\*（([^）]+)）:\s*(.*)$")
PAUSE_MARK_RE = re.compile(r"(.*?)\s*（間\s*([\d.]+)）\s*$")
CHAPTER_CARD_RE = re.compile(r"^-\s*章カード[:：]\s*「(.+)」\s*$")

# キャラクター定義（Issue #23 / タスク指示のとおり固定）
CHARACTERS = [
    {
        "name": "めたん",
        "speaker": "四国めたん",
        "sprites_dir": "C:/Users/shuya/Projects/assets-kamishibai/sprites/metan",
        "side": "left",
        "subtitle_color": "#E8A0BE",
        "default_expression": "normal",
    },
    {
        "name": "ずんだもん",
        "speaker": "ずんだもん",
        "sprites_dir": "C:/Users/shuya/Projects/assets-kamishibai/sprites/zundamon",
        "side": "right",
        "subtitle_color": "#8FCF7A",
        "default_expression": "normal",
    },
]


class Q(str):
    """このサブタイプでラップした文字列は、常に1行のダブルクォートスカラーとして出力する
    （折りたたみスカラーによる不可視スペース混入を避けるため。docs/schema.md の注意書き）。"""


def _q_representer(dumper: yaml.Dumper, data: "Q"):
    return dumper.represent_scalar("tag:yaml.org,2002:str", str(data), style='"')


yaml.add_representer(Q, _q_representer)


class IndentDumper(yaml.Dumper):
    """ブロックシーケンスの要素を親キーより2段深く字下げする（PyYAML の既定は字下げなし。
    プロジェクト内の既存 YAML（kamishibai-sample.yaml・v5 の dopagaki.yaml）の見た目に合わせる）。"""

    def increase_indent(self, flow: bool = False, indentless: bool = False):
        return super().increase_indent(flow, False)


def parse_markdown(md_path: Path):
    """台本 md をパースし、(video_title, scenes) を返す。

    scenes は [{"id", "title", "chapter_title", "narration": [...]}] のリスト。
    """
    lines = md_path.read_text(encoding="utf-8").splitlines()

    title = None
    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            break
    if title is None:
        raise ValueError("H1 タイトル行（# ...）が見つかりません")

    # シーン境界を収集（出典リスト見出しを終端の番兵として使う）
    boundaries: list[tuple[int, int | None, str | None]] = []
    for i, line in enumerate(lines):
        m = SCENE_HEADER_RE.match(line)
        if m:
            boundaries.append((i, int(m.group(1)), m.group(2)))
        elif SOURCE_LIST_RE.match(line):
            boundaries.append((i, None, None))
            break

    scenes = []
    for idx, (start_i, scene_id, scene_title) in enumerate(boundaries):
        if scene_id is None:
            continue
        end_i = boundaries[idx + 1][0] if idx + 1 < len(boundaries) else len(lines)
        block = lines[start_i + 1 : end_i]

        screen_i = None
        for j, l in enumerate(block):
            if l.strip() == "**画面**":
                screen_i = j
                break
        dialogue_lines = block[:screen_i] if screen_i is not None else block
        screen_lines = block[screen_i:] if screen_i is not None else []

        raw_entries: list[list] = []  # [speaker, expression, text, explicit_pause]
        for l in dialogue_lines:
            l = l.strip()
            if not l:
                continue
            m = DIALOGUE_RE.match(l)
            if not m:
                continue
            speaker, expr, body = m.group(1), m.group(2), m.group(3)
            pause_m = PAUSE_MARK_RE.match(body)
            explicit_pause = None
            if pause_m:
                body = pause_m.group(1)
                explicit_pause = float(pause_m.group(2))
            body = body.strip()
            if not body:
                raise ValueError(f"シーン{scene_id}: 本文が空の発話行があります: {l!r}")
            raw_entries.append([speaker, expr, body, explicit_pause])

        if not raw_entries:
            raise ValueError(f"シーン{scene_id}: 発話行が1件も見つかりませんでした")

        narration = []
        n = len(raw_entries)
        for k, (speaker, expr, body, explicit_pause) in enumerate(raw_entries):
            if explicit_pause is not None:
                pause = round(explicit_pause * PAUSES["explicit_scale"], 2)
            elif k == n - 1:
                pause = PAUSES["scene_end"]
            else:
                next_speaker = raw_entries[k + 1][0]
                pause = PAUSES["speaker_change"] if next_speaker != speaker else PAUSES["sentence"]
            narration.append(
                {
                    "text": Q(body),
                    "speaker": Q(speaker),
                    "expression": Q(expr),
                    "pause_after": pause,
                }
            )

        chapter_title = None
        for l in screen_lines:
            m = CHAPTER_CARD_RE.match(l.strip())
            if m:
                chapter_title = m.group(1)
                break

        scenes.append(
            {
                "id": scene_id,
                "title": scene_title,
                "chapter_title": chapter_title,
                "narration": narration,
            }
        )

    return title, scenes


def load_v5_readings(v5_path: Path) -> dict[int, list[tuple[str, str]]]:
    """v5 シーン YAML から、シーンID -> [(surface, reading), ...] を読み取る。"""
    with v5_path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    result: dict[int, list[tuple[str, str]]] = {}
    for sc in data.get("scenes", []):
        rs = sc.get("readings")
        if rs:
            result[sc["id"]] = [(r["surface"], r["reading"]) for r in rs]
    return result


def attach_readings(scenes: list[dict], v5_readings: dict[int, list[tuple[str, str]]]):
    """同じシーン番号の v5 readings を転記する。ただし新台本のそのシーン本文に
    表記が出てこないものは除く。"""
    for sc in scenes:
        candidates = v5_readings.get(sc["id"], [])
        scene_text = "".join(seg["text"] for seg in sc["narration"])
        kept = [(s, r) for s, r in candidates if s in scene_text]
        if kept:
            sc["readings"] = [{"surface": Q(s), "reading": Q(r)} for s, r in kept]


def build_yaml(title: str, scenes: list[dict], bgm=None, bgm_credit=None, puppet_sink=None) -> dict:
    video = {
        "title": Q(title),
        "kamishibai": ({"puppet_sink_ratio": puppet_sink} if puppet_sink else {}),
        "characters": [
            {
                "name": Q(c["name"]),
                "speaker": Q(c["speaker"]),
                "sprites_dir": Q(c["sprites_dir"]),
                "side": Q(c["side"]),
                "subtitle_color": Q(c["subtitle_color"]),
                "default_expression": Q(c["default_expression"]),
            }
            for c in CHARACTERS
        ],
        "bgm": Q(bgm) if bgm else None,
        "bgm_credit": Q(bgm_credit) if bgm_credit else None,
        "sfx": Q("chic"),
    }

    out_scenes = []
    for sc in scenes:
        entry = {
            "id": sc["id"],
            "title": Q(sc["title"]),
            "chapter_title": Q(sc["chapter_title"]) if sc["chapter_title"] else None,
            "narration": sc["narration"],
        }
        if sc.get("readings"):
            entry["readings"] = sc["readings"]
        out_scenes.append(entry)

    return {"video": video, "scenes": out_scenes}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("md_path", type=Path, help="対話形式の台本 Markdown")
    ap.add_argument("--v5-yaml", type=Path, required=True, help="readings 転記元の v5 シーン YAML")
    ap.add_argument("--out", type=Path, required=True, help="出力先の紙芝居モード YAML")
    ap.add_argument("--bgm", default=None, help="video.bgm に書く BGM パス（YAML からの相対。例: ../bgm/aozora-ni-kuchibue.mp3）")
    ap.add_argument("--bgm-credit", default=None, help="video.bgm_credit に書くクレジット文字列")
    ap.add_argument("--puppet-sink", type=float, default=None, help="video.kamishibai.puppet_sink_ratio（人形を字幕帯の裏へ沈める比。推奨 0.12）")
    ap.add_argument(
        "--tempo",
        choices=["1.0", "1.1"],
        default="1.0",
        help="想定話速。1.1 のときは間を一段長くする（話者交代 0.45・文境界 0.35・章末 1.2・（間 N）は台本の値どおり（決め文は 2.0 を推奨、間レビュー 2026-09-05）。docs/narration-style.md の 1.1 倍速ルール）",
    )
    args = ap.parse_args()

    global PAUSES
    PAUSES = PAUSE_PRESETS[args.tempo]
    title, scenes = parse_markdown(args.md_path)
    v5_readings = load_v5_readings(args.v5_yaml)
    attach_readings(scenes, v5_readings)
    data = build_yaml(title, scenes, bgm=args.bgm, bgm_credit=args.bgm_credit, puppet_sink=args.puppet_sink)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8", newline="\n") as f:
        yaml.dump(
            data,
            f,
            Dumper=IndentDumper,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
            width=1_000_000,
        )

    total_segments = sum(len(sc["narration"]) for sc in scenes)
    speaker_counts = {"めたん": 0, "ずんだもん": 0}
    pause_counts: dict[float, int] = {}
    for sc in scenes:
        for seg in sc["narration"]:
            speaker_counts[str(seg["speaker"])] += 1
            pause_counts[seg["pause_after"]] = pause_counts.get(seg["pause_after"], 0) + 1

    print(f"wrote {args.out}")
    print(f"scenes: {len(scenes)}")
    print(f"total narration segments: {total_segments}")
    print(f"speaker breakdown: {speaker_counts}")
    print(f"pause_after distribution: {sorted(pause_counts.items())}")
    readings_summary = {sc['id']: len(sc.get('readings', [])) for sc in scenes}
    print(f"readings per scene: {readings_summary}")
    chapters = {sc['id']: sc['chapter_title'] for sc in scenes if sc['chapter_title']}
    print(f"chapter_title scenes: {chapters}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
