"""採用した貼り写真を render-assets-matome/scene_NN_beat{slot}.* として配置する。

  .venv\\Scripts\\python.exe scripts/20260911-matome-dansei-kamishibai/stage_assets.py

apply_beats.py の BEATS と SOURCE_FILE を読み、image ビートの (シーン, スロット) に対応する
候補ファイルをコピーする。候補は Git 管理外（assets-kamishibai）なので、このスクリプトが
「どの候補を採用したか」の記録も兼ねる。採用元は candidates-matome の
manifest-s01-s07.md / manifest-s08-s14.md の**推奨**。
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from apply_beats import BEATS, SOURCE_FILE  # noqa: E402

SRC = Path(r"C:\Users\shuya\Projects\assets-kamishibai\photos\candidates-matome")
DST = Path(r"C:\Users\shuya\Projects\assets-kamishibai\render-assets-matome")


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    n = 0
    missing: list[str] = []
    used: dict[str, list[str]] = {}
    for sid, beats in BEATS.items():
        slot = 0  # apply_beats.main と同じ通し番号（img() の slot 引数は使わない）
        for kind, _anchor, _slot, ckey, _why, _telop in beats:
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
        raise SystemExit("\n".join(missing))
    print(f"staged {n} files -> {DST}")
    for ckey in sorted(used, key=lambda k: SOURCE_FILE[k]):
        print(f"  {SOURCE_FILE[ckey]:<34} {ckey:<18} {' '.join(used[ckey])}")


if __name__ == "__main__":
    main()
