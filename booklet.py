#!/usr/bin/env python3
"""Собрать клиентский PDF-буклет из плана и принятых рендеров."""
from io import BytesIO
from pathlib import Path
import json
import os
import re
import subprocess
from tempfile import TemporaryDirectory

import plan

from PIL import Image
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph

W, H = landscape(A4)
M = 38
C = W - M * 2
PAPER = "#F7F3EB"
INK = "#252A24"
DIM = "#5F6559"
GREEN = "#4C5743"
CLAY = "#9C4A34"
RULE = "#CFC8BA"
WHITE = "#FFFFFF"


PROJECT_NAME = "Занковичи"
PAGE_COUNT = 11
ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "output" / "pdf" / "zankovici-design-booklet.pdf"

def render_plans(directory):
    """Подготовить крупные фрагменты SVG с размерными линиями обоих этажей."""
    svg = (ROOT / "out" / "plan.svg").read_text(encoding="utf-8")
    height = round(plan.OY * plan.S) + 106
    y = plan.HEAD + plan.MARGIN - 14
    node = os.environ.get("BOOKLET_NODE", "node")
    rasterize = """
const fs = require('node:fs');
const sharp = require('sharp');
sharp(fs.readFileSync(0), {density: 216})
  .flatten({background: '#ffffff'})
  .png().toFile(process.argv[1])
  .catch(error => { console.error(error); process.exitCode = 1; });
"""
    upper_index = 2 if plan.VARIANT == "both" else 1
    for floor, index in (("ground", 0), ("upper", upper_index)):
        width = round(plan.OX * plan.S) + (113 if floor == "ground" else 114)
        x = plan.MARGIN - 10 + index * (plan.OX * plan.S + plan.GAP)
        viewport = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="{x} {y} {width} {height}">'
        )
        cropped = re.sub(r"<svg[^>]*>", lambda _: viewport, svg, count=1)
        subprocess.run(
            [node, "-e", rasterize, str(directory / f"{floor}.png")],
            input=cropped, encoding="utf-8", check=True,
        )


def build_booklet(destination, temp):
    source = ROOT / "out" / "final"
    layout = json.loads((ROOT / "out" / "layout.json").read_text(encoding="utf-8"))
    params = plan.P
    if layout["params"] != params:
        raise SystemExit("План устарел. Обновите его командой make plan.")
    if layout["floors"]["upper"]["variant"] != "b":
        raise SystemExit("Буклет рассчитан на план второго этажа в варианте Б.")
    font_dir = Path(os.environ.get("BOOKLET_FONT_DIR", "/System/Library/Fonts/Supplemental"))
    for name, file in [("Body", "Arial.ttf"), ("Bold", "Arial Bold.ttf"), ("Display", "Georgia.ttf")]:
        pdfmetrics.registerFont(TTFont(name, str(font_dir / file)))
    pdf = Canvas(str(destination), pagesize=(W, H), pageCompression=1)
    pdf.setTitle(f"{PROJECT_NAME}. Концепция реконструкции каменного дома")
    pdf.setSubject("Дизайн-буклет: участок, планы этажей и интерьеры")
    pdf.setAuthor(f"Проект «{PROJECT_NAME}»")
    pdf.showOutline()
    page = 0

    def box(x, y, w, h, fill):
        pdf.setFillColor(HexColor(fill))
        pdf.rect(x, H - y - h, w, h, fill=1, stroke=0)

    def line(x0, y, x1, color=RULE):
        pdf.setStrokeColor(HexColor(color))
        pdf.setLineWidth(.55)
        pdf.line(x0, H - y, x1, H - y)

    def text(s, x, top, size=11, font="Body", color=INK, align="left"):
        pdf.setFont(font, size)
        pdf.setFillColor(HexColor(color))
        draw = {"left": pdf.drawString, "right": pdf.drawRightString, "center": pdf.drawCentredString}[align]
        draw(x, H - top - size, s)

    def label(s, x, top, color=GREEN):
        pdf.saveState()
        t = pdf.beginText(x, H - top - 8.3)
        t.setFont("Bold", 8.3)
        t.setCharSpace(1.25)
        t.setFillColor(HexColor(color))
        t.textLine(s.upper())
        pdf.drawText(t)
        pdf.restoreState()

    def para(s, x, top, w, size=11.2, leading=None, color=INK, font="Body"):
        style = ParagraphStyle("booklet", fontName=font, fontSize=size, leading=leading or size * 1.42,
                               textColor=HexColor(color), splitLongWords=False)
        p = Paragraph(s, style)
        _, h = p.wrap(w, H)
        assert top + h < H - 25, (page, s, top, h)
        p.drawOn(pdf, x, H - top - h)
        return top + h

    def photo(name, x, top, w, h, vertical=.5):
        path = source / name
        if not path.is_file():
            raise SystemExit(f"Не найден принятый кадр: {path}")
        with Image.open(path) as original:
            img = original.convert("RGB")
            ratio = w / h
            if img.width / img.height > ratio:
                left = round((img.width - img.height * ratio) / 2)
                img = img.crop((left, 0, img.width - left, img.height))
            elif img.width / img.height < ratio:
                crop_h = round(img.width / ratio)
                y0 = round((img.height - crop_h) * vertical)
                img = img.crop((0, y0, img.width, y0 + crop_h))
            jpeg = BytesIO()
            img.save(jpeg, format="JPEG", quality=94, optimize=True, subsampling=0)
            jpeg.seek(0)
            pdf.drawImage(ImageReader(jpeg), x, H - top - h, w, h)

    def start(section, title, deck, background=PAPER):
        nonlocal page
        page += 1
        box(0, 0, W, H, background)
        key = f"page{page}"
        pdf.bookmarkPage(key)
        pdf.addOutlineEntry(title, key)
        label(section, M, 32)
        text(title, M, 45, 33, "Display")
        para(deck, M, 93, C, 10.9, 14, DIM)
        line(M, 120, W - M)

    def finish():
        line(M, 552, W - M)
        label(f"{PROJECT_NAME}  /  Концепция", M, 563)
        text(f"{page:02d} / {PAGE_COUNT:02d}", W - M, 562, 9, "Bold", GREEN, "right")
        pdf.showPage()

    def caption(s, x, top, w):
        return para(s, x, top, w, 8.7, 12, DIM)

    def story(blocks, x, y, w):
        for title, body in blocks:
            label(title, x, y, CLAY)
            y = para(body, x, y + 18, w, 11.0, 15.4) + 21
        return y

    def number(n, info, x, y, w=205):
        text(n, x, y, 21, "Display", GREEN)
        caption(info, x, y + 29, w)

    def swatches(colors, x, y, w):
        gap = 9
        sw = (w - gap * (len(colors) - 1)) / len(colors)
        for i, (color, name) in enumerate(colors):
            left = x + i * (sw + gap)
            box(left, y, sw, 19, color)
            para(name, left, y + 24, sw, 8.15, 10.3, DIM)

    def single(section, title, deck, filename, credit, blocks, palette):
        start(section, title, deck)
        photo(filename, M, 139, 510, 340)
        caption(credit, M, 489, 510)
        x = M + 534
        story(blocks, x, 144, W - M - x)
        swatches(palette, x, 454, W - M - x)
        finish()

    def pair(section, title, deck, items):
        start(section, title, deck)
        gap = 18
        w = (C - gap) / 2
        for i, (filename, headline, tag, body, chip) in enumerate(items):
            x = M + i * (w + gap)
            photo(filename, x, 139, w, w * 2 / 3)
            box(x, 403, 8, 8, chip)
            label(tag, x + 15, 402)
            text(headline, x, 415, 17, "Display")
            para(body, x, 446, w - 9, 10.7, 15)
        finish()

    def fmt(value, decimals=2):
        return f"{value:.{decimals}f}".replace(".", ",")

    def dims(x, y):
        return f"{fmt(x)} × {fmt(y)}"

    def area(floor, name):
        room = next(room for room in layout["floors"][floor]["rooms"] if room["name"] == name)
        return fmt(room["area"])

    def draw_plan(which, section, title, deck, notes):
        start(section, title, deck, WHITE)
        fp = layout["floors"][which]
        chart = temp / f"{which}.png"
        with Image.open(chart) as p:
            ratio = p.width / p.height
        pw = min(518, 382 * ratio)
        ph = pw / ratio
        pdf.drawImage(str(chart), M, H - 130 - ph, pw, ph)
        caption("Север вверху, улица со стороны южного фасада. Размеры на плане в метрах.", M, 522, 527)
        x = M + 538
        right = W - M
        label("Экспликация", x, 136)
        text("ПОМЕЩЕНИЕ", x, 156, 7.8, "Bold", DIM)
        text("РАЗМЕР, М", right - 43, 156, 7.8, "Bold", DIM, "right")
        text("М²", right, 156, 7.8, "Bold", DIM, "right")
        line(x, 172, right)
        y = 177
        for room in fp["rooms"]:
            name = room["name"].strip()
            if name == "Лестница":
                continue
            if name == "Шкаф":
                name += " спальни " + ("3" if "3" in room["note"] else "2")
            if name == "Прихожая-холл":
                name = "Холл"
            area = fmt(room["area"])
            size = dims(room["x1"] - room["x0"], room["y1"] - room["y0"])
            if name in ("Холл", "Коридор"):
                size = "-"
            text(name, x, y, 8.8)
            text(size, right - 43, y, 8.5, "Body", DIM, "right")
            text(area, right, y, 8.8, "Bold", INK, "right")
            y += 23
            line(x, y - 5, right, "#E4DED2")
        total = sum(r["area"] for r in fp["rooms"] if r["name"] != "Лестница")
        text("Итого без лестницы", x, y + 1, 9.0, "Bold")
        text(fmt(total), right, y + 1, 9.0, "Bold", INK, "right")
        story(notes, x, y + 38, right - x)
        finish()

    # Cover
    page += 1
    pdf.bookmarkPage("cover")
    pdf.addOutlineEntry(PROJECT_NAME, "cover")
    box(0, 0, W, H, PAPER)
    photo("01_ext_aerial_se.png", 0, 0, W, 420, .50)
    box(0, 420, W, 3, CLAY)
    label("Реконструкция каменного дома", M, 441)
    text(PROJECT_NAME, M - 2, 449, 55, "Display")
    text("Концепция архитектуры и интерьеров", M, 525, 14, "Body", DIM)
    pdf.setStrokeColor(HexColor(RULE))
    pdf.line(510, H - 449, 510, H - 547)
    label("Черногория  /  Бар", 537, 451)
    para("Кадастровый округ Zankovići<br/>Участок 1255", 537, 473, 260, 13, 18)
    text("Ноябрь 2026", 537, 526, 10, "Body", DIM)
    pdf.showPage()

    # Site
    s = params["site"]
    stair = layout["derived"]["stair"]
    start("01  /  Участок", "Дом, двор и улица",
          "Въезд находится в нижней части улицы. От ворот проезд идёт вдоль фасада к парковке на западе.")
    photo("00_site_top.png", M, 139, 519, 346)
    caption("Вид сверху из Blender. Улица внизу, парковка слева, бассейн справа от дома.", M, 495, 519)
    x = 582
    number(f"{fmt(params['outer_x'],0)} × {fmt(params['outer_y'],0)} м", "Габарит дома по наружным стенам", x, 140)
    number(f"{fmt(s['pool']['len'],0)} × {fmt(s['pool']['w'],0)} м", f"Бассейн · глубина по модели {fmt(s['pool']['depth'],1)} м", x, 204)
    number(f"{fmt(s['pergola']['depth'],1)} × {fmt(s['pergola']['len'],1)} м", "Пергола у выхода из кухни-гостиной", x, 268)
    number(f"{fmt(s['street']['rise'],1)} м", "Перепад между двором и улицей у парковки", x, 332)
    line(x, 400, W - M)
    para("Бассейн и пергола образуют зону отдыха у восточной стены. Четыре туи вдоль уличной ограды прикрывают бассейн со стороны проезда.", x, 416, W - M - x, 10.7, 15)
    caption("Границы и рельеф показаны по модели участка.", x, 492, W - M - x)
    finish()

    pair("02  /  Экстерьер", "Камень, черепица и дерево",
         "Традиционный силуэт каменного дома дополняют лаконичная ограда и открытая пергола.",
         [
             ("02_ext_road_sw.png", "Фасад со стороны улицы", "Известняк", "Светлый камень и известковые швы подчёркивают фактуру кладки. Антрацитовые рамы и ограда собирают рисунок фасада, а терракотовая черепица добавляет тепла.", "#AD6246"),
             ("03_ext_east.png", "Терраса у бассейна", "Тёплое дерево", "Рейки перголы дают подвижную тень. Деревянный настил выделяет террасу на фоне светлого мощения, а оливы и кипарисы продолжают зелень участка.", "#787A54"),
         ])

    draw_plan("ground", "03  /  Планировка", "Первый этаж",
         "Вход со стороны улицы ведёт в холл с лестницей. Кухня-гостиная выходит на террасу.",
         [("Планировочный акцент", "Кухня и гостиная занимают единый объём. В западной части собраны лестница, кладовая и санузел с ванной."),
         ("Лестница", f"Ширина марша {fmt(stair['width'])} м. В модели {stair['risers']} подъёмов по {fmt(stair['riser'] * 1000, 1)} мм, глубина проступи {stair['tread'] * 1000:.0f} мм.")])

    draw_plan("upper", "04  /  Планировка", "Второй этаж",
         "Вариант Б. Три спальни, шкафы при спальнях 2 и 3 и узкий санузел с душем в торце.",
         [("Каменная стена", "Пунктир показывает положение стены, которую в варианте Б предполагается разобрать. Решение требует расчёта конструктора.")])

    single("05  /  Интерьер", "Гостиная",
           f"Общая зона первого этажа · {area('ground', 'Кухня-гостиная')} м² вместе с кухней",
           "04_living.png", "Вид из кухни на камин, ТВ-зону и проход к лестнице.",
           [("Светлая основа", "Белые стены и светлый пол с мягкими прожилками отражают дневной свет. Глубокие оконные откосы подчёркивают толщину каменных стен."),
            ("Тёмные акценты", "Антрацитовый диван и рамы создают контраст. Тёплое дерево и приглушённое золото связывают гостиную с кухней и холлом.")],
           [("#EDE5D8", "Тёплый белый"), ("#3F3B36", "Антрацит"), ("#AC8656", "Тёплое дерево")])

    single("06  /  Интерьер", "Кухня и барная стойка",
           "Кухня вдоль глухой стены. Раздвижная дверь ведёт на террасу.",
           "05_kitchen.png", "Встроенная техника и шкафы до потолка образуют спокойный фон для общей комнаты.",
           [("Кашемир и светлый камень", "Тёплые бежевые фасады без ручек смягчают белую основу. Столешница и фартук в близких тонах объединяют рабочую линию."),
            ("Свет над стойкой", "Золотистые подвесы обозначают зону завтрака. Подсветка под шкафами отдельно освещает рабочую поверхность.")],
           [("#BFAE96", "Кашемир"), ("#E9DFCF", "Светлый камень"), ("#B4894D", "Тёплый металл")])

    single("07  /  Интерьер", "Холл и лестница",
           f"Прихожая · {area('ground', 'Прихожая-холл')} м². Лестница связывает общую зону и спальни.",
           "06_hall.png", "Дубовая панель с крючками, круглое зеркало и скамья у лестницы.",
           [("Дуб и графит", "Вертикальные рейки собирают зону хранения в один объём. Тёмная скамья перекликается с перилами, а зеркало ловит свет у входа."),
            ("Линия ступеней", "Светлый бетон и тёплая подсветка под ступенями подчёркивают поворот лестницы. Тонкое чёрное ограждение сохраняет ощущение открытого пространства.")],
           [("#AB7849", "Дуб"), ("#D6CFC1", "Светлый бетон"), ("#383634", "Графит")])

    pair("08  /  Спальни", "Олива и терракота",
         "Три спальни объединяют светлые боковые стены, натуральный текстиль и тёплый свет у изголовий.",
         [
             ("07_bedroom1.png", f"Спальня 1 · {area('upper', 'Спальня 1')} м²", "Глубокая олива", "Приглушённый зелёный повторяет оттенки пейзажа за окном. Тёплое дерево, латунь и кремовый текстиль смягчают тёмную стену.", "#55593A"),
             ("08_bedroom2.png", f"Спальня 2 · {area('upper', 'Спальня 2')} м²", "Тёплая терракота", "Цвет обожжённой глины отсылает к черепице дома. Вертикальные рейки, картина и льняной текстиль добавляют фактуру в одной тёплой гамме.", "#A45337"),
         ])

    single("09  /  Спальни", "Спальня в дымчато-синем",
           f"Спальня 3 · {area('upper', 'Спальня 3')} м². Кровать 140 см по модели, шкаф встроен в нишу.",
           "09_bedroom3.png", "Акцент за изголовьем и окно в боковой стене.",
           [("Синий и песочный", "Глубокий приглушённый синий даёт более прохладный характер комнате. Светлый лён, дерево и латунь возвращают тепло."),
            ("Общий мотив", "Панель за изголовьем, парные светильники и картина связывают комнату с двумя другими спальнями. Цвет делает её самостоятельной.")],
           [("#3C5661", "Дымчато-синий"), ("#E7D7BF", "Лён"), ("#AA895F", "Тёплый металл")])

    pair("10  /  Санузлы", "Светлый камень и тёмные детали",
         "Крупный формат плитки, прозрачное стекло и тёплый свет объединяют оба санузла.",
         [
             ("10_bath_tub.png", f"Первый этаж · {area('ground', 'Санузел с ванной')} м²", "Ванна", "Ванна стоит в торце. Светлый керамогранит под мрамор объединяет стены и пол, а дерево, чёрная фурнитура и подсветка зеркала добавляют глубины.", "#B99F86"),
             ("11_bath_up.png", f"Второй этаж · {area('upper', 'Санузел с душем')} м²", "Душ", "Санузел 4,25 × 1,12 м. Душ занимает торец 1,12 × 0,90 м. По плану предусмотрена одна распашная створка 70 см и неподвижная часть остекления.", "#605549"),
         ])

    assert page == PAGE_COUNT
    pdf.save()

def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".booklet-", dir=OUTPUT.parent) as staging:
        temp = Path(staging)
        destination = temp / OUTPUT.name
        render_plans(temp)
        build_booklet(destination, temp)
        destination.replace(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    main()
