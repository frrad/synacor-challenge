#!/bin/bash

GENPATH=generated

# Generate disassembled code
./disassembler.py > $GENPATH/asm.txt

# Create graphviz map
./mapper.py > $GENPATH/map.gv
# Compile
dot -Tsvg $GENPATH/map.gv > $GENPATH/map.svg
# Remove uncompiled
rm $GENPATH/map.gv
