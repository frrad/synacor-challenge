#!/bin/bash

GENPATH=generated

# generate disassembled code
./disassembler.py > $GENPATH/asm.txt

# create graphviz map
./mapper.py > $GENPATH/map.gv
# divide into components
ccomps $GENPATH/map.gv -x -o $GENPATH/comps.gv
# compile
for subgraph in $GENPATH/comps*.gv; do dot -Tsvg $subgraph > $subgraph.svg; done
# remove supergraph
rm $GENPATH/map.gv
# remove connected components
rm $GENPATH/comps*.gv
# rename
mv $GENPATH/comps.gv.svg $GENPATH/start.svg
mv $GENPATH/comps_1.gv.svg $GENPATH/hq.svg
mv $GENPATH/comps_2.gv.svg $GENPATH/beach.svg
