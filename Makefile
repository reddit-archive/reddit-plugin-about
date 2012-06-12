LESSC=contrib/less.js/bin/lessc

all:

.PHONY: clean
clean:
	rm -f $(LESS_OUTPUTS)

LESS_FILES := $(wildcard reddit_about/public/static/css/*.less)
LESS_OUTPUTS := $(LESS_FILES:.less=.css)

static: $(LESS_OUTPUTS)

%.css : %.less
	$(LESSC) $< $@
