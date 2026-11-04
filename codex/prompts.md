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
  entrance hall with a glimpse of the oak staircase; keep it as an open passage (no door).
- Foreground left: the back of a straight dark anthracite fabric sofa with adjustable headrests and two
  armrests — no chaise, no corner part.
- Foreground right: the breakfast bar attached to the wall on the right — light stone-look worktop,
  cashmere-beige base, with cream bar stools on black bases (two visible here; the brown blocks are
  placeholder stools).
- Floor: white marble-look porcelain tiles throughout; a soft light rug under the sofa area.
```
