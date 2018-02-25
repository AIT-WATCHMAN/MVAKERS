ROOT_CONFIG := $(shell root-config --cflags)
ROOT_LIBS := $(shell root-config --libs)
PROGRAM_PAIR := SBMaker.cc
OUTPUT_PAIR_FILE := SBMaker
standard:
	g++ $(ROOT_CONFIG)  $(PROGRAM_PAIR) -o $(OUTPUT_PAIR_FILE) $(ROOT_LIBS)

