"""採用した貼り写真を render-assets-matome/scene_NN_beat{slot}.* として配置する（v7・10シーン）。

  .venv\\Scripts\\python.exe scripts/20260911-matome-dansei-kamishibai/stage_assets.py

apply_beats.py の BEATS と SOURCE_FILE を読み、image ビートの (シーン, スロット) に対応する
候補ファイルをコピーする。候補は Git 管理外（assets-kamishibai）なので、このスクリプトが
「どの候補を採用したか」の記録も兼ねる。採用元は candidates-matome の
manifest-s01-s07.md / manifest-s08-s14.md（v4 で追加した S6・S9 の新規分は後者の末尾
「v4 追加分」、v7 で追加した S7 の `s15_*` は references/20260912-s7-photo-credits.md）。

候補ファイルが見つからない場合は**警告して続行**する（素材収集と YAML 組み立てを並行する
ことがあるため。レンダ前に preflight の「素材ファイル」チェックで取りこぼしを拾う）。

配置前に `scene_*_beat*.*` をいったん全部消すので、v3（14シーン）の scene_10〜scene_14 など
古い残骸は残らない。
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
    # 割り当てを変えるとスロット数や拡張子が変わるので、毎回いったん空にしてから配置する
    # （古い scene_NN_beatM.png が残ると、同じスロットの .jpg と二重になる）。
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
        raise SystemExit("\n".join(missing))
    print(f"staged {n} files -> {DST}")
    for ckey in sorted(used, key=lambda k: SOURCE_FILE[k]):
        print(f"  {SOURCE_FILE[ckey]:<34} {ckey:<18} {' '.join(used[ckey])}")


if __name__ == "__main__":
    main()
