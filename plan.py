#!/usr/bin/env python3
"""Черновой план дома по params.json -> plan.svg + layout.json (для Blender).

Все координаты считаются от размеров в params.json: поменял цифру -> запусти
    python3 plan.py
и план перерисуется. Если что-то перестало помещаться, скрипт печатает
предупреждения.
"""
import json
import math
from pathlib import Path

HERE = Path(__file__).parent
P = json.loads((HERE / "params.json").read_text())
OUT = HERE / "out"          # всё сгенерированное (в git не идёт)

S = 62           # пикселей на метр
MARGIN = 90
GAP = 190        # между планами
HEAD = 80
FOOT = 260

# ---- базовые размеры ---------------------------------------------------------
W = P["wall"]
OX, OY = P["outer_x"], P["outer_y"]
T = P["partition"]
CW = P["corridor"]

ax0, ax1 = W, P["annex_outer_x"]         # пристройка, внутри
iw0, iw1 = ax1, ax1 + W                  # каменная стена пристройка | основной объём
mx0, mx1 = iw1, OX - W                   # основной объём, внутри
y0, y1 = W, OY - W

# ---- лестница: Г-образная, левый ближний (юго-западный) угол -----------------
st = P["stair"]
SW_ = st["width"]
TR = st["tread"]
RISERS = max(2, round(P["floor_to_floor"] / st["target_riser"]))
RISER = P["floor_to_floor"] / RISERS
TREADS = RISERS - 1
N1 = st["bottom_treads"]                 # вдоль южной стены, от входа на запад
NW_ = st["winders"]                      # забежные в углу
N2 = TREADS - N1 - NW_                   # вдоль западной стены на север
cx0, cx1 = ax0, ax0 + SW_                # угловой квадрат
cy0, cy1 = y0, y0 + SW_
b_x1 = cx1 + N1 * TR                     # восточный край нижнего марша (первая ступень)
st_top = cy1 + N2 * TR                   # куда приходит марш на 2 этаже
corr0, corr1 = st_top, st_top + CW       # коридор 2 этажа (вместе с площадкой)

WARN = []


def check(cond, msg):
    if not cond:
        WARN.append(msg)


door_w = P["entrance_door"]
ent1 = ax1 - 0.1
ent0 = ent1 - door_w
check(N2 >= 1, "лестница: не хватает ступеней для марша вдоль западной стены")
check(ent0 >= b_x1 + 0.05, f"вход: дверь ({ent0:.2f}) налезает на первую ступень ({b_x1:.2f}) — пристройка узкая")
check(y1 - corr1 - T >= 1.0, f"2 этаж: на санузел остаётся {y1 - corr1 - T:.2f} м глубины (< 1.0)")


def R(name, x0_, y0_, x1_, y1_, note="", area=None, label_at=None):
    a = area if area is not None else (x1_ - x0_) * (y1_ - y0_)
    r = {"name": name, "x0": round(x0_, 3), "y0": round(y0_, 3),
         "x1": round(x1_, 3), "y1": round(y1_, 3), "area": round(a, 2), "note": note}
    if label_at:
        r["label_at"] = [round(label_at[0], 3), round(label_at[1], 3)]
    return r


stair_foot = SW_ * SW_ + N1 * TR * SW_ + N2 * TR * SW_

# ---- 1 этаж -----------------------------------------------------------------
g = P["ground"]
wc_y0 = y1 - g["wc_d"]                   # санузел: всю ширину пристройки, в глубине
stor_y0 = cy1 + 3 * TR                   # под маршем, где высота уже > ~1.5 м
check(wc_y0 - T >= st_top, "1 этаж: санузел налезает на марш лестницы")
check(g["tub"][0] <= g["wc_d"] + 1e-6, "1 этаж: ванна длиннее глубины санузла")
_lv = P["living"]
_il = _lv["island"]
_iy0 = y1 - 0.6 - _il["aisle_kitchen"] - _il["depth"]
check(_il["aisle_kitchen"] >= 0.9, "1 этаж: между островом и кухней меньше 0.9 м")
check(mx0 + _il["gap_left"] + _il["len"] <= mx1 - 0.9, "1 этаж: справа от острова меньше 0.9 м прохода")
check(_il["len"] / _il["seats"] >= 0.55, "1 этаж: на острове меньше 55 см на место")
_sf = _lv["sofa"]
check(y0 + _sf["gap_window"] + _sf["leg"] <= _iy0 - 0.42 - 0.9 + 1e-6,
      "1 этаж: между спинкой дивана и стульями у острова меньше 0.9 м прохода")
check(_sf["x0"] >= _lv["fireplace"]["side"] + 0.1, "1 этаж: диван упирается в камин")
check(mx1 - (mx0 + _sf["x0"] + _sf["long"]) >= 0.7 - 1e-6, "1 этаж: от дивана до раздвижной двери меньше 0.7 м")
check(y0 + _sf["gap_window"] + _sf["leg"] - _sf["depth"] >= y0 + _lv["tv_stand"][1] + 0.3
      or mx0 + _sf["x0"] + _sf["long"] <= mx1 - _lv["tv_stand"][0],
      "1 этаж: диван налезает на ТВ-тумбу")
hall_area = ((ax1 - ax0) * (y1 - y0) - stair_foot
             - SW_ * (wc_y0 - T - st_top)               # кладовая за маршем
             - (ax1 - ax0) * (g["wc_d"] + T))
GROUND = [
    R("Кухня-гостиная", mx0, y0, mx1, y1,
      label_at=((mx0 + mx1) / 2, y1 - 0.6 - P["living"]["island"]["aisle_kitchen"] / 2 + 0.05)),
    R("Прихожая-холл", cx1, cy1, ax1, wc_y0, area=hall_area),
    R("Санузел с ванной", ax0, wc_y0, ax1, y1),
    R("Кладовая", cx0, stor_y0, cx1, wc_y0 - T, "под лестницей"),
    R("Лестница", cx0, cy0, b_x1, st_top, area=stair_foot),
]

# ---- 2 этаж, вариант А: каменная стена остаётся ----------------------------
A = P["upper_a"]
mpA = A["main_split_y"]
nsA0 = mpA - 0.95 - 0.1                  # коридор вдоль стены начинается у двери спальни 1
A_ROOMS = [
    R("Спальня 1", mx0, y0, mx1, mpA),
    R("Спальня 2", mx0, mpA + T, mx1, y1),
    R("Кабинет / гардероб", cx1 + T, y0, ax1, nsA0 - T),
    R("Шкаф", cx1 + T, nsA0, ax1 - CW - T, corr0 - T),
    R("Коридор", ax0, corr0, ax1, corr1, "с площадкой",
      area=(ax1 - ax0) * CW + CW * (corr0 - nsA0)),
    R("Санузел с душем", ax0, corr1 + T, ax1, y1),
    R("Лестница", cx0, cy0, cx1, st_top, "проём", area=SW_ * (st_top - cy0)),
]

# ---- 2 этаж, вариант Б: стену на 2 этаже снимаем ---------------------------
B = P["upper_b"]
ex0 = mx1 - B["east_room_w"]             # западная грань восточных спален
esp = B["east_split_y"]
nsx1 = ex0 - T                           # коридор вдоль восточных спален
nsx0 = nsx1 - CW
nsB0 = esp - 0.95 - 0.1
b1x1 = nsx0 - T
check(b1x1 - (cx1 + T) >= 2.4, f"вариант Б: спальня 1 уже 2.4 м ({b1x1 - cx1 - T:.2f})")
B_ROOMS = [
    R("Спальня 1", cx1 + T, y0, b1x1, corr0 - T),
    R("Спальня 2", ex0, y0, mx1, esp),
    R("Спальня 3", ex0, esp + T, mx1, y1),
    R("Коридор", ax0, corr0, nsx1, corr1, "с площадкой",
      area=(nsx1 - ax0) * CW + CW * (corr0 - nsB0)),
    R("Санузел с душем", ax0, corr1 + T, b1x1, y1),
    R("Шкаф", nsx0, y0, nsx1, nsB0 - T, "открыт в спальню 2"),
    R("Шкаф ", nsx0, corr1 + T, nsx1, y1, "открыт в спальню 3"),
    R("Лестница", cx0, cy0, cx1, st_top, "проём", area=SW_ * (st_top - cy0)),
]


# ---- SVG ---------------------------------------------------------------------
class Svg:
    def __init__(self, ox, oy):
        self.ox, self.oy = ox, oy
        self.out = []
        # то, что уходит в 3D: проёмы, перегородки, мебель (в метрах)
        self.rec = {"openings": [], "parts": [], "furn": []}

    def _op(self, kind, x0_, y0_, x1_, y1_):
        self.rec["openings"].append({"kind": kind, "x0": round(min(x0_, x1_), 3), "y0": round(min(y0_, y1_), 3),
                                     "x1": round(max(x0_, x1_), 3), "y1": round(max(y0_, y1_), 3)})

    def X(self, x):
        return self.ox + x * S

    def Y(self, y):
        return self.oy + (OY - y) * S

    def rect(self, x0_, y0_, x1_, y1_, cls):
        a, b = sorted((x0_, x1_)), sorted((y0_, y1_))
        if cls == "part":
            self.rec["parts"].append([round(a[0], 3), round(b[0], 3), round(a[1], 3), round(b[1], 3)])
        elif cls in ("furn", "furnd"):
            self.rec["furn"].append({"kind": "misc", "r": [round(a[0], 3), round(b[0], 3),
                                                          round(a[1], 3), round(b[1], 3)]})
        self.out.append(
            f'<rect x="{self.X(a[0]):.1f}" y="{self.Y(b[1]):.1f}" '
            f'width="{(a[1]-a[0])*S:.1f}" height="{(b[1]-b[0])*S:.1f}" class="{cls}"/>')

    def line(self, x0_, y0_, x1_, y1_, cls):
        self.out.append(
            f'<line x1="{self.X(x0_):.1f}" y1="{self.Y(y0_):.1f}" '
            f'x2="{self.X(x1_):.1f}" y2="{self.Y(y1_):.1f}" class="{cls}"/>')

    def polygon(self, pts, cls, kind="misc"):
        """Замкнутый многоугольник; мебель-многоугольник уходит в 3D как призма."""
        if cls in ("furn", "furnd"):
            self.rec["furn"].append({"kind": kind, "poly": [[round(x, 3), round(y, 3)] for x, y in pts]})
        d = " ".join(f"{self.X(x):.1f},{self.Y(y):.1f}" for x, y in pts)
        self.out.append(f'<polygon points="{d}" class="{cls}"/>')

    def poly(self, pts, cls):
        d = " ".join(f"{self.X(x):.1f},{self.Y(y):.1f}" for x, y in pts)
        self.out.append(f'<polyline points="{d}" class="{cls}"/>')

    def text(self, x, y, s, cls):
        self.out.append(f'<text x="{self.X(x):.1f}" y="{self.Y(y):.1f}" class="{cls}">{s}</text>')

    def arc(self, cx, cy, r, a0, a1, cls):
        p0 = (cx + r * math.cos(a0), cy + r * math.sin(a0))
        p1 = (cx + r * math.cos(a1), cy + r * math.sin(a1))
        cross = math.cos(a0) * math.sin(a1) - math.sin(a0) * math.cos(a1)
        sweep = 0 if cross > 0 else 1
        self.out.append(
            f'<path d="M{self.X(p0[0]):.1f},{self.Y(p0[1]):.1f} '
            f'A{r*S:.1f},{r*S:.1f} 0 0 {sweep} {self.X(p1[0]):.1f},{self.Y(p1[1]):.1f}" class="{cls}"/>')

    def door_h(self, a, b, c, d, side, hinge="a"):
        """Дверь в стене вдоль X (y∈[c,d]), проём x∈[a,b]; side=+1 открывается на север."""
        self._op("door", a, c, b, d)
        self.rect(a, c, b, d, "cut")
        face = d if side > 0 else c
        hx, ox_ = (a, b) if hinge == "a" else (b, a)
        w = b - a
        self.line(hx, face, hx, face + side * w, "leaf")
        self.arc(hx, face, w, math.atan2(side, 0), math.atan2(0, ox_ - hx), "swing")

    def door_v(self, a, b, c, d, side, hinge="a"):
        """Дверь в стене вдоль Y (x∈[c,d]), проём y∈[a,b]; side=+1 открывается на восток."""
        self._op("door", c, a, d, b)
        self.rect(c, a, d, b, "cut")
        face = d if side > 0 else c
        hy, oy_ = (a, b) if hinge == "a" else (b, a)
        w = b - a
        self.line(face, hy, face + side * w, hy, "leaf")
        self.arc(face, hy, w, math.atan2(0, side), math.atan2(oy_ - hy, 0), "swing")

    def opening_v(self, a, b, c, d):
        self._op("opening", c, a, d, b)
        self.rect(c, a, d, b, "cut")
        self.line(c, a, d, a, "thin")
        self.line(c, b, d, b, "thin")

    def win_h(self, a, b, c, d, kind="window"):
        self._op(kind, a, c, b, d)
        self.rect(a, c, b, d, "win")
        for k in (0.4, 0.6):
            m = c + (d - c) * k
            self.line(a, m, b, m, "glass")

    def win_v(self, a, b, c, d, kind="window"):
        self._op(kind, c, a, d, b)
        self.rect(c, a, d, b, "win")
        for k in (0.4, 0.6):
            m = c + (d - c) * k
            self.line(m, a, m, b, "glass")

    def dim_h(self, xs, y):
        for x in xs:
            self.line(x, y - 0.12, x, y + 0.12, "dim")
        self.line(xs[0], y, xs[-1], y, "dim")
        for a, b in zip(xs, xs[1:]):
            self.text((a + b) / 2, y + 0.12, f"{b-a:.2f}", "dimt")

    def dim_v(self, ys, x):
        for y in ys:
            self.line(x - 0.12, y, x + 0.12, y, "dim")
        self.line(x, ys[0], x, ys[-1], "dim")
        for a, b in zip(ys, ys[1:]):
            cx, cy = self.X(x) + 14, self.Y((a + b) / 2)
            self.out.append(f'<text x="{cx:.1f}" y="{cy:.1f}" class="dimt" '
                            f'transform="rotate(-90 {cx:.1f} {cy:.1f})">{b-a:.2f}</text>')


def shell(g_, keep_internal=True):
    g_.rect(0, 0, OX, OY, "stone")
    if keep_internal:
        g_.rect(ax0, y0, ax1, y1, "floor")
        g_.rect(mx0, y0, mx1, y1, "floor")
    else:
        g_.rect(ax0, y0, mx1, y1, "floor")
        g_.rect(iw0, y0, iw1, y1, "removed")


def stair(g_, upper):
    # нижний марш вдоль южной стены (на 2 этаже над ним уже пол -> пунктир)
    cls = "hidden" if upper else "stairf"
    g_.rect(cx1, cy0, b_x1, cy1, cls)
    for i in range(1, N1):
        x = cx1 + i * TR
        g_.line(x, cy0, x, cy1, "hidden" if upper else "tread")
    # угол с забежными
    g_.rect(cx0, cy0, cx1, cy1, "stairf")
    for k in range(1, NW_):
        ang = math.pi + k * (math.pi / 2) / NW_
        dx, dy = math.cos(ang), math.sin(ang)
        s = min(SW_ / abs(dx) if dx else 9, SW_ / abs(dy) if dy else 9)
        g_.line(cx1, cy1, cx1 + dx * s, cy1 + dy * s, "tread")
    # марш вдоль западной стены
    g_.rect(cx0, cy1, cx1, st_top, "stairf")
    for i in range(1, N2):
        y = cy1 + i * TR
        g_.line(cx0, y, cx1, y, "tread")
    mid_x, mid_y = (cx0 + cx1) / 2, (cy0 + cy1) / 2
    if not upper:
        pts = [(b_x1 - 0.12, mid_y), (mid_x, mid_y), (mid_x, st_top - 0.15)]
        g_.text((cx1 + b_x1) / 2, cy1 + 0.18, "вверх", "small")
    else:
        pts = [(mid_x, mid_y), (mid_x, st_top - 0.15)]
        g_.line(cx1, cy0, cx1, st_top, "rail")
    g_.poly(pts, "arrow")
    ex, ey = pts[-1]
    g_.poly([(ex - 0.13, ey - 0.25), (ex, ey), (ex + 0.13, ey - 0.25)], "arrow")


def label(g_, r):
    cx, cy = r.get("label_at") or ((r["x0"] + r["x1"]) / 2, (r["y0"] + r["y1"]) / 2)
    w, h = r["x1"] - r["x0"], r["y1"] - r["y0"]
    if w < 2.3 or h < 1.3:
        lines = [r["name"].strip(), f"{r['area']:.1f} м²"]
        if w >= 1.2 and h >= 1.3:
            lines.insert(1, f"{w:.2f}×{h:.2f}")
        top = cy + 0.14 * (len(lines) - 1)
        for i, s in enumerate(lines):
            g_.text(cx, top - i * 0.27, s, "rname-s" if i == 0 else "rdim-s")
        return
    g_.text(cx, cy + 0.22, r["name"].strip(), "rname")
    g_.text(cx, cy - 0.1, f"{w:.2f} × {h:.2f} м", "rdim")
    g_.text(cx, cy - 0.4, f"{r['area']:.1f} м²" + (f" · {r['note']}" if r["note"] else ""), "rdim")


def dims(g_):
    g_.dim_h([0, ax0, ax1, iw1, mx1, OX], -0.75)
    g_.dim_h([0, OX], -1.25)
    g_.dim_v([0, y0, y1, OY], OX + 0.75)
    g_.dim_v([0, OY], OX + 1.25)


def furn(g_, *rects, cls="furn", kind="misc"):
    for r in rects:
        g_.rect(*r, cls)
        g_.rec["furn"][-1]["kind"] = kind


def bed(g_, x_head, yc, length=2.0, width=1.6, head="east"):
    if head == "east":
        furn(g_, (x_head - length, yc - width / 2, x_head, yc + width / 2), kind="bed")
        furn(g_, (x_head - 0.45, yc - width / 2 + 0.1, x_head - 0.1, yc + width / 2 - 0.1), kind="pillow")
    else:
        furn(g_, (x_head, yc - width / 2, x_head + length, yc + width / 2), kind="bed")
        furn(g_, (x_head + 0.1, yc - width / 2 + 0.1, x_head + 0.45, yc + width / 2 - 0.1), kind="pillow")


def bath_line(g_, x0_, x1_, yb0, yb1):
    """Санузел в линию вдоль северной стены: унитаз в левом углу (спиной к западной стене,
    лицом на восток), раковина за дверью, душ в восточном торце."""
    furn(g_, (x1_ - 0.9, yb1 - 0.9, x1_, yb1), kind="shower")      # душ 0.9x0.9
    g_.line(x1_ - 0.9, yb1 - 0.9, x1_, yb1, "furn")
    furn(g_, (x0_, yb1 - 0.55, x0_ + 0.65, yb1 - 0.15), kind="toilet")
    sx = cx1 + 1.25                                                # восточнее двери
    furn(g_, (sx, yb1 - 0.45, sx + 0.6, yb1 - 0.02), kind="sink")


# ---- этажи -------------------------------------------------------------------
def draw_ground(g_):
    shell(g_)
    stair(g_, upper=False)
    # перегородки: туалет, кладовая под маршем
    g_.rect(ax0, wc_y0 - T, ax1, wc_y0, "part")                   # холл | санузел
    g_.rect(cx1, stor_y0, cx1 + T, wc_y0 - T, "part")
    sd0 = wc_y0 - T - 0.85                                          # дверь кладовой у северного конца
    g_.door_v(sd0, sd0 + 0.7, cx1, cx1 + T, +1)
    furn(g_, (cx1 + T, cy1 + 0.05, cx1 + T + 0.6, sd0 - 0.1), kind="wardrobe")  # шкаф у подъёма лестницы
    bd0, bd1 = g["bath_door_x"]
    g_.door_h(bd0, bd1, wc_y0 - T, wc_y0, +1, hinge="b")          # в санузел
    # вход: дверь в южной стене пристройки, сразу налево — первая ступень
    g_.door_h(ent0, ent1, 0, y0, +1, hinge="b")
    g_.text((ent0 + ent1) / 2, -0.35, "вход", "small")
    # проёмы в каменной стене
    lo0, lo1 = g["living_opening_y"]
    g_.opening_v(lo0, lo1, iw0, iw1)                              # холл -> гостиная
    # окна
    g_.win_h(ax0 + 0.15, ax0 + 0.85, 0, y0)                       # окно над лестницей
    mxc = (mx0 + mx1) / 2
    g_.win_h(mxc - 0.7, mxc + 0.7, 0, y0)                         # юг, гостиная
    g_.win_v(y0 + 1.1, y0 + 2.9, mx1, OX, kind="sliding")         # раздвижная к перголе
    g_.text(mx1 - 0.6, y0 + 2.1, "раздвижная", "small")
    g_.text(mx1 - 0.6, y0 + 1.85, "к перголе", "small")
    g_.win_v(y1 - 1.6, y1 - 0.6, mx1, OX)                         # восток, кухня
    g_.win_h(mx0 + 1.0, mx0 + 2.0, y1, OY)                        # север, кухня
    g_.win_h(ax0 + 1.6, ax0 + 2.2, y1, OY)                        # север, санузел
    # мебель
    furn(g_, (mx0, y1 - 0.6, mx0 + 3.0, y1), kind="counter")      # кухня вдоль северной стены
    furn(g_, (mx1 - 0.6, y1 - 0.6, mx1, y1), kind="fridge")
    lv = P["living"]
    il = lv["island"]                                              # остров: отдельно от стен, 4 места с юга
    ix0, ix1 = mx0 + il["gap_left"], mx0 + il["gap_left"] + il["len"]
    iy1 = y1 - 0.6 - il["aisle_kitchen"]                           # северный край: проход до кухни
    iy0 = iy1 - il["depth"]
    furn(g_, (ix0, iy0, ix1, iy1), kind="island_top")              # столешница со свесом для коленей
    furn(g_, (ix0 + 0.05, iy0 + il["overhang"], ix1 - 0.05, iy1 - 0.05), kind="island_base", cls="furnd")
    n_st = il["seats"]
    pitch = il["len"] / n_st
    for i in range(n_st):                                          # стулья со стороны гостиной
        sx = ix0 + pitch * (i + 0.5) - 0.19
        furn(g_, (sx, iy0 - 0.42, sx + 0.38, iy0 - 0.04), kind="stool")
    fp = lv["fireplace"]                                           # камин в углу, фасад под 45°
    fa, fc = fp["side"], fp["cut"]
    g_.polygon([(mx0, y0), (mx0 + fa, y0), (mx0 + fa, y0 + fc), (mx0 + fc, y0 + fa), (mx0, y0 + fa)],
               "furnd", kind="fireplace")
    g_.text(mx0 + fa * 0.36, y0 + fa * 0.36 - 0.05, "камин", "small")
    tw_, td_ = lv["tv_stand"]
    furn(g_, (mx1 - tw_, y0, mx1, y0 + td_), kind="tv_stand")      # тумба под ТВ, правый нижний угол
    furn(g_, (mx1 - tw_ / 2 - 0.6, y0 + 0.05, mx1 - tw_ / 2 + 0.6, y0 + 0.12), kind="tv")
    g_.text(mx1 - tw_ / 2, y0 + td_ + 0.15, "ТВ", "small")
    sf = lv["sofa"]                                                # угловой диван, уголок со стороны камина
    sx0 = mx0 + sf["x0"]                                           # левый край дивана от левой стены гостиной
    sby = y0 + sf["gap_window"] + sf["leg"]                        # спинка длинной части
    sdp, sbk, sar, sl = sf["depth"], sf["back"], sf["arm"], sf["long"]
    sx1 = sx0 + sl
    furn(g_, (sx0, sby - sbk, sx1, sby), kind="sofa_back")         # спинка длинной части
    furn(g_, (sx0, sby - sf["leg"], sx0 + sbk, sby - sbk), kind="sofa_back")   # спинка уголка
    furn(g_, (sx1 - sar, sby - sdp, sx1, sby - sbk), kind="sofa_arm")          # подлокотник у ТВ
    cush_x = [sx0 + sbk, (sx0 + sbk + sx1 - sar) / 2, sx1 - sar]   # две подушки длинной части
    for a, b in zip(cush_x, cush_x[1:]):
        furn(g_, (a + 0.01, sby - sdp, b - 0.01, sby - sbk), kind="sofa_seat")
    furn(g_, (sx0 + sbk, sby - sf["leg"], sx0 + sdp, sby - sdp - 0.01), kind="sofa_seat")  # уголок
    ow, od = lv["ottoman"]                                         # оттоманка вплотную к дивану
    ox1 = sx1 - sar - 0.05
    oy1 = sby - sdp - lv["ottoman_gap"]
    furn(g_, (ox1 - ow, oy1 - od, ox1, oy1), kind="ottoman")
    tl, tw = g["tub"]
    furn(g_, (ax0, y1 - tl, ax0 + tw, y1), kind="tub")            # ванна у западной стены
    g_.rect(ax0 + 0.08, y1 - tl + 0.08, ax0 + tw - 0.08, y1 - 0.08, "fline")   # чаша ванны
    furn(g_, (ax0 + tw + 0.2, y1 - 0.65, ax0 + tw + 0.6, y1 - 0.05), kind="toilet")
    furn(g_, (bd0 + 0.05, y1 - 0.45, bd0 + 0.65, y1 - 0.02), kind="sink")
    furn(g_, (ax1 - 0.5, wc_y0, ax1, y1), kind="cabinet")          # шкаф для хранения
    for r in GROUND:
        if r["name"] != "Лестница":
            label(g_, r)
    dims(g_)


def draw_upper_a(g_):
    shell(g_)
    stair(g_, upper=True)
    g_.rect(cx1, cy0, cx1 + T, corr0, "part")                    # проём лестницы | кабинет
    g_.rect(cx1 + T, nsA0 - T, ax1, nsA0, "part")                 # кабинет | коридор/шкаф
    g_.rect(ax1 - CW - T, nsA0, ax1 - CW, corr0, "part")          # шкаф | коридор
    g_.rect(cx1 + T, corr0 - T, ax1 - CW - T, corr0, "part")      # шкаф | коридор E-W
    g_.rect(ax0, corr1, ax1, corr1 + T, "part")                   # коридор | санузел
    g_.rect(mx0, mpA, mx1, mpA + T, "part")                       # спальни
    # двери
    g_.door_v(mpA - 0.95, mpA - 0.1, iw0, iw1, +1, hinge="b")      # спальня 1
    g_.door_v(corr0 + 0.05, corr1 - 0.05, iw0, iw1, +1)           # спальня 2
    g_.door_h(ax1 - CW + 0.08, ax1 - 0.08, nsA0 - T, nsA0, -1)     # кабинет
    g_.door_h(cx1 + 0.3, cx1 + 1.05, corr1, corr1 + T, +1)         # санузел
    # окна
    mxc = (mx0 + mx1) / 2
    g_.win_h(cx1 + 0.5, cx1 + 1.5, 0, y0)                         # кабинет
    g_.win_h(mxc - 0.6, mxc + 0.6, 0, y0)                         # спальня 1 юг
    g_.win_v((y0 + mpA) / 2 - 0.5, (y0 + mpA) / 2 + 0.5, mx1, OX)
    g_.win_v((mpA + y1) / 2 - 0.5, (mpA + y1) / 2 + 0.5, mx1, OX)
    g_.win_h(mxc - 0.6, mxc + 0.6, y1, OY)                        # спальня 2 север
    g_.win_h(ax0 + 1.6, ax0 + 2.2, y1, OY)                        # санузел
    g_.win_v(corr0 + 0.15, corr1 - 0.15, 0, ax0)                   # площадка, запад
    bed(g_, mx1, (y0 + mpA) / 2)
    bed(g_, mx1, (mpA + T + y1) / 2)
    bath_line(g_, ax0, ax1, corr1 + T, y1)
    furn(g_, (cx1 + T, nsA0, ax1 - CW - T, corr0 - T), cls="furnd")
    for r in A_ROOMS:
        if r["name"] not in ("Лестница",):
            label(g_, r)
    dims(g_)


def draw_upper_b(g_):
    shell(g_, keep_internal=False)
    stair(g_, upper=True)
    g_.text((iw0 + iw1) / 2, y1 - 0.25, "стена", "tiny")
    g_.text((iw0 + iw1) / 2, y1 - 0.45, "снята", "tiny")
    g_.rect(cx1, cy0, cx1 + T, corr0, "part")                    # проём | спальня 1
    g_.rect(cx1 + T, corr0 - T, b1x1 + T, corr0, "part")          # спальня 1 | коридор
    g_.rect(b1x1, y0, b1x1 + T, corr0, "part")                    # спальня 1 | шкаф/коридор
    g_.rect(nsx0, nsB0 - T, nsx1, nsB0, "part")                   # шкаф | коридор
    g_.rect(ax0, corr1, nsx1, corr1 + T, "part")                  # коридор | санузел
    g_.rect(b1x1, corr1 + T, b1x1 + T, y1, "part")                # санузел | шкаф
    g_.rect(nsx1, nsB0 - T, ex0, corr1 + T, "part")              # восточные спальни (у шкафов стенки нет)
    for sy0_, sy1_ in ((y0, nsB0 - T), (corr1 + T, y1)):        # шкафы, открытые в спальню
        g_.line(nsx1 + T / 2, sy0_, nsx1 + T / 2, sy1_, "open")
        furn(g_, (nsx0, sy0_, nsx0 + 0.6, sy1_), kind="wardrobe")
    g_.rect(ex0, esp, mx1, esp + T, "part")
    # двери
    g_.door_h(b1x1 - 0.95, b1x1 - 0.15, corr0 - T, corr0, -1, hinge="b")  # спальня 1
    g_.door_v(esp - 0.95, esp - 0.1, nsx1, ex0, +1, hinge="b")     # спальня 2
    g_.door_v(corr0 + 0.05, corr1 - 0.05, nsx1, ex0, +1)           # спальня 3
    g_.door_h(cx1 + 0.3, cx1 + 1.05, corr1, corr1 + T, +1)         # санузел
    # окна
    exc = (ex0 + mx1) / 2
    g_.win_h((cx1 + b1x1) / 2 - 0.6, (cx1 + b1x1) / 2 + 0.6, 0, y0)  # спальня 1
    g_.win_h(exc - 0.6, exc + 0.6, 0, y0)                         # спальня 2 юг
    g_.win_v((y0 + esp) / 2 - 0.5, (y0 + esp) / 2 + 0.5, mx1, OX)
    g_.win_v((esp + y1) / 2 - 0.5, (esp + y1) / 2 + 0.5, mx1, OX)
    g_.win_h(exc - 0.6, exc + 0.6, y1, OY)                        # спальня 3 север
    g_.win_h(ax0 + 1.6, ax0 + 2.2, y1, OY)                        # санузел
    g_.win_v(corr0 + 0.15, corr1 - 0.15, 0, ax0)                   # площадка
    bed(g_, cx1 + T, (y0 + corr0 - T) / 2, head="west")
    bed(g_, mx1, (y0 + esp) / 2)
    bed(g_, mx1, (esp + T + y1) / 2, width=1.4)
    bath_line(g_, ax0, b1x1, corr1 + T, y1)
    for r in B_ROOMS:
        if r["name"] not in ("Лестница",):
            label(g_, r)
    dims(g_)


def table(out, x, y, title, rooms):
    out.append(f'<text x="{x}" y="{y}" class="th">{title}</text>')
    total, i = 0.0, 0
    for r in rooms:
        if r["name"] == "Лестница":
            continue
        total += r["area"]
        yy = y + 24 + i * 21
        out.append(f'<text x="{x}" y="{yy}" class="td">{r["name"].strip()}</text>')
        out.append(f'<text x="{x + 300}" y="{yy}" class="td num">{r["area"]:.1f} м²</text>')
        i += 1
    yy = y + 24 + i * 21
    out.append(f'<text x="{x}" y="{yy}" class="td b">Итого без лестницы</text>')
    out.append(f'<text x="{x + 300}" y="{yy}" class="td b num">{total:.1f} м²</text>')


CSS = """
.stone{fill:url(#hatch);stroke:#3a342c;stroke-width:1.6}
.floor{fill:#fbfaf7;stroke:#3a342c;stroke-width:1.2}
.removed{fill:#fbfaf7;stroke:#b5562f;stroke-width:1;stroke-dasharray:5 4}
.part{fill:#b9b2a6;stroke:#6d665b;stroke-width:0.8}
.cut{fill:#fbfaf7;stroke:none}
.win{fill:#e6f0f5;stroke:#3a342c;stroke-width:0.8}
.glass{stroke:#5a8aa3;stroke-width:1}
.leaf{stroke:#3a342c;stroke-width:1.6}
.swing{fill:none;stroke:#8c857a;stroke-width:0.8;stroke-dasharray:3 3}
.thin{stroke:#8c857a;stroke-width:0.8}
.stairf{fill:#f0ede6;stroke:#6d665b;stroke-width:0.9}
.hidden{fill:none;stroke:#a9a296;stroke-width:0.8;stroke-dasharray:4 3}
.tread{stroke:#9b9487;stroke-width:0.8}
.arrow{fill:none;stroke:#b5562f;stroke-width:1.4}
.rail{stroke:#b5562f;stroke-width:2.4}
.furn{fill:none;stroke:#b8b1a5;stroke-width:1}
.furnd{fill:none;stroke:#b8b1a5;stroke-width:1;stroke-dasharray:4 3}
.fline{fill:none;stroke:#b8b1a5;stroke-width:1}
.open{stroke:#8c857a;stroke-width:1;stroke-dasharray:2 3}
.dim{stroke:#6d665b;stroke-width:0.8}
text{font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;fill:#2b2620}
.dimt{font-size:12px;text-anchor:middle;fill:#4a443b}
.rname{font-size:14px;font-weight:600;text-anchor:middle}
.rdim{font-size:12px;text-anchor:middle;fill:#5a5349}
.rname-s{font-size:11.5px;font-weight:600;text-anchor:middle}
.rdim-s{font-size:10.5px;text-anchor:middle;fill:#5a5349}
.small{font-size:10.5px;text-anchor:middle;fill:#6d665b}
.tiny{font-size:9.5px;text-anchor:middle;fill:#b5562f}
.title{font-size:24px;font-weight:600}
.sub{font-size:13px;fill:#6d665b}
.ftitle{font-size:18px;font-weight:600}
.fsub{font-size:12.5px;fill:#6d665b}
.th{font-size:14px;font-weight:600}
.td{font-size:13px}
.num{text-anchor:end}
.b{font-weight:600}
.warn{font-size:13px;fill:#b5562f}
"""


VARIANT = P.get("upper_variant", "b")
UPPER = {"a": ("2 этаж · вариант А", "каменная стена остаётся", draw_upper_a, A_ROOMS),
         "b": ("2 этаж · вариант Б", "стена на 2 этаже снята — нужен расчёт конструктора", draw_upper_b, B_ROOMS)}
SHEETS = [("1 этаж", "", draw_ground, GROUND)]
SHEETS += [UPPER[v] for v in (("a", "b") if VARIANT == "both" else (VARIANT,))]


def export_png(svg, png, w, h):
    """PNG для просмотра через встроенные в macOS qlmanage + sips; на других системах пропускаем."""
    import shutil
    import subprocess
    import tempfile
    if not (shutil.which("qlmanage") and shutil.which("sips")):
        print("PNG не сделан: нет qlmanage/sips (не macOS) — открой out/plan.svg")
        return
    side = max(w, h)
    tmp = Path(tempfile.mkdtemp())
    try:
        head = f'width="{w}" height="{h}" viewBox="0 0 {w} {h}"'
        sq = f'width="{side}" height="{side}" viewBox="{-(side - w) / 2} {-(side - h) / 2} {side} {side}"'
        (tmp / "p.svg").write_text(svg.read_text(encoding="utf-8").replace(head, sq, 1), encoding="utf-8")
        subprocess.run(["qlmanage", "-t", "-s", str(side), "-o", str(tmp), str(tmp / "p.svg")],
                       check=True, capture_output=True)
        subprocess.run(["sips", "-c", str(h), str(w), str(tmp / "p.svg.png"), "--out", str(png)],
                       check=True, capture_output=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    plan_w, plan_h = OX * S, OY * S
    n = len(SHEETS)
    W_ = MARGIN * 2 + plan_w * n + GAP * (n - 1) + 60
    H_ = HEAD + MARGIN + plan_h + 110 + FOOT + 22 * len(WARN)
    oy = HEAD + MARGIN
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W_:.0f}" height="{H_:.0f}" '
           f'viewBox="0 0 {W_:.0f} {H_:.0f}">',
           '<defs><pattern id="hatch" width="7" height="7" patternUnits="userSpaceOnUse" '
           'patternTransform="rotate(45)"><rect width="7" height="7" fill="#d9d2c4"/>'
           '<line x1="0" y1="0" x2="0" y2="7" stroke="#a69c8a" stroke-width="1.2"/></pattern></defs>',
           f'<style>{CSS}</style>',
           f'<rect width="{W_:.0f}" height="{H_:.0f}" fill="#ffffff"/>',
           f'<text x="{MARGIN}" y="42" class="title">Черновик планировки v2 · дом {OX:.2f} × {OY:.2f} м</text>',
           f'<text x="{MARGIN}" y="64" class="sub">Камень {W:.2f} м (штриховка) · перегородки {T:.2f} м · '
           f'этаж {P["floor_to_floor"]:.2f} м · лестница Г-образная: {RISERS} подъёмов по {RISER*1000:.0f} мм, '
           f'проступь {TR*1000:.0f} мм ({N1} + {NW_} забежных + {N2}) · низ листа = юг, сторона дорожки (условно)</text>']
    recs = {}
    for i, (title, sub, fn, rooms) in enumerate(SHEETS):
        ox = MARGIN + i * (plan_w + GAP)
        g_ = Svg(ox, oy)
        fn(g_)
        recs[fn.__name__] = g_.rec
        out.append(f'<text x="{ox}" y="{oy - 38}" class="ftitle">{title}</text>')
        out.append(f'<text x="{ox}" y="{oy - 18}" class="fsub">{sub}</text>')
        out.extend(g_.out)
        table(out, ox, oy + plan_h + 135, "Помещения", rooms)
    for k, w in enumerate(WARN):
        out.append(f'<text x="{MARGIN}" y="{H_ - 20 - 22 * (len(WARN) - 1 - k)}" class="warn">⚠ {w}</text>')
    out.append("</svg>")
    OUT.mkdir(exist_ok=True)
    (OUT / "plan.svg").write_text("\n".join(out), encoding="utf-8")
    export_png(OUT / "plan.svg", OUT / "plan.png", round(W_), round(H_))

    up_v = "b" if VARIANT == "both" else VARIANT
    up_fn = UPPER[up_v][2]
    if up_fn.__name__ not in recs:
        g_ = Svg(0, 0)
        up_fn(g_)
        recs[up_fn.__name__] = g_.rec
    layout = {"params": P,
              "derived": {"x": {"ax0": ax0, "ax1": ax1, "iw0": iw0, "iw1": iw1, "mx0": mx0, "mx1": mx1},
                          "y": {"y0": y0, "y1": y1},
                          "stair": {"risers": RISERS, "riser": round(RISER, 4), "treads": TREADS,
                                    "tread": TR, "width": SW_, "bottom": N1, "winders": NW_, "north": N2,
                                    "cx0": cx0, "cx1": cx1, "cy0": cy0, "cy1": cy1,
                                    "bx1": round(b_x1, 3), "top_y": round(st_top, 3)}},
              "floors": {
                  "ground": {"z": 0.0, "internal_wall": True, "rooms": GROUND, **recs["draw_ground"]},
                  "upper": {"z": P["floor_to_floor"], "internal_wall": up_v == "a", "variant": up_v,
                            "rooms": UPPER[up_v][3], **recs[up_fn.__name__]}}}
    (OUT / "layout.json").write_text(json.dumps(layout, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Лестница: {RISERS} x {RISER*1000:.0f} мм, {N1}+{NW_}+{N2} проступей, приход на y={st_top:.2f}")
    for name, _sub, _fn, rooms in SHEETS:
        print(name)
        for r in rooms:
            print(f"  {r['name']:<24} {r['x1']-r['x0']:.2f} x {r['y1']-r['y0']:.2f}  {r['area']:.1f} м²")
    for w in WARN:
        print("ВНИМАНИЕ:", w)


if __name__ == "__main__":
    main()
