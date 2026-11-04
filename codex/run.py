#!/usr/bin/env python3
"""Отправить один ракурс в Codex на генерацию картинки.

    python3 codex/run.py 04_int_living        # следующая версия: out/codex/04_int_living_v1.png, v2, ...
    python3 codex/run.py 06_int_hall_stair refs/hall_concept.png   # + доп. референсы для этого ракурса

Собирает промпт из codex/prompts.md (общий блок + стиль интерьера + блок ракурса),
прикладывает out/views/<ракурс>.png и все фото из refs/style/, запускает `codex exec`.
Промпт и ответ Codex сохраняются рядом с картинкой (.prompt.txt, .log.txt).
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROMPTS = ROOT / "codex" / "prompts.md"
OUT = ROOT / "out" / "codex"


def blocks(md):
    """Код-блоки по разделам: {'common': ..., 'style': ..., '<ракурс>': ...}."""
    res, sec = {}, None
    for part in re.split(r"^## ", md, flags=re.M)[1:]:
        title = part.splitlines()[0]
        m = re.search(r"`(\d\d_[a-z0-9_]+)`", title)
        sec = m.group(1) if m else ("common" if "Общий" in title else
                                    "bedroom_style" if "Спальни" in title else
                                    "bath_style" if "Санузлы" in title else
                                    "ext_style" if "Экстерьер" in title else
                                    "style" if "Стиль" in title else title)
        code = re.findall(r"```\n(.*?)```", part, flags=re.S)
        if code:
            res[sec] = code[0].strip()
    return res


def main():
    view = sys.argv[1]
    b = blocks(PROMPTS.read_text(encoding="utf-8"))
    if view not in b:
        sys.exit(f"нет промпта для {view} в {PROMPTS}")
    img = ROOT / "out" / "views" / f"{view}.png"
    if not img.exists():
        sys.exit(f"нет ракурса {img} — сначала make views ONLY={view[:2]}")
    style_imgs = sorted(p for p in (ROOT / "refs" / "style").glob("*")
                        if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")) if "_int_" in view else []
    common = b["common"]
    if not style_imgs:   # стилевых фото нет — убираем абзац про них
        common = re.sub(r"\n\nThe OTHER attached photos.*?layout\.", "", common, flags=re.S)
    body = "\n".join(l for l in b[view].splitlines() if not l.startswith("["))
    is_int = "_int_" in view
    OUT.mkdir(parents=True, exist_ok=True)
    n = 1
    while (OUT / f"{view}_v{n}.png").exists():
        n += 1
    target = OUT / f"{view}_v{n}.png"
    extra = ([b["bedroom_style"]] if "bedroom" in view and "bedroom_style" in b else []) + \
            ([b["bath_style"]] if "_bath" in view and "bath_style" in b else []) + \
            ([b["ext_style"]] if "_ext_" in view and "ext_style" in b else [])
    prompt = "\n\n".join([common] + ([b["style"]] if is_int else []) + extra + [body]) + (
        f"\n\nGenerate this image with your image generation tool and save the final image as PNG to "
        f"{target.relative_to(ROOT)} (create the folder if needed). Do not modify any other files. "
        f"When done, reply with the saved path only.")
    (OUT / f"{view}_v{n}.prompt.txt").write_text(prompt, encoding="utf-8")
    cmd = ["codex", "exec", "-C", str(ROOT), "-s", "workspace-write",
           "-o", str(OUT / f"{view}_v{n}.log.txt"), "-i", str(img)]
    extra_imgs = [ROOT / a for a in sys.argv[2:]]                  # доп. референсы ракурса — сразу после черновика
    for p in extra_imgs + style_imgs:
        cmd += ["-i", str(p)]
    cmd += ["--", prompt]
    print("ракурс:", img.relative_to(ROOT), "| доп. реф:", len(extra_imgs), "| стилевых фото:", len(style_imgs), "| цель:", target.relative_to(ROOT))
    r = subprocess.run(cmd)
    print("готово" if target.exists() else f"картинка не появилась в {target.relative_to(ROOT)}, код {r.returncode}")


if __name__ == "__main__":
    main()
