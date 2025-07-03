all: help

eglc:
	clear
	mkdir -p download
	python3 eglc/main.py

metoffice:
	clear
	python3 metoffice/main.py

ignore:
	clear
	python3 data/csv_check.py

train:
	clear
	python3 model/main.py train

test:
	clear
	python3 model/main.py test

format:
	yapf -ir .

help:
	@echo "Available targets:"
	@echo "  eglc           - Download EGLC METAR data"
	@echo "  metoffice      - Download Met Office archive"
	@echo "  ignore         - Ignore bad csv files"
	@echo "  train          - Train model"
	@echo "  test          - Test model"
	@echo "  format         - Format code using yapf"
	@echo "  help           - Show this help message"

.PHONY: all eglc metoffice ignore train test format help
