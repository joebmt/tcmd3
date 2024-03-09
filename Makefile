# --- 
# Makefile - QA Makefile to create bin/tcmd binary from python bin/tcmd.py
# --- 
SHELL := /bin/bash

ls:
	@echo "make <target> where <target> is one of:"
	@echo 
	@grep '^[a-zA-Z_]*:' Makefile | sed 's/:.*//' |sed 's/^/	/'
	@echo 

cat:
	@cat Makefile

tcmd_binary:
	@echo "--- Makefile: Creating tcmd binary from tcmd.py ---"
	bin/build_tcmd.sh --binary

tcmd_python:
	@echo "--- Makefile: Creating tcmd python from tcmd.py ---"
	bin/build_tcmd.sh --python

install:
	@echo "--- Makefile: Installing python dependencies: pip install -r inc/requirements.txt ---"
	pip install -r inc/requirements.txt

buildpydoc:
	@echo "--- Makefile: Making new pydoc file ---"
	# cd bin
	bin/build_pydoc.sh
