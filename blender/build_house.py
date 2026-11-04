"""Черновая 3D-модель дома из layout.json (его пишет plan.py).

Сборка и рендер:
    python3 plan.py
    /Applications/Blender.app/Contents/MacOS/Blender -b -P blender/build_house.py -- --render

Результат: out/house.blend и out/renders/*.png.
Без --render только собирается и сохраняется house.blend.
"""
import json
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent.parent
OUT = HERE / "out"
L = json.loads((OUT / "layout.json").read_text(encoding="utf-8"))
P, D = L["params"], L["derived"]
ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
RENDER = "--render" in ARGS
SAMPLES = 96

W, OX, OY = P["wall"], P["outer_x"], P["outer_y"]
F2F, T = P["floor_to_floor"], P["partition"]
SLAB = 0.25
ROOF = P["roof"]
EAVE = ROOF["eave_z"]
ST = D["stair"]
EPS = 1e-3

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


# ---- коллекции и материалы -----------------------------------------------------
def collection(name, parent=None):
    c = bpy.data.collections.new(name)
    (parent or scene.collection).children.link(c)
    return c


C_GROUND = collection("1 этаж")
C_GROUND_HI = collection("1 этаж — выше 1.2 м")
C_UPPER = collection("2 этаж")
C_UPPER_HI = collection("2 этаж — выше 1.2 м")
CUT_H = 1.2      # высота, на которой «срезаем» стены для видов-разрезов
C_ROOF = collection("Крыша")
C_SITE = collection("Участок")
C_CUT = collection("_вырезы")


def principled(name, color, rough=0.6, **extra):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    for k, v in extra.items():
        if k in b.inputs:
            b.inputs[k].default_value = v
    return m


def hexc(h):
    h = h.lstrip("#")
    srgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb)


def stone_material():
    """Бутовая кладка: камни разного тона + светлый известковый шов (процедурно)."""
    m = bpy.data.materials.new("Камень кладка")
    m.use_nodes = True
    nt = m.node_tree
    N, Lk = nt.nodes, nt.links
    bsdf = N["Principled BSDF"]
    geo = N.new("ShaderNodeNewGeometry")
    mp = N.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (3.2, 3.2, 5.0)      # камни шире, чем выше
    Lk.new(geo.outputs["Position"], mp.inputs["Vector"])
    vc = N.new("ShaderNodeTexVoronoi")                       # цвет камня
    vc.inputs["Scale"].default_value = 1.0
    vc.inputs["Randomness"].default_value = 0.9
    Lk.new(mp.outputs["Vector"], vc.inputs["Vector"])
    ve = N.new("ShaderNodeTexVoronoi")                       # швы
    ve.feature = "DISTANCE_TO_EDGE"
    ve.inputs["Scale"].default_value = 1.0
    ve.inputs["Randomness"].default_value = 0.9
    Lk.new(mp.outputs["Vector"], ve.inputs["Vector"])
    bw = N.new("ShaderNodeRGBToBW")
    Lk.new(vc.outputs["Color"], bw.inputs["Color"])
    ramp = N.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*hexc("#8f887c"), 1)
    ramp.color_ramp.elements[1].color = (*hexc("#c9c2b4"), 1)
    e = ramp.color_ramp.elements.new(0.55)
    e.color = (*hexc("#b3a58c"), 1)
    Lk.new(bw.outputs["Val"], ramp.inputs["Fac"])
    mr = N.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.0
    mr.inputs["From Max"].default_value = 0.035
    Lk.new(ve.outputs["Distance"], mr.inputs["Value"])
    mix = N.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.inputs["A"].default_value = (*hexc("#b4ab9b"), 1)   # A — шов, B — камень
    Lk.new(mr.outputs["Result"], mix.inputs["Factor"])
    Lk.new(ramp.outputs["Color"], mix.inputs["B"])
    Lk.new(mix.outputs["Result"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.9
    bump = N.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.6
    bump.inputs["Distance"].default_value = 0.03
    Lk.new(mr.outputs["Result"], bump.inputs["Height"])
    Lk.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return m


def tile_material():
    m = principled("Черепица", hexc("#b65a35"), 0.7)
    nt = m.node_tree
    N, Lk = nt.nodes, nt.links
    bsdf = N["Principled BSDF"]
    geo = N.new("ShaderNodeNewGeometry")
    sep = N.new("ShaderNodeSeparateXYZ")
    Lk.new(geo.outputs["Position"], sep.inputs["Vector"])
    wave = N.new("ShaderNodeTexWave")                    # ряды черепицы по высоте
    wave.wave_type = "BANDS"
    wave.bands_direction = "Z"
    wave.inputs["Scale"].default_value = 1.2
    wave.inputs["Distortion"].default_value = 0.0
    Lk.new(geo.outputs["Position"], wave.inputs["Vector"])
    noise = N.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 3.0
    Lk.new(geo.outputs["Position"], noise.inputs["Vector"])
    mix = N.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.inputs["A"].default_value = (*hexc("#a24c2b"), 1)
    mix.inputs["B"].default_value = (*hexc("#c8683d"), 1)
    Lk.new(noise.outputs["Fac"], mix.inputs["Factor"])
    Lk.new(mix.outputs["Result"], bsdf.inputs["Base Color"])
    bump = N.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.5
    Lk.new(wave.outputs["Fac"], bump.inputs["Height"])
    Lk.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return m


M = {
    "stone": stone_material(),
    "dressed": principled("Тёсаный камень", hexc("#d6d0c4"), 0.75),
    "tile": tile_material(),
    "plaster": principled("Штукатурка", hexc("#eeeae3"), 0.85),
    "floor0": principled("Пол 1 этаж", hexc("#cbbfae"), 0.5),
    "floor1": principled("Пол дерево", hexc("#a87a50"), 0.5),
    "slab": principled("Перекрытие", hexc("#e3ded5"), 0.8),
    "wood": principled("Дерево рам", hexc("#6a4830"), 0.55),
    "glass": principled("Стекло", hexc("#bcd3dc"), 0.03,
                        **{"Transmission Weight": 1.0, "IOR": 1.45}),
    "stair": principled("Лестница", hexc("#8a6442"), 0.5),
    "furn": principled("Мебель", hexc("#dad3c7"), 0.7),
    "screen": principled("Экран", hexc("#1d1f22"), 0.15),
    "fabric": principled("Ткань", hexc("#9d9387"), 0.95),
    "soot": principled("Топка", hexc("#141210"), 0.9),
    "bed": principled("Кровать", hexc("#efe9de"), 0.8),
    "ceramic": principled("Сантехника", hexc("#f4f4f2"), 0.2),
    "grass": principled("Газон", hexc("#6f8a4c"), 0.95),
    "cut": principled("Вырез", (1, 0, 0), 0.5),
}


# ---- геометрия -------------------------------------------------------------------
def link(ob, col):
    col.objects.link(ob)
    return ob


def box(name, x0, y0, z0, x1, y1, z1, mat, col):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x = x1 if v.co.x > 0 else x0
        v.co.y = y1 if v.co.y > 0 else y0
        v.co.z = z1 if v.co.z > 0 else z0
    bm.to_mesh(me)
    bm.free()
    me.materials.append(mat)
    return link(bpy.data.objects.new(name, me), col)


def prism(name, pts, z0, z1, mat, col):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bot = [bm.verts.new((x, y, z0)) for x, y in pts]
    top = [bm.verts.new((x, y, z1)) for x, y in pts]
    bm.faces.new(bot[::-1])
    bm.faces.new(top)
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((bot[i], bot[j], top[j], top[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(mat)
    return link(bpy.data.objects.new(name, me), col)


def bake(ob):
    """Применить модификаторы через depsgraph (работает в фоне без контекста UI)."""
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    old = ob.data
    ob.modifiers.clear()
    ob.data = me
    bpy.data.meshes.remove(old)


def subtract(obs, cutters_col):
    for ob in obs:
        mod = ob.modifiers.new("cut", "BOOLEAN")
        mod.operation = "DIFFERENCE"
        mod.operand_type = "COLLECTION"
        mod.collection = cutters_col
        mod.solver = "EXACT"
    bpy.context.view_layer.update()
    for ob in obs:
        bake(ob)


def is_outer(o):
    return o["x0"] <= EPS or o["y0"] <= EPS or o["x1"] >= OX - EPS or o["y1"] >= OY - EPS


def band_axis(o):
    """По какой оси идёт толщина стены у проёма: 'y' (стена вдоль X) или 'x'."""
    dx, dy = o["x1"] - o["x0"], o["y1"] - o["y0"]
    for t in (W, T):
        if abs(dy - t) < 0.02:
            return "y"
        if abs(dx - t) < 0.02:
            return "x"
    return "y" if dy < dx else "x"


def z_range(o):
    k = o["kind"]
    span =(o["x1"] - o["x0"]) if band_axis(o) == "y" else (o["y1"] - o["y0"])
    if k == "door":
        return 0.0, 2.2 if is_outer(o) else 2.1
    if k == "opening":
        return 0.0, 2.25
    if k == "sliding":
        return 0.0, 2.3
    if span <= 0.75:
        return 1.35, 2.05            # маленькие окна: санузлы, лестница
    return 0.85, 2.2


# ---- стены, перекрытия, проёмы ---------------------------------------------------
def floor_walls(z_floor, z0, z1, internal, col):
    obs = [
        box("Стена юг", 0, 0, z0, OX, W, z1, M["stone"], col),
        box("Стена север", 0, OY - W, z0, OX, OY, z1, M["stone"], col),
        box("Стена запад", 0, W, z0, W, OY - W, z1, M["stone"], col),
        box("Стена восток", OX - W, W, z0, OX, OY - W, z1, M["stone"], col),
    ]
    if internal:
        x = D["x"]
        top = min(z1, z_floor + F2F - SLAB)
        if top > z0:
            obs.append(box("Стена внутр.", x["iw0"], W, z0, x["iw1"], OY - W, top, M["stone"], col))
    return obs


def build_floor(key, col, col_hi, z_top):
    """Стены и перегородки этажа двумя кусками: до 1.2 м (col) и выше (col_hi)."""
    fl = L["floors"][key]
    z = fl["z"]
    zc = z + CUT_H
    walls = (floor_walls(z, z, zc, fl["internal_wall"], col)
             + floor_walls(z, zc, z_top, fl["internal_wall"], col_hi))
    h_part = (z_top - z) - (SLAB if key == "ground" else 0.0)   # перегородки до потолка
    parts = []
    for x0, y0, x1, y1 in fl["parts"]:
        parts.append(box("Перегородка", x0, y0, z, x1, y1, zc, M["plaster"], col))
        parts.append(box("Перегородка", x0, y0, zc, x1, y1, z + h_part, M["plaster"], col_hi))
    cut_col = collection(f"_вырезы {key}", C_CUT)
    for o in fl["openings"]:
        za, zb = z_range(o)
        ax_ = band_axis(o)
        ex = (0.0, 0.08) if ax_ == "y" else (0.08, 0.0)
        box("вырез", o["x0"] - ex[0], o["y0"] - ex[1], z + za - (0.05 if za == 0 else 0),
            o["x1"] + ex[0], o["y1"] + ex[1], z + zb, M["cut"], cut_col)
    subtract(walls + parts, cut_col)
    for o in fl["openings"]:
        if is_outer(o):
            fill_opening(o, z, col_hi)    # окна и двери уходят вместе с верхом стен на разрезах
    return fl


def fill_opening(o, z, col):
    """Стекло/дверь + деревянная рама + обрамление из тёсаного камня снаружи."""
    za, zb = z_range(o)
    za, zb = z + za, z + zb
    ax_ = band_axis(o)
    if ax_ == "y":
        a0, a1 = o["x0"], o["x1"]
        outer = o["y0"] if o["y0"] <= EPS else o["y1"]
        sgn = 1 if o["y0"] <= EPS else -1
    else:
        a0, a1 = o["y0"], o["y1"]
        outer = o["x0"] if o["x0"] <= EPS else o["x1"]
        sgn = 1 if o["x0"] <= EPS else -1
    pane = outer + sgn * 0.22      # плоскость окна: 22 см вглубь от фасада

    def B(name, s0, s1, d0, d1, h0, h1, mat):
        d0, d1 = sorted((d0, d1))
        if ax_ == "y":
            return box(name, s0, d0, h0, s1, d1, h1, mat, col)
        return box(name, d0, s0, h0, d1, s1, h1, mat, col)

    fw = 0.07
    door = o["kind"] == "door"
    B("рама", a0, a0 + fw, pane - 0.04, pane + 0.04, za, zb, M["wood"])
    B("рама", a1 - fw, a1, pane - 0.04, pane + 0.04, za, zb, M["wood"])
    B("рама", a0, a1, pane - 0.04, pane + 0.04, zb - fw, zb, M["wood"])
    if not door:
        B("рама", a0, a1, pane - 0.04, pane + 0.04, za, za + fw, M["wood"])
    if door:
        B("дверь", a0 + fw, a1 - fw, pane - 0.025, pane + 0.025, za, zb - fw, M["wood"])
    else:
        B("стекло", a0 + fw, a1 - fw, pane - 0.01, pane + 0.01, za + fw, zb - fw, M["glass"])
        if a1 - a0 > 1.1:          # средний импост
            mid = (a0 + a1) / 2
            B("импост", mid - 0.035, mid + 0.035, pane - 0.04, pane + 0.04, za, zb, M["wood"])
    # обрамление из тёсаного камня (как на старом доме): косяки, перемычка, подоконник
    s = 0.2
    fo, fi = outer - sgn * 0.02, outer + sgn * 0.12
    B("обрамление", a0 - s, a0, fo, fi, za, zb, M["dressed"])
    B("обрамление", a1, a1 + s, fo, fi, za, zb, M["dressed"])
    B("перемычка", a0 - s, a1 + s, fo, fi, zb, zb + s, M["dressed"])
    if not (door or o["kind"] == "sliding"):
        B("подоконник", a0 - s, a1 + s, outer - sgn * 0.06, pane, za - 0.12, za, M["dressed"])


def build_slabs():
    box("Пол 1 этажа", W, W, -0.05, OX - W, OY - W, 0.0, M["floor0"], C_GROUND)
    slab = box("Перекрытие", W, W, F2F - SLAB, OX - W, OY - W, F2F - 0.02, M["slab"], C_UPPER)
    box("Пол 2 этажа", W, W, F2F - 0.02, OX - W, OY - W, F2F, M["floor1"], C_UPPER)
    cut = collection("_проём лестницы", C_CUT)
    box("проём", ST["cx0"] - 0.01, ST["cy0"] - 0.01, F2F - SLAB - 0.1,
        ST["cx1"], ST["top_y"], F2F + 0.1, M["cut"], cut)
    subtract([slab, bpy.data.objects["Пол 2 этажа"]], cut)
    for ob in (slab, bpy.data.objects["Пол 2 этажа"]):
        print(f"проверка: {ob.name}: {len(ob.data.vertices)} вершин, размеры {tuple(round(d, 2) for d in ob.dimensions)}")


def build_stair():
    r, t, wdt = ST["riser"], ST["tread"], ST["width"]
    cx0, cx1, cy0, cy1, bx1 = ST["cx0"], ST["cx1"], ST["cy0"], ST["cy1"], ST["bx1"]
    thick = 0.32

    def step(name, pts, i):
        ztop = i * r
        prism(name, pts, max(0.0, ztop - thick), ztop, M["stair"], C_GROUND)

    n = 0
    for i in range(1, ST["bottom"] + 1):          # вдоль южной стены, от входа на запад
        n += 1
        xa, xb = bx1 - i * t, bx1 - (i - 1) * t
        step(f"ступень {n}", [(xa, cy0), (xb, cy0), (xb, cy1), (xa, cy1)], n)
    k = math.tan(math.radians(30)) * wdt          # забежные: лучи из внутреннего угла
    winders = [
        [(cx1, cy1), (cx1, cy0), (cx1 - k, cy0)],
        [(cx1, cy1), (cx1 - k, cy0), (cx0, cy0), (cx0, cy1 - k)],
        [(cx1, cy1), (cx0, cy1 - k), (cx0, cy1)],
    ][:ST["winders"]]
    for pts in winders:
        n += 1
        step(f"ступень {n}", pts, n)
    for j in range(1, ST["north"] + 1):           # вдоль западной стены на север
        n += 1
        ya, yb = cy1 + (j - 1) * t, cy1 + j * t
        step(f"ступень {n}", [(cx0, ya), (cx1, ya), (cx1, yb), (cx0, yb)], n)
    # перила вдоль открытого края марша (на 1 этаже)
    yb = ST["top_y"]
    for j in range(0, ST["north"] + 1, 2):
        y = cy1 + j * t + 0.1
        zb = (ST["bottom"] + ST["winders"] + j) * r
        box("стойка", cx1 - 0.06, y - 0.02, zb, cx1 - 0.02, y + 0.02, zb + 0.9, M["wood"], C_GROUND)
    rail = box("поручень", cx1 - 0.07, cy1, 0, cx1 - 0.01, yb, 0.05, M["wood"], C_GROUND)
    me = rail.data
    z_lo = (ST["bottom"] + ST["winders"]) * r + 0.9
    z_hi = (ST["bottom"] + ST["winders"] + ST["north"]) * r + 0.9
    for v in me.vertices:                          # наклонный поручень
        frac = (v.co.y - cy1) / max(yb - cy1, 1e-6)
        v.co.z = z_lo + frac * (z_hi - z_lo) + (0.05 if v.co.z > 0.01 else 0)


FURN_H = {  # (z0, z1, материал)
    "bed": (0.0, 0.45, "bed"), "pillow": (0.45, 0.58, "bed"), "counter": (0.0, 0.9, "furn"),
    "fridge": (0.0, 1.9, "furn"), "table": (0.0, 0.75, "wood"), "sofa": (0.0, 0.8, "furn"),
    "coffee": (0.0, 0.4, "wood"), "wardrobe": (0.0, 2.1, "furn"), "toilet": (0.0, 0.42, "ceramic"),
    "sink": (0.75, 0.88, "ceramic"), "shower": (0.0, 0.05, "ceramic"), "misc": (0.0, 0.8, "furn"),
    "tub": (0.0, 0.55, "ceramic"), "cabinet": (0.0, 2.0, "furn"),
    "bar": (0.0, 1.05, "wood"), "stool": (0.0, 0.65, "wood"), "tv_stand": (0.0, 0.5, "furn"),
    "island_top": (0.87, 0.92, "wood"), "island_base": (0.0, 0.87, "furn"),
    "shoe_bench": (0.0, 0.45, "wood"), "coat_panel": (1.15, 1.95, "wood"), "hat_shelf": (1.85, 1.89, "wood"),
    "tv": (0.6, 1.3, "screen"), "fireplace": (0.0, 1.05, "dressed"),
    "sofa_seat": (0.0, 0.44, "fabric"), "sofa_back": (0.0, 0.82, "fabric"), "sofa_arm": (0.0, 0.62, "fabric"),
    "ottoman": (0.0, 0.42, "fabric"),
}


def build_poly_furniture(f, zf, z0, z1, mat, col):
    pts = [tuple(p) for p in f["poly"]]
    prism(f["kind"], pts, zf + z0, zf + z1, M[mat], col)
    if f["kind"] != "fireplace":
        return
    # камин: дымоход до потолка (чуть уже) + тёмная топка на диагональном фасаде
    cx_, cy_ = pts[0]
    inner = [(cx_ + (x - cx_) * 0.8, cy_ + (y - cy_) * 0.8) for x, y in pts]
    prism("дымоход", inner, zf + z1, zf + F2F - SLAB, M["plaster"], col)
    prism("полка", [(cx_ + (x - cx_) * 1.04, cy_ + (y - cy_) * 1.04) for x, y in pts],
          zf + z1, zf + z1 + 0.06, M["wood"], col)
    (ax_, ay_), (bx_, by_) = pts[2], pts[3]                         # диагональная грань
    mx_, my_ = (ax_ + bx_) / 2, (ay_ + by_) / 2
    L_ = math.hypot(bx_ - ax_, by_ - ay_)
    ux, uy = (bx_ - ax_) / L_, (by_ - ay_) / L_
    nx, ny = uy * -1, ux                                            # наружу, в комнату
    if nx * (mx_ - cx_) + ny * (my_ - cy_) < 0:
        nx, ny = -nx, -ny
    hw = min(0.32, L_ / 2 - 0.08)
    q = [(mx_ - ux * hw - nx * 0.2, my_ - uy * hw - ny * 0.2), (mx_ + ux * hw - nx * 0.2, my_ + uy * hw - ny * 0.2),
         (mx_ + ux * hw + nx * 0.01, my_ + uy * hw + ny * 0.01), (mx_ - ux * hw + nx * 0.01, my_ - uy * hw + ny * 0.01)]
    prism("топка", q, zf + 0.18, zf + 0.72, M["soot"], col)


def build_furniture(key, col):
    fl = L["floors"][key]
    for f in fl["furn"]:
        z0, z1, mat = FURN_H.get(f["kind"], FURN_H["misc"])
        zf = fl["z"]
        if "poly" in f:
            build_poly_furniture(f, zf, z0, z1, mat, col)
            continue
        x0, y0, x1, y1 = f["r"]
        if f["kind"] in ("table", "coffee"):      # столешница на ножках
            box(f["kind"], x0, y0, zf + z1 - 0.04, x1, y1, zf + z1, M[mat], col)
            for lx, ly in ((x0 + 0.05, y0 + 0.05), (x1 - 0.1, y0 + 0.05),
                           (x0 + 0.05, y1 - 0.1), (x1 - 0.1, y1 - 0.1)):
                box("ножка", lx, ly, zf, lx + 0.05, ly + 0.05, zf + z1 - 0.04, M[mat], col)
            continue
        box(f["kind"], x0, y0, zf + z0, x1, y1, zf + z1, M[mat], col)
        if f["kind"] == "coat_panel":   # крючки на панели
            n = max(2, int((y1 - y0) / 0.3))
            for i in range(n):
                hy = y0 + (i + 0.5) * (y1 - y0) / n
                box("крючок", x1, hy - 0.015, zf + 1.6, x1 + 0.07, hy + 0.015, zf + 1.64, M["wood"], col)
        if f["kind"] == "shower":   # стеклянная перегородка душа
            box("душ стекло", x0, y0, fl["z"], x0 + 0.01, y1, fl["z"] + 2.0, M["glass"], col)


def build_roof():
    o, p = ROOF["overhang"], math.radians(ROOF["pitch_deg"])
    z_e = EAVE - o * math.tan(p)        # край свеса ниже, чтобы на линии фасада было ровно EAVE
    x0, y0, x1, y1 = -o, -o, OX + o, OY + o
    lx, ly = x1 - x0, y1 - y0
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    if lx >= ly:
        h = ly / 2 * math.tan(p)
        r0, r1 = (cx - (lx - ly) / 2, cy, z_e + h), (cx + (lx - ly) / 2, cy, z_e + h)
    else:
        h = lx / 2 * math.tan(p)
        r0, r1 = (cx, cy - (ly - lx) / 2, z_e + h), (cx, cy + (ly - lx) / 2, z_e + h)
    me = bpy.data.meshes.new("Крыша")
    bm = bmesh.new()
    c = [bm.verts.new(v) for v in ((x0, y0, z_e), (x1, y0, z_e), (x1, y1, z_e), (x0, y1, z_e))]
    a, b = bm.verts.new(r0), bm.verts.new(r1)
    if lx >= ly:
        faces = [(c[0], c[1], b, a), (c[2], c[3], a, b), (c[1], c[2], b), (c[3], c[0], a)]
    else:
        faces = [(c[1], c[2], b, a), (c[3], c[0], a, b), (c[0], c[1], a), (c[2], c[3], b)]
    for f in faces:
        bm.faces.new(f)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(M["tile"])
    ob = link(bpy.data.objects.new("Крыша", me), C_ROOF)
    sol = ob.modifiers.new("толщина", "SOLIDIFY")
    sol.thickness = ROOF["thickness"]
    sol.offset = -1
    bake(ob)
    # потолок 2 этажа / низ свеса (софит), чтобы снизу не было видно насквозь
    box("Потолок 2 этажа", W, W, EAVE - 0.02, OX - W, OY - W, EAVE, M["plaster"], C_ROOF)
    return h + z_e


# ---- участок, свет, камеры -------------------------------------------------------
def build_site():
    box("Земля", -15, -15, -0.12, OX + 15, OY + 15, -0.06, M["grass"], C_SITE)
    box("Отмостка", -0.6, -0.6, -0.07, OX + 0.6, OY + 0.6, -0.04, M["dressed"], C_SITE)


def lights_and_world():
    sun_d = bpy.data.lights.new("Солнце", "SUN")
    sun_d.energy = 4.0
    sun_d.angle = math.radians(1.5)
    sun = bpy.data.objects.new("Солнце", sun_d)
    sun.rotation_euler = (math.radians(48), 0, math.radians(38))
    scene.collection.objects.link(sun)
    world = bpy.data.worlds.new("Небо")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (*hexc("#a9c3dc"), 1)
    bg.inputs["Strength"].default_value = 0.9
    scene.world = world


def camera(name, loc, target, lens=35):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    cd.clip_end = 300
    cam = bpy.data.objects.new(name, cd)
    cam.location = loc
    d = Vector(target) - Vector(loc)
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(cam)
    return cam


def setup_render():
    scene.render.engine = "CYCLES"
    scene.cycles.samples = SAMPLES
    scene.cycles.use_denoising = True
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = "METAL"
        prefs.get_devices()
        for dev in prefs.devices:
            dev.use = True
        scene.cycles.device = "GPU"
    except Exception as e:  # noqa: BLE001
        print("GPU недоступен, рендер на CPU:", e)
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 1000
    scene.view_settings.view_transform = "AgX"
    scene.render.image_settings.file_format = "PNG"


ALL = (C_GROUND, C_GROUND_HI, C_UPPER, C_UPPER_HI, C_ROOF, C_SITE)


def set_visible(*cols):
    for c in ALL:
        c.hide_render = c not in cols
        c.hide_viewport = c not in cols


def main():
    build_site()
    build_floor("ground", C_GROUND, C_GROUND_HI, F2F)
    build_floor("upper", C_UPPER, C_UPPER_HI, EAVE)
    build_slabs()
    build_stair()
    build_furniture("ground", C_GROUND)
    build_furniture("upper", C_UPPER)
    ridge = build_roof()
    C_CUT.hide_render = True
    C_CUT.hide_viewport = True
    lights_and_world()
    setup_render()

    cx, cy = OX / 2, OY / 2
    views = {
        "aerial": (camera("Вид сверху-сбоку", (OX + 10, -12, 11), (cx, cy, 2.6), 35), ALL),
        "south": (camera("Южный фасад", (cx + 2.0, -16, 1.7), (cx, cy, 3.1), 35), ALL),
        "cut_ground": (camera("Разрез 1 этаж", (cx + 5.0, -7.5, 12.5), (cx, cy - 0.2, 0.2), 30),
                       (C_GROUND, C_SITE)),
        "cut_upper": (camera("Разрез 2 этаж", (cx + 5.0, -7.5, 15.5), (cx, cy - 0.2, 3.2), 30),
                      (C_GROUND, C_GROUND_HI, C_UPPER, C_SITE)),
    }
    print(f"Конёк на высоте {ridge:.2f} м, карниз {EAVE:.2f} м")
    out = OUT / "renders"
    out.mkdir(exist_ok=True)
    if RENDER:
        for name, (cam, cols) in views.items():
            set_visible(*cols)
            scene.camera = cam
            scene.render.filepath = str(out / f"{name}.png")
            bpy.ops.render.render(write_still=True)
            print("рендер:", scene.render.filepath)
    set_visible(*ALL)
    scene.camera = views["aerial"][0]
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "house.blend"))
    print("сохранено:", OUT / "house.blend")


main()
