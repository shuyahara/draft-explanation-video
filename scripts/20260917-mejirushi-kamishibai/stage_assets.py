"""採用した貼り写真を render-assets-mejirushi/scene_NN_beat{slot}.* として配置する。

  .venv\\Scripts\\python.exe scripts/20260917-mejirushi-kamishibai/stage_assets.py

apply_beats.py の BEATS と SOURCE_FILE を読み、image ビートの (シーン, スロット) に対応する
候補ファイルをコピーする。候補は Git 管理外（assets-kamishibai）なので、このスクリプトが
「どの候補を採用したか」の記録も兼ねる。採用元は candidates-mejirushi/{gen,stock}/ の
素材メモ.md（2026-09-17）。ストックの選定理由は apply_beats.py 冒頭の設計メモを参照。

候補ファイルが見つからない場合は**警告して続行**する（レンダ前に preflight の
「素材ファイル」チェックで取りこぼしを拾う）。

配置前に `scene_*_beat*.*` をいったん全部消すので、ビート構成を変えても古い残骸は残らない。
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from apply_beats import BEATS, SOURCE_FILE  # noqa: E402

SRC = Path(r"C:\Users\shuya\Projects\assets-kamishibai\photos\candidates-mejirushi")
DST = Path(r"C:\Users\shuya\Projects\assets-kamishibai\render-assets-mejirushi")


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    for old in DST.glob("scene_*_beat*.*"):
        old.unlink()
    n = 0
    missing: list[str] = []
    used: dict[str, list[str]] = {}
    for sid, beats in BEATS.items():
        slot = 0  # apply_beats.main と同じ通し番号（img() の slot 引数は使わない）
        for beat in beats:
            kind, ckey = beat[0], beat[3]
            if kind != "image":
                continue
            slot += 1
            rel = SOURCE_FILE.get(ckey)
            if rel is None:
                missing.append(f"scene {sid} slot {slot}: SOURCE_FILE に {ckey} がありません（未配置）")
                continue
            src = SRC / rel
            if not src.exists():
                missing.append(f"scene {sid} slot {slot}: {src} が見つかりません（未配置）")
                continue
            dst = DST / f"scene_{sid:02d}_beat{slot}{src.suffix}"
            shutil.copyfile(src, dst)
            used.setdefault(ckey, []).append(f"S{sid}-{slot}")
            n += 1
    if missing:
        print("\n".join(missing))
        raise SystemExit(f"{len(missing)} 件未配置（上記参照）")
    print(f"staged {n} files -> {DST}")
    for ckey in sorted(used, key=lambda k: SOURCE_FILE[k]):
        print(f"  {SOURCE_FILE[ckey]:<32} {ckey:<12} {' '.join(used[ckey])}")


if __name__ == "__main__":
    main()
