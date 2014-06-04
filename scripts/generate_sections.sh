#!/bin/sh
mkdir -p ../sections/
rm -R ../sections/*
python ../python/generate_sections.py ../oss

