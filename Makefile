BLENDER ?= /Applications/Blender.app/Contents/MacOS/Blender

.PHONY: plan model render open clean

# План этажей: out/plan.svg, out/plan.png, out/layout.json
plan:
	python3 plan.py

# 3D-модель без рендера: out/house.blend
model: plan
	$(BLENDER) -b -P blender/build_house.py

# Модель + рендеры: out/renders/*.png (около 2–3 минут)
render: plan
	$(BLENDER) -b -P blender/build_house.py -- --render

# Открыть папку с результатами в Finder
open:
	open out

clean:
	rm -rf out
