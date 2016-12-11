#!/bin/bash

GENPATH=generated

# Generate disassembled code
./disassembler.py > $GENPATH/asm.txt

# Create graphviz map
./mapper.py > $GENPATH/map.gv
# divide into components
ccomps $GENPATH/map.gv -x -o $GENPATH/comps.gv
# Compile
for subgraph in $GENPATH/comps*.gv; do dot -Tsvg $subgraph > $subgraph.svg; done

# Remove supergraph
rm $GENPATH/map.gv
# remove connected components
rm $GENPATH/comps*.gv

mv $GENPATH/comps.gv.svg $GENPATH/start.svg
mv $GENPATH/comps_1.gv.svg $GENPATH/hq.svg
mv $GENPATH/comps_2.gv.svg $GENPATH/beach.svg
