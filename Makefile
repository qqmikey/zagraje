BLENDER ?= /Applications/Blender.app/Contents/MacOS/Blender

.PHONY: plan model render views open clean

# План этажей: out/plan.svg, out/plan.png, out/layout.json
plan:
	python3 plan.py

# 3D-модель без рендера: out/house.blend
model: plan
	$(BLENDER) -b -P blender/build_house.py

# Модель + рендеры: out/renders/*.png (около 2–3 минут)
render: plan
	$(BLENDER) -b -P blender/build_house.py -- --render

# Ракурсы для генерации картинок: out/views/*.png (около 5–8 минут)
# Один ракурс: make views ONLY=04
views: plan
	$(BLENDER) -b -P blender/build_house.py -- --views $(if $(ONLY),--only=$(ONLY),)

# Открыть папку с результатами в Finder
open:
	open out

clean:
	rm -rf out
