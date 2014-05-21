#!/bin/sh

for PLAY in "kinglear" "12night"
do
    mkdir -p sections/${PLAY}
    rm sections/${PLAY}/*
    python generate_sections.py ${PLAY} sections/${PLAY} ../oss
done

