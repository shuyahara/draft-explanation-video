# -*- coding: utf-8 -*-
"""rev6: v2 の自動映像レビュー（GPT）採用分を YAML に反映。
- 特定 slot の gen_prompt を差し替え（画とナレーションの不一致・含意・白紙の徹底）
- シーン11 の converge 図解ラベル「共感が回復しない」→「共感が高まらない」
- シーン12 の telop を rev4 の文言に合わせる
"""
import io, re, yaml
from pathlib import Path

p = Path(r"C:\Users\shuya\Projects\draft-explanation-video\scripts\20260827-cynicism\20260827-cynicism.yaml")
s = p.read_text(encoding="utf-8")
d = yaml.safe_load(s)

MOD = "present-day scene, "
TAIL = ", no ancient architecture, no columns, no ruins, no historical costume"
NEW = {
    (4, 1): "ancient Greece, 4th century BC: a man in a rough cloak sitting on the ground of a sunlit market in front of well-dressed citizens, a lean stray dog lying beside him, seen from behind, warm stone tones, painterly, no faces, no lettering",
    (5, 3): MOD + "a street volunteer in a bright vest standing upright and holding a small collection box with a coin slot, passers-by walking past without looking, all seen from behind, no faces, daytime city street, no lettering" + TAIL,
    (5, 6): MOD + "two people standing strictly back to back in the middle of a city sidewalk, each facing away from the other and away from a blank white poster on a wall behind them, seen from the side, no faces, daytime, no lettering" + TAIL,
    (7, 4): MOD + "seen from behind: young people walking past an outdoor notice board on a Japanese street without stopping, the board holds only empty plain white sheets of paper, absolutely no photos, no faces, no print, overcast daylight, no lettering" + TAIL,
    (7, 5): MOD + "close view of an outdoor notice board holding rows of completely blank white sheets of paper, no photos, no portraits, no print at all, the back of one passer-by blurred in the foreground, overcast daylight, no lettering" + TAIL,
    (7, 6): MOD + "seen from behind: a pedestrian in ordinary light clothing walking briskly past a person in ordinary casual clothes who holds up a completely blank white placard on a city street, no phones, no faces visible, no print on the placard, daytime, no lettering" + TAIL,
    (9, 2): MOD + "a participant watching a monitor in a small lab room, seen from behind, the monitor shows only the blurred back and shoulders of an interviewee, no faces anywhere, neutral light, no lettering" + TAIL,
    (10, 4): MOD + "seen from behind: a street volunteer in a bright vest holding a collection box with a visible coin slot, an armband on the sleeve, while blurred passers-by walk past without looking, no faces, daytime city street, no lettering" + TAIL,
    (11, 6): MOD + "a long conference table seen from behind the far end: a person of indeterminate gender sits at the very end seat at the edge of the frame while another person at the head of the table leads the meeting, all seen from behind, no faces, cool office light, no lettering" + TAIL,
    (12, 1): MOD + "a modern television news studio with an empty anchor desk and chairs, clean minimal set, cool blue-white studio lighting, no people, no historical decor, no lettering" + TAIL,
}
n = 0
for sc in d["scenes"]:
    for b in sc.get("beats", []):
        key = (sc["id"], b.get("slot"))
        if key in NEW and b.get("type") == "image":
            old = b["gen_prompt"]
            c = s.count(f'gen_prompt: "{old}"')
            assert c >= 1, key
            s = s.replace(f'gen_prompt: "{old}"', f'gen_prompt: "{NEW[key]}"', 1)
            n += 1
print("prompts replaced", n)

# diagram label
assert "text: 共感が回復しない" in s
s = s.replace("text: 共感が回復しない", "text: 共感が高まらない")
# telop scene 12
old_t = 'telop: "日本は「不信の国」ではなく「無力感の国」"'
assert old_t in s
s = s.replace(old_t, 'telop: "不信よりも、無力感"')
p.write_text(s, encoding="utf-8")
print("ok")
