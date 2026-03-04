# Makefile for technical_note.tex compilation

# Main target file (without extension)
TARGET = technical_note

# LaTeX compiler
LATEX = pdflatex

# LaTeX flags
LATEXFLAGS = -interaction=nonstopmode -halt-on-error

# Source file
SOURCE = $(TARGET).tex

# Output PDF
PDF = $(TARGET).pdf

# Auxiliary files to clean
AUX_FILES = $(TARGET).aux $(TARGET).log $(TARGET).out $(TARGET).toc \
            $(TARGET).bbl $(TARGET).blg $(TARGET).nav $(TARGET).snm

.PHONY: all clean cleanall view help

# Default target: build PDF
all: $(PDF)

# Build PDF (run twice for references)
$(PDF): $(SOURCE)
	@echo "Building $(PDF)..."
	$(LATEX) $(LATEXFLAGS) $(SOURCE)
	@echo "Running second pass for references..."
	$(LATEX) $(LATEXFLAGS) $(SOURCE)
	@echo "Build complete: $(PDF)"

# Clean auxiliary files but keep PDF
clean:
	@echo "Cleaning auxiliary files..."
	rm -f $(AUX_FILES)
	@echo "Clean complete."

# Clean everything including PDF
cleanall: clean
	@echo "Removing PDF..."
	rm -f $(PDF)
	@echo "Full clean complete."

# View PDF (macOS)
view: $(PDF)
	@echo "Opening $(PDF)..."
	open $(PDF)

# Help target
help:
	@echo "Gibbs Invariant Technical Note - Build System"
	@echo ""
	@echo "Available targets:"
	@echo "  make          - Build technical_note.pdf"
	@echo "  make all      - Same as 'make'"
	@echo "  make clean    - Remove auxiliary LaTeX files"
	@echo "  make cleanall - Remove all generated files (including PDF)"
	@echo "  make view     - Open PDF in default viewer (macOS)"
	@echo "  make help     - Show this help message"
	@echo ""
	@echo "Requirements:"
	@echo "  - pdflatex (from TeX Live, MacTeX, or MiKTeX)"
	@echo ""
	@echo "First time build:"
	@echo "  cd docs && make"
	@echo ""
