#!/bin/sh
mkdir -p ../sections/
rm -R ../sections/*
mkdir -p ../public_html/
rm -R ../public_html/*
python ../python/generate_sections.py ../oss

