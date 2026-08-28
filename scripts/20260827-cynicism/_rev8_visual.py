# -*- coding: utf-8 -*-
"""rev8: v4 の自動映像レビュー（大きな間違いのみ）採用分。
- 7:6 酸っぱい葡萄: cut_reason は「ナレーション自身が口にする比喩」なのにプロンプトがプラカードだった → 狐と葡萄の直接描写に
- 9:5 芥子畑の引き: 背景に古代遺跡が出る → 遺跡・建物なしを明示
- 12:9 は画像ファイル側の誤り（CRT が入っている）なので YAML は変えず再生成のみ
"""
import yaml
from pathlib import Path
p = Path(r"C:\Users\shuya\Projects\draft-explanation-video\scripts\20260827-cynicism\20260827-cynicism.yaml")
s = p.read_text(encoding="utf-8")
d = yaml.safe_load(s)
NEW = {
    (7, 6): "a red fox standing on its hind legs beneath a rustic grapevine trellis, looking up at a bunch of dark grapes hanging just out of reach, seen from the side, soft late-afternoon light in a quiet orchard, no people, no text, no lettering",
    (9, 5): "a wide view of the full field of red poppies stretching to a flat empty horizon, the one taller poppy now small within the larger field, soft morning light, open countryside with no buildings, no ruins, no ancient architecture, no text, no people, no lettering",
}
n = 0
for sc in d["scenes"]:
    for b in sc.get("beats", []):
        key = (sc["id"], b.get("slot"))
        if key in NEW and b.get("type") == "image":
            old = b["gen_prompt"]
            assert s.count(f'gen_prompt: "{old}"') == 1, key
            s = s.replace(f'gen_prompt: "{old}"', f'gen_prompt: "{NEW[key]}"', 1)
            n += 1
assert n == 2, n
p.write_text(s, encoding="utf-8")
print("prompts replaced", n)
