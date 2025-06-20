all: help

format:
	yapf -ir .

help:
	@echo "Available targets:"
	@echo "  format         - Format code using yapf"
	@echo "  help           - Show this help message"

.PHONY: all format help
