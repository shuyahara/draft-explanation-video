"""採用した貼り写真を render-assets-comparison/scene_NN_beat{slot}.* として配置する。

  .venv\\Scripts\\python.exe scripts/20260913-comparison-kamishibai/stage_assets.py

apply_beats.py の BEATS と SOURCE_FILE を読み、image ビートの (シーン, スロット) に対応する
候補ファイルをコピーする。候補は Git 管理外（assets-kamishibai）なので、このスクリプトが
「どの候補を採用したか」の記録も兼ねる。採用元は candidates-comparison/stock/ の
素材メモ.md（2026-09-13。各アンカーの「推奨」候補）。

見つからなかった3アンカーの判断（2026-09-13 コーディネーター指示）:
  - S4 表彰台（無人の表彰台。podium_a を採用）
  - S8 タイマー（タイマー単独で可。stopwatch 画面の timer_b を採用）
  - S8 ランニング（後ろ姿単独で可。running_c を採用）
S3 の MRI 写真（mri_a）は CT の可能性があるが汎用の検査装置カットとして採用。
S1 の時計は薬瓶が写らない方（clock_b）を採用していたが、clock_b の表示（4:12）がテロップ
「3時まで眠れなかった」と食い違うため、2026-09-13 に clock_c（3:33表示）へ差し替え（Issue #38）。

候補ファイルが見つからない場合は**警告して続行**する（素材収集と YAML 組み立てを並行する
ことがあるため。レンダ前に preflight の「素材ファイル」チェックで取りこぼしを拾う）。

配置前に `scene_*_beat*.*` をいったん全部消すので、ビート構成を変えても古い残骸は残らない。
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from apply_beats import BEATS, SOURCE_FILE  # noqa: E402

SRC = Path(r"C:\Users\shuya\Projects\assets-kamishibai\photos\candidates-comparison")
DST = Path(r"C:\Users\shuya\Projects\assets-kamishibai\render-assets-comparison")


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
        print(f"  {SOURCE_FILE[ckey]:<28} {ckey:<16} {' '.join(used[ckey])}")


if __name__ == "__main__":
    main()
