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
Decor rule: every decorative item is unique in the image — never repeat the same object (no second
fruit bowl, no identical vases or plants on different surfaces); keep worktops and the bar mostly clear.

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
- Back wall (no window): one straight kitchen run along the whole wall. Handleless matte cashmere-beige
  fronts (push-to-open, thin shadow gaps), same sizes and door rhythm as the draft: base units, and the
  wall units go all the way up to the ceiling (no gap above them). Light stone-look worktop with a
  matching stone backsplash slab between base and wall units; warm LED strip under the wall units; an
  undermount sink with a black mixer tap on the left part and a flush black induction hob on the right.
- Right end of the run, both floor-to-ceiling and flush with the fronts: first a tall appliance column
  with a built-in black-glass oven at waist height and a built-in black-glass microwave directly above
  it (cashmere drawer below, cashmere door above up to the ceiling); then, in the corner, a tall
  integrated fridge-freezer column hidden behind two cashmere handleless doors up to the ceiling.
- Right wall: a window with a black aluminium frame in a deep white reveal, and further right a tall
  black-framed sliding glass door to the terrace; outside: green garden, olive trees, cypresses and rocky
  mountains in the distance (no sea).
- Foreground left: the breakfast bar attached to the left wall (out of frame) — light stone-look
  worktop, cashmere-beige base; the brown blocks are placeholders for three cream leatherette bar stools
  with low backs on black metal bases. Two gold wire pendant lights hang above the bar. The bar top stays
  almost empty (at most one small item).
- Foreground right: the top of the back of the dark anthracite sofa.
- Ceiling: smooth white with round flush LED ceiling lights. Floor: white marble-look porcelain tiles.
```

---

## Спальни — общий стиль (вставляется в промпты 3–5)

```
Bedroom style: a stylish, rich, magazine-worthy modern bedroom — calm but not bland. White ceiling and
side walls; the wall behind the bed is the feature wall painted in a deep, saturated colour (given per
room below) with a full-height upholstered or vertically fluted headboard panel in a tone-on-tone shade.
Low upholstered bed with layered linen bedding in sand / cream with a textured throw and a few cushions
picking up the feature colour. Two matching floating nightstands (walnut, or anthracite with a walnut top)
on both sides of the bed, each with a brass or black wall sconce or a slim pendant. On the walls: one
large piece of framed art or a pair of framed prints above the headboard, a slim picture ledge or a
round mirror where it fits; a tall plant (olive tree or fiddle-leaf) in a ceramic pot; a soft large wool
rug under the bed on the white marble-look floor. Slim linen roller blinds recessed in the deep white
window reveals (no heavy curtains), black aluminium frames. Warm daylight plus warm accent lighting.
Every decorative item appears only once. Placeholders in the draft: the white block with a pillow strip
is the bed, the small brown blocks next to it are the nightstands.
```

## 3. Спальня 1 — `07_int_bedroom1`

```
[общий блок]
[стиль интерьера]
[стиль спальни]

This view: bedroom 1 (above the entrance hall), seen from the door.
- Feature colour: deep olive / sage green, with brass accents and warm oak.
- The bed stands in the middle with its headboard against the far wall: make the far wall the accent
  headboard wall with the two nightstands and sconces.
- The window with a black frame in a deep white reveal is in the wall on the left; outside: olive trees,
  cypresses and rocky mountains (no sea).
- On the right: the corner of the wall by the door.
- Keep the room compact and uncluttered: no extra wardrobes or desks beyond what is in the draft.
```

## 4. Спальня 2 — `08_int_bedroom2`

```
[общий блок]
[стиль интерьера]
[стиль спальни]

This view: bedroom 2 (front corner of the house), seen from the door.
- Feature colour: warm terracotta / clay, with cream, rattan and black accents.
- The bed stands with its headboard against the far wall — a solid feature wall with no window: tall
  fluted headboard panel, framed art above it, nightstands and sconces on both sides.
- The only window, with a black frame, is in the wall on the right; outside: olive trees, cypresses,
  rocky mountains (no sea).
- Behind the camera / at the edge of the frame: a built-in wardrobe niche — handleless cashmere-beige or
  white fronts flush with the wall.
```

## 5. Спальня 3 — `09_int_bedroom3`

```
[общий блок]
[стиль интерьера]
[стиль спальни]

This view: bedroom 3 (back corner of the house), seen from the door.
- Feature colour: dusty denim blue, with natural linen, light oak and brass accents.
- The bed (a narrower 140 cm double) stands with its headboard against the wall on the right — a solid
  feature wall with no window: tall fluted headboard panel, framed art above it, nightstands and sconces
  on both sides.
- The only window, with a black frame, is in the wall on the left; outside: garden greenery, olive trees
  and mountains (no sea).
- The built-in wardrobe niche is behind the camera — do not add other wardrobes.
```

---

## 6. Холл и лестница — `06_int_hall_stair`

Файлы: `out/views/06_int_hall_stair.png` + `refs/hall_concept.png` (кусок одобренной гостиной v3) + `refs/style/`.
Запуск: `python3 codex/run.py 06_int_hall_stair refs/hall_concept.png`

```
[общий блок]
[стиль интерьера]

The SECOND attached image is the approved hall concept (a crop from the approved living-room render of
this same house): keep exactly this concept and make the hall a beautiful, high-quality space.

This view: the entrance hall seen from the passage to the living room.
- Left: the front entrance door — a tall anthracite flush door with black hardware in a deep white reveal.
- Centre: the L-shaped staircase in smooth light-grey polished concrete / microcement, warm LED strip under
  the nosing of every step, slim black metal handrail on thin black posts. Under the upper flight, where the
  draft shows an opening on the right, a flush handleless door to the under-stair storage, painted the wall
  colour or in oak slats so it nearly disappears.
- Along the stair side: the entrance unit from the concept — an anthracite low cabinet/bench with an oak
  top, and above it a full-height vertical oak slatted panel with a large round mirror on it, a row of
  black hooks and a small black wall light on top, a slim oak shelf crowning the panel.
- A small white plastered niche in the wall by the stair, as in the concept, with one ceramic object.
- Floor: white marble-look porcelain tiles; warm, soft evening-like accent lighting plus daylight.
- You may refine details (shadow gaps, lighting, one plant, one rug) to make it stylish — but keep the
  layout, the stair, the door and the entrance unit where they are in the draft.
```

---

## Санузлы — общий стиль (вставляется в промпты 7–8)

```
Bathroom style (as in the owner's other house): floor and walls in large-format polished white
marble-look porcelain slabs with soft grey and warm gold veins, laid floor-to-ceiling; wall-hung white
toilet with a concealed cistern and a slim white flush plate; walk-in shower with a frameless clear glass
panel, black rain shower and black hand shower, a recessed lit niche; vanity unit in matte anthracite
with a walnut top and an oval white vessel basin with a tall black mixer; a large round mirror with
warm LED backlight where there is a free wall; a white ladder heated towel rail; a tall anthracite +
walnut storage cabinet with a few open shelves of rolled towels. Warm soft lighting, black accessories.
Every decorative item appears only once. Placeholders in the draft: white blocks are the bathtub,
toilet, vanity/basin and cabinets; a grey-green glass panel is the shower screen.
```

## 7. Санузел с ванной, 1 этаж — `10_int_bath_tub`

```
[общий блок]
[стиль интерьера]
[стиль санузла]

This view: the ground-floor bathroom seen from the door.
- Far wall (left part of the frame): a built-in bathtub running the full depth of the room, enclosed in
  the same marble-look slabs, with a black wall-mounted bath mixer and a frameless glass splash screen.
- Centre: the vanity with the vessel basin, and directly above it the large round backlit mirror on the
  wall (between the bathtub and the window).
- Right: the wall-hung toilet with the concealed cistern and flush plate, directly under the small window
  (as in the owner's reference bathroom); a white ladder towel rail on the wall nearby.
- Behind the camera there is a tall storage cabinet — do not add extra furniture in the frame.
```

## 8. Санузел с душем, 2 этаж — `11_int_bath_up`

```
[общий блок]
[стиль интерьера]
[стиль санузла]

This view: the upstairs shower room (narrow, about 1.1 m deep), seen from the door.
- Foreground left: the vanity with the vessel basin on the back wall, a round backlit mirror above it.
- Far end: the shower takes the WHOLE width of the room (wall to wall, about 0.9 m deep), with a flush
  floor and a linear drain. It is closed by a frameless clear glass enclosure across the full width: a
  narrow fixed glass panel plus a hinged glass DOOR (black hinges and a slim black handle) that opens
  outward into the room, so you can walk in. Black rain shower, black hand shower, a lit niche in the
  marble-look back wall.
- Right: the door opening to the corridor.
- The wall-hung toilet is behind the camera — do not add it in the frame. Keep the room narrow and
  realistic; do not widen it.
```

---

## Экстерьер — общий стиль (вставляется в промпты 9–11)

```
Exterior style: a restored traditional stone house in a village above Bar, coastal Montenegro. Thick
walls of light grey-beige local limestone rubble masonry with lime mortar joints (natural, irregular,
slightly weathered stones, larger dressed quoin stones at the corners); smooth light dressed-stone
surrounds, lintels and sills around every window and door; slim anthracite aluminium windows and an
anthracite front door; a low hip roof with traditional terracotta curved clay tiles (Mediterranean
"kanalica"), a thin eave; no gutters visible. Garden: neat lawn, local light limestone paving, olive
trees with silver-green leaves and twisted trunks, tall slim dark cypresses, lavender and rosemary
beds, a clipped green hedge along the side boundary; the front fence is a low stone plinth with a black
vertical-bar metal railing, a black sliding car gate and a matching pedestrian gate between stone
pillars. Pergola: warm natural oak/teak beams and slats, a terrace deck of brown composite boards under
it with an outdoor lounge set (dark metal-frame sofa with anthracite cushions, a round grey pouf) and
a beige umbrella. Pool: light limestone coping and paving, turquoise mosaic water, two wooden sun
loungers with white cushions. Background: green Mediterranean hills and rocky grey mountains, blue sky
with a few white clouds, warm late-morning sun. Placeholders in the draft: green blobs are olive trees,
green cones are cypresses, green boxes are hedges.
```

## 9. Вид сверху с юго-востока — `01_ext_aerial_se`

```
[общий блок]
[стиль экстерьера]

This view: a high drone view of the whole plot from the front-right corner. Show the house, the front
fence along the lane with the gates, the parking on the front-left, the entry path to the front door,
the pool in the front-right corner and the pergola terrace on the right side of the house, the hedge and
cypresses at the back-right. A white compact car parked on the parking. Keep the lane in the
foreground as a light concrete village path.
```

## 10. С улицы у калитки — `02_ext_road_sw`

```
[общий блок]
[стиль экстерьера]

This view: eye level from the lane outside the front fence, looking at the front (south) facade over
the black railing. The front door with the small window to its left and the living-room window to its
right on the ground floor, two windows upstairs. Keep the railing in the foreground sharp; the corner of
the pergola and the pool are just visible on the right, an olive tree on the left by the parking.
```

## 11. Бассейн и пергола — `03_ext_east`

```
[общий блок]
[стиль экстерьера]

This view: eye level from the far corner of the garden behind the pool, looking at the house and the
pergola. Foreground: the pool with light limestone coping, two wooden sun loungers with white cushions
on the paving at its side. Middle: the pergola terrace against the side wall of the house with the
outdoor lounge set under it and the black-framed sliding glass door behind it. Right: a large olive
tree, the clipped hedge and two cypresses behind it. Left: the front corner of the house with its
windows and front door.
```
