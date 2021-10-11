# Options:
# 	-W
# 		turn warnings into errors.
# 	--keep-going
# 		keep processing after the first warning, so the output has _all_ the
# 		warnings in it, not just the first.
# 	-T
# 		dump a full traceback if some exception occurs, to help debug a failure
# 		in CI.
SPHINXOPTS    ?= -W --keep-going -T
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
