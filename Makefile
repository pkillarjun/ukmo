all: help

eglc:
	clear
	mkdir -p download
	python3 eglc/main.py

metoffice:
	clear
	python3 metoffice/main.py

format:
	yapf -ir .

help:
	@echo "Available targets:"
	@echo "  eglc           - Download EGLC METAR data"
	@echo "  metoffice      - Download Met Office archive"
	@echo "  format         - Format code using yapf"
	@echo "  help           - Show this help message"

.PHONY: all eglc metoffice format help
