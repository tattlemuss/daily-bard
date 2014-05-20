#!/bin/sh

mkdir -p sections/kinglear
rm sections/kinglear/*
python generate_sections.py kinglear sections/kinglear

