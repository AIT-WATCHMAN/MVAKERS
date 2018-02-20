ROOT_CONFIG := $(shell root-config --cflags)
ROOT_LIBS := $(shell root-config --libs)
PROGRAM_PAIR := SBMaker.cc
OUTPUT_PAIR_FILE := SBMaker
PROGRAM_SINGLE := SBMaker_singles.cc
OUTPUT_SINGLE_FILE := SBMaker_singles
standard:
	g++ $(ROOT_CONFIG)  $(PROGRAM_PAIR) -o $(OUTPUT_PAIR_FILE) $(ROOT_LIBS)
	g++ $(ROOT_CONFIG)  $(PROGRAM_SINGLE) -o $(OUTPUT_SINGLE_FILE) $(ROOT_LIBS)

