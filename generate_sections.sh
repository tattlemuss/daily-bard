#!/bin/sh
mkdir -p sections/
rm -R sections/*
   python generate_sections.py sections/${PLAY} ../oss

