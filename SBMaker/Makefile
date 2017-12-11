ROOT_CONFIG := $(shell root-config --cflags)
ROOT_LIBS := $(shell root-config --libs)
PROGRAM := SBMaker.cc
OUTPUT_FILE := SBMaker

standard:
	g++ $(ROOT_CONFIG)  $(PROGRAM) -o $(OUTPUT_FILE) $(ROOT_LIBS)
