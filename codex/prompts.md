# Промпты для генерации картинок (Codex)

Идём по одному ракурсу. Каждый ракурс — черновой рендер из Blender (`out/views/…png`, делается `make views`),
к нему прикладываем стилевые фото (`refs/style/…`) и вставляем промпт: общий блок + блок ракурса.
Результаты складываем в `out/codex/<имя ракурса>_vN.png`.

Запуск одного ракурса: `python3 codex/run.py 04_int_living` — следующая версия vN, промпт и ответ сохраняются рядом.

Промпты на английском — генераторы картинок понимают его точнее.

---

## Общий блок (вставляется в каждый промпт)

```
The FIRST attached image is a draft 3D render of a real renovation project. Treat it as a strict
geometry reference: keep the exact camera position, lens, perspective and framing; keep every wall,
opening, window, door, the staircase and every furniture piece at the same position, size and
proportion. Do not add or remove windows, doors, walls, rooms or major furniture. Replace only the
placeholder materials and blocky placeholder furniture with realistic, finished versions of the same
items in the same footprint, and add lighting, textiles and a little tasteful decor.

The OTHER attached images are style references (photos of the owner's other house in Montenegro and
approved earlier renders of this project): follow their materials, colours and furniture style, not
their layout. Where a reference conflicts with the text below, the text wins.

Output: one photorealistic image, professional interior/architectural photography, natural daylight,
3:2 landscape, same aspect as the draft.
```

## Стиль интерьера (для внутренних ракурсов)

```
Interior style: bright, modern, clean Mediterranean home (fully renovated — no exposed stone inside).
Smooth white painted walls and ceilings; deep window reveals (the outer walls are 70 cm thick) finished
in smooth white plaster; large-format polished white marble-look porcelain floor tiles with soft grey
and warm gold veins; slim black/anthracite aluminium window and door frames; warm white LED lighting,
round flush ceiling lights. Furniture: dark anthracite fabric corner sofa with adjustable headrests and
a mustard accent cushion; handleless matte cashmere-beige kitchen fronts with integrated appliances,
light stone-look worktop and backsplash, black mixer tap; cream leatherette bar stools on black metal
bases; gold wire pendant lights; anthracite + walnut cabinetry in bathrooms.
Staircase: an L-shaped monolithic stair in smooth light-grey polished concrete / microcement (not wood),
solid sculptural treads and risers, a warm LED strip glowing under the nosing of every step, a slim black
metal handrail on thin black posts. Entrance hall: calm and stylish — a low built-in bench/shoe cabinet
in matte anthracite with an oak top along the stair side, an oak slatted wall panel above it with a row of
black hooks and a slim shelf, a large round mirror, warm wall lights; same white marble-look floor.
```

---

## 1. Гостиная — `04_int_living`

Файлы: `out/views/04_int_living.png` + фото гостиной, кухни и барной зоны из `refs/style/`.

```
[общий блок]
[стиль интерьера]

This view: the living room seen from the kitchen corner, looking towards the front (south) of the house.
- Left: a large flat TV on a long, low, wall-to-window media unit (matte anthracite or walnut, handleless),
  standing in front of the white wall; keep its width — it runs from the window edge almost to the wall.
- Centre: the south window with a black aluminium frame in a deep white reveal. No curtains: only a slim
  linen-coloured roller blind recessed into the top of the reveal, rolled up. Outside the window: a green
  Mediterranean hillside with olive trees and cypresses rising to rocky grey mountains (coastal
  Montenegro inland view) — no sea.
- Centre-right: a corner fireplace set diagonally at 45° in the corner — make it a stylish modern built-in
  fireplace: smooth white plaster / microcement chimney breast up to the ceiling, a wide glass-fronted
  firebox with a real flame, a slim light-stone or oak mantel shelf.
- Right of the fireplace, separated from it by a clear strip of white wall: a wide opening to the
  entrance hall; keep it as an open passage (no door). Through it you see the hall: the light-grey concrete
  staircase with LED-lit steps and a black handrail, and the stylish entrance bench with the slatted oak
  hook panel (see the staircase and hall description above). The brown blocks there are placeholders.
- Foreground left: the back of a straight dark anthracite fabric sofa with adjustable headrests and two
  armrests — no chaise, no corner part.
- Foreground right: the breakfast bar attached to the wall on the right — light stone-look worktop,
  cashmere-beige base, with cream bar stools on black bases (two visible here; the brown blocks are
  placeholder stools).
- Floor: white marble-look porcelain tiles throughout; a soft light rug under the sofa area.
```

---

## 2. Кухня — `05_int_kitchen`

Файлы: `out/views/05_int_kitchen.png` + стилевые референсы из `refs/style/`.

```
[общий блок]
[стиль интерьера]

This view: the kitchen seen from the living area by the fireplace, looking towards the back (north)
and the right (east) side of the house.
- Back wall (no window): one straight kitchen run along the whole wall. Replace the white placeholder
  cabinets with handleless matte cashmere-beige fronts (push-to-open, thin shadow gaps), base units and a
  full row of wall units above, same sizes and door rhythm. Light stone-look worktop with a matching stone
  backsplash slab between the base and wall units; warm LED strip under the wall units; an undermount sink
  with a black mixer tap on the left part and a flush black induction hob on the right part.
- Right end of the run: the grey block is a tall column — make it a tall cashmere-beige unit with an
  integrated fridge-freezer behind the same handleless fronts, flush with the run.
- Right wall: a window with a black aluminium frame in a deep white reveal, and further right a tall
  black-framed sliding glass door to the terrace; outside: green garden, olive trees, cypresses and rocky
  mountains in the distance (no sea).
- Foreground left: the breakfast bar attached to the left wall (out of frame) — light stone-look
  worktop, cashmere-beige base; the brown blocks are placeholders for three cream leatherette bar stools
  with low backs on black metal bases. Two gold wire pendant lights hang above the bar.
- Foreground right: the top of the back of the dark anthracite sofa.
- Ceiling: smooth white with round flush LED ceiling lights. Floor: white marble-look porcelain tiles.
```
