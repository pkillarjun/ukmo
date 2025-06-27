all: help

eglc:
	clear
	mkdir -p download
	python3 eglc/main.py

format:
	yapf -ir .

help:
	@echo "Available targets:"
	@echo "  eglc           - Download EGLC METAR data"
	@echo "  format         - Format code using yapf"
	@echo "  help           - Show this help message"

.PHONY: all eglc format help
