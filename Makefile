BLENDER ?= /Applications/Blender.app/Contents/MacOS/Blender
BOOKLET_RUNTIME ?= $(HOME)/.cache/codex-runtimes/codex-primary-runtime/dependencies
BOOKLET_PYTHON ?= $(or $(wildcard $(BOOKLET_RUNTIME)/python/bin/python3),python3)
BOOKLET_NODE ?= $(or $(wildcard $(BOOKLET_RUNTIME)/node/bin/node),node)

.PHONY: plan model render views booklet open clean

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

# Клиентский PDF из текущего плана и принятых кадров
booklet:
	NODE_PATH="$(BOOKLET_RUNTIME)/node/node_modules$${NODE_PATH:+:$$NODE_PATH}" BOOKLET_NODE="$(BOOKLET_NODE)" "$(BOOKLET_PYTHON)" booklet.py

# Открыть папку с результатами в Finder
open:
	open out

clean:
	rm -rf out
