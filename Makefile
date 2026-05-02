# Generate a timestamp
TIMESTAMP = $(shell date +"%Y-%m-%d-%H%M%S")
organization = "wamason.com"
year = $(shell date +"%Y")
# this is the graduation month
month = "may"
name = "mason_tony"

DOCUMENT = draft-position-$(TIMESTAMP).pdf
MAIN = paper
SOURCES  = $(wildcard *.tex) $(wildcard */*.tex) $(wildcard bib/*.bib) $(wildcard *.cls)


# Use the timestamp in the new filename

$(DOCUMENT) : tidy $(SOURCES)
	make $(MAIN).pdf || rm $(MAIN).pdf
	-mv $(MAIN).pdf $(DOCUMENT)

$(MAIN).pdf : $(SOURCES)
	latexmk -lualatex -C $(MAIN).tex
	latexmk -lualatex $(MAIN).tex

tidy:
	-find . -type f \( -name "*.aux" -o -name "*.log" -o -name "*.out" -o -name "*.toc" -o -name "*.bbl" -o -name "*.blg" -o -name "*.fdb_latexmk" -o -name "*.fls" -o -name "*.synctex.gz" -o -name "*.nav" -o -name "*.snm" -o -name "*.xdv" \) -delete

clean : tidy
	-rm -f draft-position-*.pdf $(MAIN).pdf

commit : $(SOURCES)
	git commit -a -m "Automatic commit: $(TIMESTAMP)"
	git push

pull:
	git pull

all: $(DOCUMENT)
