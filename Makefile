CURRENT_DIR := $(shell pwd)
BASENAME := $(shell basename $(CURRENT_DIR))
package=$(BASENAME)

include ../cloudmesh-common/makefile.mk
